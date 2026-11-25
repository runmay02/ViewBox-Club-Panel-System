from datetime import date, timedelta
import csv
import io
import time

from app.models.fraud import FraudFlag
from app.models.member import MemberProfile
from app.models.meta_lead import MetaLead
from app.models.payout import Payout
from app.models.referral import Referral
from app.models.source import AcquisitionSource, AttributionEvent
from app.models.survey import Survey, SurveyApplication
from app.models.user import User
from app.utils.normalizer import calculate_next_eligible_date


def login(client, phone):
    response = client.post("/api/v1/auth/otp/send", json={"phone": phone})
    assert response.status_code == 200, response.text
    otp = response.json()["dev_otp"] or "123456"
    response = client.post("/api/v1/auth/otp/verify", json={"phone": phone, "otp": otp})
    assert response.status_code == 200, response.text
    return response.json()


def onboard(client, token, phone, **overrides):
    payload = {
        "full_name": "Test Respondent", "date_of_birth": "1990-04-12", "gender": "Female",
        "city": "Mumbai", "income_range": "6L-10L", "interests": ["Tech", "Travel"],
    }
    payload.update(overrides)
    response = client.post("/api/v1/members/onboarding", headers={"Authorization": f"Bearer {token}"}, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def create_survey(client, admin_token, **overrides):
    payload = {
        "title": f"Assessment {time.time_ns()}", "description": "test", "survey_url": "https://example.test/survey",
        "start_date": date.today().isoformat(), "deadline": (date.today() + timedelta(days=15)).isoformat(),
        "target_quota": 3, "max_applications": 10, "incentive_amount": 150,
    }
    payload.update(overrides)
    response = client.post("/api/v1/surveys", headers={"Authorization": f"Bearer {admin_token}"}, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_source_referral_bonus_and_phone_privacy(api):
    client, factory = api
    admin = login(client, "9999900001")["access_token"]
    ops = login(client, "9999900002")["access_token"]
    sources = client.get("/api/v1/sources").json()
    instagram = next(s for s in sources if s["name"] == "Instagram")
    link = client.post(f"/api/v1/sources/{instagram['id']}/links", headers={"Authorization": f"Bearer {admin}"}, json={"target_url": "http://testserver/join"})
    assert link.status_code == 200, link.text
    token = link.json()["token"]
    click = client.get(f"/api/v1/sources/track/{token}", headers={"user-agent": "assessment-test"})
    assert click.status_code == 302 and f"source_token={token}" in click.headers["location"]

    referrer_phone = "9876543001"
    referrer = login(client, referrer_phone)
    referrer_profile = onboard(client, referrer["access_token"], referrer_phone)
    candidate_phone = "9876543002"
    candidate = login(client, candidate_phone)
    candidate_profile = onboard(client, candidate["access_token"], candidate_phone, source_token=token, referral_code=referrer_profile["member_id"])
    with factory() as db:
        profile = db.query(MemberProfile).filter_by(id=candidate_profile["id"]).one()
        assert profile.acquisition_source.name == "Instagram"
        assert db.query(AttributionEvent).filter_by(source_id=instagram["id"]).count() == 1
        referral = db.query(Referral).filter_by(referred_member_id=profile.id).one()
        assert referral.stage == "LEAD"
        assert db.query(Payout).filter_by(referral_id=referral.id).count() == 0

    referred_rows = client.get("/api/v1/referrals/my-referrals", headers={"Authorization": f"Bearer {referrer['access_token']}"})
    assert referred_rows.status_code == 200
    assert "raw_phone" not in referred_rows.json()[0]
    assert referred_rows.json()[0]["masked_phone"] == "98XXXXXX02"

    survey = create_survey(client, admin, title="Referral completion survey")
    applied = client.post(f"/api/v1/surveys/{survey['id']}/apply", headers={"Authorization": f"Bearer {candidate['access_token']}"})
    assert applied.json()["status"] == "APPROVED"
    queue = client.get("/api/v1/referrals/operations/queue", headers={"Authorization": f"Bearer {ops}"}).json()
    ref_row = next(r for r in queue if r["candidate_id"] == candidate_profile["member_id"])
    transitioned = client.patch(f"/api/v1/referrals/operations/{ref_row['id']}/stage", headers={"Authorization": f"Bearer {ops}"}, json={"stage": "FIT"})
    assert transitioned.status_code == 200
    complete = client.post(f"/api/v1/operations/survey-applications/{applied.json()['id']}/verify-completion", headers={"Authorization": f"Bearer {ops}"})
    assert complete.status_code == 200, complete.text
    with factory() as db:
        referral = db.query(Referral).filter_by(referred_member_id=candidate_profile["id"]).one()
        assert referral.stage == "COMPLETED"
        bonus = db.query(Payout).filter_by(referral_id=referral.id).one()
        assert float(bonus.amount) == 100 and bonus.status == "PENDING_APPROVAL"


def test_strict_flexible_precedence_and_cooloff(api):
    client, factory = api
    admin = login(client, "9999900001")["access_token"]
    user = login(client, "9876543010")
    profile = onboard(client, user["access_token"], "9876543010", city="Pune", date_of_birth="1990-01-01")
    mixed = create_survey(client, admin, rules=[
        {"rule_type": "CITY", "rule_value": "Mumbai", "strictness": "FLEXIBLE"},
        {"rule_type": "AGE_MIN", "rule_value": "40", "strictness": "STRICT"},
    ])
    flexible = create_survey(client, admin, rules=[{"rule_type": "CITY", "rule_value": "Mumbai", "strictness": "FLEXIBLE"}])
    feed = {item["id"]: item for item in client.get("/api/v1/surveys", headers={"Authorization": f"Bearer {user['access_token']}"}).json()}
    assert feed[mixed["id"]]["eligibility_status"] == "REJECTED"
    assert feed[flexible["id"]]["eligibility_status"] == "WAITLISTED"
    assert client.post(f"/api/v1/surveys/{mixed['id']}/apply", headers={"Authorization": f"Bearer {user['access_token']}"}).status_code == 409

    with factory() as db:
        row = db.query(MemberProfile).filter_by(id=profile["id"]).one()
        row.last_survey_completed_on = date.today() - timedelta(days=20)
        db.commit()
    refreshed = {item["id"]: item for item in client.get("/api/v1/surveys", headers={"Authorization": f"Bearer {user['access_token']}"}).json()}
    assert refreshed[flexible["id"]]["eligibility_status"] == "REJECTED"
    assert "cool-off" in refreshed[flexible["id"]]["eligibility_reason"]
    assert calculate_next_eligible_date(date(2024, 11, 30)) == date(2025, 3, 1)


def test_start_deadline_quota_and_role_guards(api):
    client, factory = api
    admin = login(client, "9999900001")["access_token"]
    ops = login(client, "9999900002")["access_token"]
    respondent = login(client, "9876543020")
    onboard(client, respondent["access_token"], "9876543020")
    future = create_survey(client, admin, start_date=(date.today()+timedelta(days=1)).isoformat(), deadline=(date.today()+timedelta(days=15)).isoformat())
    assert all(s["id"] != future["id"] for s in client.get("/api/v1/surveys", headers={"Authorization": f"Bearer {respondent['access_token']}"}).json())
    assert client.post(f"/api/v1/surveys/{future['id']}/apply", headers={"Authorization": f"Bearer {respondent['access_token']}"}).status_code == 409
    assert client.get("/api/v1/admin/kpis", headers={"Authorization": f"Bearer {respondent['access_token']}"}).status_code == 403
    assert client.post("/api/v1/sources", headers={"Authorization": f"Bearer {ops}"}, json={"name":"Should Be Denied","channel_type":"OTHER"}).status_code == 403
    assert client.get("/api/v1/admin/kpis", headers={"Authorization": f"Bearer {admin}"}).status_code == 200
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": respondent["refresh_token"]})
    assert refreshed.status_code == 200
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refreshed.json()['access_token']}"}).status_code == 200
    preflight=client.options("/api/v1/admin/kpis",headers={"Origin":"http://127.0.0.1:5173","Access-Control-Request-Method":"GET","Access-Control-Request-Headers":"authorization"})
    assert preflight.status_code==200 and preflight.headers.get("access-control-allow-origin")=="http://127.0.0.1:5173"

    capped = create_survey(client, admin, title="At quota", target_quota=1, max_applications=2)
    with factory() as db:
        row = db.query(Survey).filter_by(id=capped["id"]).one()
        row.status = "QUOTA_REACHED"
        db.commit()
    assert client.post(f"/api/v1/surveys/{capped['id']}/apply", headers={"Authorization": f"Bearer {respondent['access_token']}"}).status_code == 409

    expired = create_survey(client, admin, title="Expired survey", start_date=(date.today()-timedelta(days=15)).isoformat(), deadline=(date.today()-timedelta(days=1)).isoformat())
    client.get("/api/v1/surveys", headers={"Authorization": f"Bearer {respondent['access_token']}"})
    with factory() as db:
        assert db.query(Survey).filter_by(id=expired["id"]).one().status == "EXPIRED"


def test_completion_closes_final_quota_slot(api):
    client, factory = api
    admin = login(client, "9999900001")["access_token"]
    ops = login(client, "9999900002")["access_token"]
    first = login(client, "9876543050")
    second = login(client, "9876543051")
    onboard(client, first["access_token"], "9876543050")
    onboard(client, second["access_token"], "9876543051")
    survey = create_survey(client, admin, title="One completion only", target_quota=1, max_applications=3)
    application = client.post(f"/api/v1/surveys/{survey['id']}/apply", headers={"Authorization": f"Bearer {first['access_token']}"}).json()
    completed = client.post(f"/api/v1/operations/survey-applications/{application['id']}/verify-completion", headers={"Authorization": f"Bearer {ops}"})
    assert completed.status_code == 200, completed.text
    assert client.post(f"/api/v1/surveys/{survey['id']}/apply", headers={"Authorization": f"Bearer {second['access_token']}"}).status_code == 409
    with factory() as db:
        row = db.query(Survey).filter_by(id=survey["id"]).one()
        assert row.completed_count == 1 and row.status == "QUOTA_REACHED"


def test_referral_fit_after_completion_queues_configured_bonus(api):
    client, factory = api
    admin = login(client, "9999900001")["access_token"]
    ops = login(client, "9999900002")["access_token"]
    referrer = login(client, "9876543060")
    referrer_profile = onboard(client, referrer["access_token"], "9876543060")
    referred = login(client, "9876543061")
    profile = onboard(client, referred["access_token"], "9876543061", referral_code=referrer_profile["member_id"])
    survey = create_survey(client, admin, title="Referral order survey", referral_bonus_amount=175)
    application = client.post(f"/api/v1/surveys/{survey['id']}/apply", headers={"Authorization": f"Bearer {referred['access_token']}"}).json()
    assert client.post(f"/api/v1/operations/survey-applications/{application['id']}/verify-completion", headers={"Authorization": f"Bearer {ops}"}).status_code == 200
    with factory() as db:
        referral = db.query(Referral).filter_by(referred_member_id=profile["id"]).one()
        referral_id = referral.id
        assert referral.stage == "LEAD"
        assert db.query(Payout).filter_by(referral_id=referral_id).count() == 0
    response = client.patch(f"/api/v1/referrals/operations/{referral_id}/stage", headers={"Authorization": f"Bearer {ops}"}, json={"stage": "FIT"})
    assert response.status_code == 200 and response.json()["stage"] == "COMPLETED"
    with factory() as db:
        bonus = db.query(Payout).filter_by(referral_id=referral_id).one()
        assert float(bonus.amount) == 175


def test_messy_csv_normalizes_and_reports_duplicates(api):
    client, factory = api
    admin=login(client,"9999900001")["access_token"]
    data=(
        "member_id,full_name,phone,email,gender,date_of_birth,city,income_range,interests,source\n"
        "VB70001,  Test Person  ,+91 98765 43030,test@example.in,M,12/04/1990,bombay,10L-20L,Auto;Tech,insta\n"
        "VB70002,Duplicate,+919876543030,,Female,1990-04-12,Mumbai,10L-20L,Tech,Instagram\n"
        "VB70003,Bad Date,9876543031,,F,31/02/1995,Pune,5 lakh,Tech,Instagram\n"
    )
    response=client.post("/api/v1/admin/imports/upload",headers={"Authorization":f"Bearer {admin}"},files={"file":("messy.csv",data,"text/csv")})
    assert response.status_code==200,response.text
    job=response.json()
    assert (job["total_rows"],job["imported_rows"],job["skipped_rows"],job["error_count"])==(3,1,1,2)
    with factory() as db:
        imported=db.query(MemberProfile).filter_by(member_id="VB70001").one()
        assert imported.phone=="9876543030" and imported.city=="Mumbai" and imported.gender=="Male"
        assert imported.income_range=="10L-20L" and imported.acquisition_source.name=="Instagram"
    report=client.get(f"/api/v1/admin/imports/{job['id']}/report",headers={"Authorization":f"Bearer {admin}"})
    assert report.status_code==200 and "Duplicate respondent" in report.text
    exported=client.get("/api/v1/admin/respondents/export?search=Test%20Person&format=xlsx",headers={"Authorization":f"Bearer {admin}"})
    assert exported.status_code==200 and exported.content[:2]==b"PK"


def test_meta_lead_idempotency_and_duplicate_phone_flag(api):
    client, factory=api
    admin=login(client,"9999900001")["access_token"]
    respondent=login(client,"9876543040")
    profile=onboard(client,respondent["access_token"],"9876543040")
    payload={"leadgen_id":"ASSESSMENT_META_001","form_id":"FORM_01","campaign_id":"CMP_01","ad_id":"AD_01","created_time":"2026-11-24T10:00:00Z","field_data":[{"name":"full_name","values":["Existing Respondent"]},{"name":"phone_number","values":["+91 98765 43040"]}]}
    first=client.post("/api/v1/integrations/meta/leads",json=payload)
    assert first.status_code==200 and first.json()["duplicate_phone"] is True
    second=client.post("/api/v1/integrations/meta/leads",json=payload)
    assert second.status_code==200 and second.json()["duplicate"] is True
    with factory() as db:
        assert db.query(MetaLead).filter_by(leadgen_id=payload["leadgen_id"]).count()==1
        assert db.query(FraudFlag).filter_by(member_id=profile["id"],flag_type="DUPLICATE_PHONE").count()==1
