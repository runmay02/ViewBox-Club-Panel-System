from datetime import date, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.permissions import get_current_user, require_role
from app.database.session import get_db
from app.models.member import MemberProfile
from app.models.participation import SurveyParticipation
from app.models.survey import Survey, SurveyApplication, SurveyEligibilityRule, SurveyQuota
from app.models.user import RoleEnum, User
from app.utils.normalizer import calculate_age, calculate_next_eligible_date

router = APIRouter(prefix="/surveys", tags=["Surveys"])


class RuleInput(BaseModel):
    rule_type: Literal["AGE_MIN", "AGE_MAX", "CITY", "GENDER", "INCOME_RANGE", "INTEREST"]
    rule_value: str = Field(min_length=1, max_length=100)
    strictness: Literal["STRICT", "FLEXIBLE"] = "STRICT"


class SurveyCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = ""
    survey_url: str = ""
    start_date: date
    deadline: date
    status: Literal["DRAFT", "ACTIVE"] = "ACTIVE"
    target_quota: int = Field(default=50, ge=1)
    max_applications: int = Field(default=60, ge=1)
    incentive_amount: float = Field(default=250, ge=0)
    referral_bonus_amount: float = Field(default=100, ge=0)
    rules: list[RuleInput] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_lifecycle(self):
        if self.deadline < self.start_date or self.deadline > self.start_date + timedelta(days=15):
            raise ValueError("Deadline must be between start date and 15 days after start date")
        if self.max_applications < self.target_quota:
            raise ValueError("Application limit cannot be lower than target quota")
        return self


def _quota_exhausted(survey: Survey, member: MemberProfile | None, db: Session) -> str | None:
    completed = db.query(func.count(SurveyParticipation.id)).filter_by(survey_id=survey.id, status="COMPLETED").scalar() or 0
    if completed >= survey.target_quota:
        return "Survey quota is full"
    for quota in db.query(SurveyQuota).filter_by(survey_id=survey.id).all():
        query = db.query(func.count(SurveyParticipation.id)).join(
            MemberProfile, SurveyParticipation.member_id == MemberProfile.id
        ).filter(SurveyParticipation.survey_id == survey.id, SurveyParticipation.status == "COMPLETED")
        if quota.quota_type == "TOTAL":
            used = completed
        elif quota.quota_type == "CITY" and quota.quota_key:
            used = query.filter(MemberProfile.city == quota.quota_key).scalar() or 0
        elif quota.quota_type == "GENDER" and quota.quota_key:
            used = query.filter(MemberProfile.gender == quota.quota_key).scalar() or 0
        else:
            continue
        if used >= quota.target_count and (quota.quota_type == "TOTAL" or member is None or (quota.quota_type == "CITY" and member.city == quota.quota_key) or (quota.quota_type == "GENDER" and member.gender == quota.quota_key)):
            return f"{quota.quota_type.title()} quota is full"
    return None


def evaluate_eligibility(survey: Survey, member: MemberProfile | None, db: Session) -> tuple[str, str]:
    today = date.today()
    if survey.status != "ACTIVE":
        return "REJECTED", f"Survey is {survey.status.lower()}"
    if today < survey.start_date:
        return "REJECTED", f"Survey opens on {survey.start_date.isoformat()}"
    if today > survey.deadline:
        return "REJECTED", f"Survey closed on {survey.deadline.isoformat()}"
    quota_reason = _quota_exhausted(survey, member, db)
    if quota_reason:
        return "REJECTED", quota_reason
    if member is None:
        return "APPROVED", "Survey available"
    cooldown = calculate_next_eligible_date(member.last_survey_completed_on) if member.last_survey_completed_on else None
    if cooldown and today < cooldown:
        return "REJECTED", f"Survey cool-off active until {cooldown.isoformat()}"

    age = calculate_age(member.date_of_birth)
    interests = set((member.interests or "").split(";"))
    mismatches: list[tuple[str, str]] = []
    for rule in survey.rules:
        value = rule.rule_value.strip()
        if rule.rule_type == "AGE_MIN":
            matches = age >= int(value)
        elif rule.rule_type == "AGE_MAX":
            matches = age <= int(value)
        elif rule.rule_type == "CITY":
            matches = member.city.casefold() == value.casefold()
        elif rule.rule_type == "GENDER":
            matches = member.gender.casefold() == value.casefold()
        elif rule.rule_type == "INCOME_RANGE":
            matches = member.income_range.casefold() == value.casefold()
        elif rule.rule_type == "INTEREST":
            matches = any(item.casefold() == value.casefold() for item in interests)
        else:
            continue
        if not matches:
            mismatches.append((rule.rule_type, rule.strictness))
    strict_failures = sorted({rule for rule, strictness in mismatches if strictness == "STRICT"})
    if strict_failures:
        return "REJECTED", "Does not meet strict criteria: " + ", ".join(strict_failures)
    flexible_failures = sorted({rule for rule, strictness in mismatches if strictness == "FLEXIBLE"})
    if flexible_failures:
        return "WAITLISTED", "Does not meet flexible criteria: " + ", ".join(flexible_failures)
    return "APPROVED", "Meets all eligibility criteria"


