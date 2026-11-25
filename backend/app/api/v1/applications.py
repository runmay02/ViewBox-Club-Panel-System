from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.permissions import require_role
from app.models.user import RoleEnum, User
from app.models.survey import SurveyApplication, SurveyQuota
from app.models.survey import Survey
from app.models.member import MemberProfile
from app.models.participation import SurveyParticipation
from app.models.payout import Payout
from app.models.referral import Referral

router=APIRouter(prefix="/operations/survey-applications",tags=["Survey Applications"])
roles=[RoleEnum.ADMIN.value,RoleEnum.OPERATIONS.value]

class ApplicationReview(BaseModel):
    status: str
    reason: str | None = Field(default=None, max_length=500)

@router.get("")
def list_applications(db:Session=Depends(get_db), user:User=Depends(require_role(roles))):
    rows=db.query(SurveyApplication).order_by(SurveyApplication.applied_at.desc()).all()
    return [{"id":a.id,"survey_id":a.survey_id,"survey_title":a.survey.title,"member_id":a.member.member_id,"member_name":a.member.full_name,"city":a.member.city,"status":a.status,"eligibility_reasons":a.eligibility_reasons,"applied_at":a.applied_at,"completed":bool(a.participation)} for a in rows]

@router.post("/{application_id}/verify-completion")
def verify_completion(application_id:str, db:Session=Depends(get_db), user:User=Depends(require_role(roles))):
    application=db.query(SurveyApplication).filter_by(id=application_id).first()
    if not application: raise HTTPException(404,"Survey application not found")
    if application.status!="APPROVED": raise HTTPException(409,"Only approved survey applications can be completed")
    if db.query(SurveyParticipation).filter_by(application_id=application.id).first(): raise HTTPException(409,"Survey completion already verified")
    survey=application.survey; member=application.member
    if survey.status!="ACTIVE" or survey.start_date > date.today() or survey.deadline < date.today(): raise HTTPException(409,"Survey is not currently active")
    from sqlalchemy import update, func
    locked=db.execute(update(Survey).where(Survey.id==survey.id,Survey.status=="ACTIVE",Survey.start_date<=date.today(),Survey.deadline>=date.today(),Survey.completed_count<Survey.target_quota).values(completed_count=Survey.completed_count+1)).rowcount
    if not locked:
        db.rollback()
        raise HTTPException(409,"Survey quota is full or the survey is closed")
    db.refresh(survey, attribute_names=["completed_count"])
    for quota in db.query(SurveyQuota).filter_by(survey_id=survey.id).all():
        if quota.quota_type not in ("TOTAL", "CITY", "GENDER"):
            continue
        count_query=db.query(func.count(SurveyParticipation.id)).join(MemberProfile, SurveyParticipation.member_id==MemberProfile.id).filter(SurveyParticipation.survey_id==survey.id,SurveyParticipation.status=="COMPLETED")
        if quota.quota_type=="CITY" and quota.quota_key: count_query=count_query.filter(MemberProfile.city==quota.quota_key)
        if quota.quota_type=="GENDER" and quota.quota_key: count_query=count_query.filter(MemberProfile.gender==quota.quota_key)
        if quota.quota_type!="TOTAL" and quota.quota_key not in (member.city,member.gender): continue
        if (count_query.scalar() or 0)>=quota.target_count:
            db.rollback();raise HTTPException(409,f"{quota.quota_type.title()} quota is full")
    now=datetime.now(timezone.utc)
    db.add(SurveyParticipation(survey_id=survey.id,member_id=member.id,application_id=application.id,status="COMPLETED",verified_by_user_id=user.id,verified_at=now))
    member.last_survey_completed_on=date.today()
    for quota in db.query(SurveyQuota).filter_by(survey_id=survey.id).all():
        if quota.quota_type == "TOTAL" or (quota.quota_type == "CITY" and quota.quota_key == member.city) or (quota.quota_type == "GENDER" and quota.quota_key == member.gender):
            quota.completed_count += 1
    db.add(Payout(member_id=member.id,survey_id=survey.id,payout_type="SURVEY_COMPLETION",amount=survey.incentive_amount,status="PENDING_APPROVAL"))
    referral=db.query(Referral).filter_by(referred_member_id=member.id,stage="FIT").first()
    if referral:
        referral.stage="COMPLETED";referral.completion_verified_at=now
        if not referral.payout:
            db.add(Payout(member_id=referral.referrer_member_id,referral_id=referral.id,payout_type="REFERRAL_BONUS",amount=survey.referral_bonus_amount,status="PENDING_APPROVAL"))
    if survey.completed_count>=survey.target_quota:
        survey.status="QUOTA_REACHED"
    db.commit()
    return {"application_id":application.id,"status":"COMPLETED","verified_at":now,"payout_status":"PENDING_APPROVAL","referral_completed":bool(referral)}

@router.patch("/{application_id}/review")
def review_application(application_id:str, payload:ApplicationReview, db:Session=Depends(get_db), user:User=Depends(require_role(roles))):
    application=db.query(SurveyApplication).filter_by(id=application_id).first()
    if not application: raise HTTPException(404,"Survey application not found")
    if application.status not in ("WAITLISTED","APPLIED") or payload.status not in ("APPROVED","REJECTED"):
        raise HTTPException(409,"Only pending or waitlisted applications can be reviewed")
    application.status=payload.status
    application.eligibility_reasons=payload.reason or ("Approved by operations" if payload.status=="APPROVED" else "Rejected by operations")
    db.commit()
    return {"id":application.id,"status":application.status,"eligibility_reasons":application.eligibility_reasons}