def serialize(survey: Survey, member: MemberProfile | None = None, db: Session | None = None):
    rules = {"age_min": None, "age_max": None, "cities": [], "genders": [], "income_ranges": [], "interests": [], "strictness": "STRICT"}
    strictnesses = {rule.strictness for rule in survey.rules}
    if len(strictnesses) > 1:
        rules["strictness"] = "MIXED"
    elif strictnesses:
        rules["strictness"] = next(iter(strictnesses))
    mapping = {"CITY": "cities", "GENDER": "genders", "INCOME_RANGE": "income_ranges", "INTEREST": "interests"}
    for rule in survey.rules:
        if rule.rule_type in ("AGE_MIN", "AGE_MAX"):
            rules[rule.rule_type.lower()] = int(rule.rule_value)
        elif rule.rule_type in mapping:
            rules[mapping[rule.rule_type]].append(rule.rule_value)
    status, reason = evaluate_eligibility(survey, member, db) if db is not None else ("APPROVED", "Survey details")
    application = db.query(SurveyApplication).filter_by(survey_id=survey.id, member_id=member.id).first() if db is not None and member is not None else None
    if application:
        status, reason = application.status, application.eligibility_reasons or reason
    return {
        "id": survey.id, "title": survey.title, "description": survey.description,
        "survey_url": survey.survey_url, "category": "Research", "start_date": survey.start_date,
        "deadline": survey.deadline, "days_left": max(0, (survey.deadline - date.today()).days),
        "status": survey.status, "target_quota": survey.target_quota,
        "completed_count": survey.completed_count, "incentive_amount": float(survey.incentive_amount),
        "referral_bonus_amount": float(survey.referral_bonus_amount), "rules": rules,
        "eligibility_status": status, "eligibility_reason": reason,
        "application_id": application.id if application else None,
    }


@router.get("")
def list_surveys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in (RoleEnum.RESPONDENT.value, RoleEnum.ADMIN.value):
        raise HTTPException(403, "Survey feed is not available to this role")
    # Persist lifecycle expiry as users load the feed, so stale ACTIVE records
    # cannot remain eligible in other operations.
    db.query(Survey).filter(Survey.status == "ACTIVE", Survey.deadline < date.today()).update(
        {Survey.status: "EXPIRED"}, synchronize_session=False
    )
    db.commit()
    query = db.query(Survey)
    if current_user.role != RoleEnum.ADMIN.value:
        query = query.filter(Survey.status == "ACTIVE", Survey.deadline >= date.today(), Survey.start_date <= date.today())
    surveys = query.order_by(Survey.deadline).all()
    return [serialize(survey, current_user.profile, db) for survey in surveys]


@router.post("")
def create_survey(payload: SurveyCreate, current_user: User = Depends(require_role([RoleEnum.ADMIN.value])), db: Session = Depends(get_db)):
    survey = Survey(
        title=payload.title, description=payload.description, survey_url=payload.survey_url,
        start_date=payload.start_date, deadline=payload.deadline, status=payload.status,
        target_quota=payload.target_quota, max_applications=payload.max_applications,
        incentive_amount=payload.incentive_amount, referral_bonus_amount=payload.referral_bonus_amount,
        created_by_user_id=current_user.id,
    )
    survey.rules = [SurveyEligibilityRule(rule_type=rule.rule_type, rule_value=rule.rule_value, strictness=rule.strictness) for rule in payload.rules]
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return serialize(survey, db=db)


@router.post("/{survey_id}/apply")
def apply_survey(survey_id: str, current_user: User = Depends(require_role([RoleEnum.RESPONDENT.value])), db: Session = Depends(get_db)):
    member = current_user.profile
    if not member:
        raise HTTPException(400, "Complete your profile before applying")
    # Acquire the survey row's write lock before checking limits. This serializes
    # submissions for a survey on both PostgreSQL and SQLite.
    locked = db.execute(update(Survey).where(Survey.id == survey_id).values(max_applications=Survey.max_applications)).rowcount
    if not locked:
        db.rollback()
        raise HTTPException(404, "Survey not found")
    survey = db.query(Survey).filter_by(id=survey_id).first()
    existing = db.query(SurveyApplication).filter_by(survey_id=survey.id, member_id=member.id).first()
    if existing:
        db.rollback()
        raise HTTPException(409, "You have already applied to this survey")
    status, reason = evaluate_eligibility(survey, member, db)
    if status not in ("APPROVED", "WAITLISTED"):
        db.rollback()
        raise HTTPException(409, reason)
    used = db.query(func.count(SurveyApplication.id)).filter_by(survey_id=survey.id).scalar() or 0
    if used >= survey.max_applications:
        db.rollback()
        raise HTTPException(409, "Application quota is full")
    application = SurveyApplication(survey_id=survey.id, member_id=member.id, status=status, eligibility_reasons=reason)
    db.add(application)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "You have already applied to this survey")
    db.refresh(application)
    return {"id": application.id, "survey_id": survey.id, "status": application.status,
            "eligibility_reason": application.eligibility_reasons,
            "survey_url": survey.survey_url if application.status == "APPROVED" else None}
