from enum import Enum
from datetime import date, datetime, timezone
from sqlalchemy import String, Text, Date, Integer, Numeric, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class SurveyStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    QUOTA_REACHED = "QUOTA_REACHED"
    EXPIRED = "EXPIRED"
    CLOSED = "CLOSED"

class RuleStrictnessEnum(str, Enum):
    STRICT = "STRICT"
    FLEXIBLE = "FLEXIBLE"

class Survey(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "surveys"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    survey_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=SurveyStatusEnum.ACTIVE.value, index=True, nullable=False)
    target_quota: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    max_applications: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    completed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    incentive_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=250.00, nullable=False)
    referral_bonus_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=100.00, nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    rules = relationship("SurveyEligibilityRule", back_populates="survey", cascade="all, delete-orphan")
    quotas = relationship("SurveyQuota", back_populates="survey", cascade="all, delete-orphan")
    applications = relationship("SurveyApplication", back_populates="survey", cascade="all, delete-orphan")
    participations = relationship("SurveyParticipation", back_populates="survey")
    payouts = relationship("Payout", back_populates="survey")

class SurveyEligibilityRule(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "survey_eligibility_rules"

    survey_id: Mapped[str] = mapped_column(String(36), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_type: Mapped[str] = mapped_column(String(30), nullable=False)  # AGE_MIN, AGE_MAX, CITY, GENDER, INCOME_RANGE, INTEREST
    rule_value: Mapped[str] = mapped_column(String(100), nullable=False)
    strictness: Mapped[str] = mapped_column(String(10), default=RuleStrictnessEnum.STRICT.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    survey = relationship("Survey", back_populates="rules")

class SurveyQuota(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "survey_quotas"

    survey_id: Mapped[str] = mapped_column(String(36), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False, index=True)
    quota_type: Mapped[str] = mapped_column(String(30), default="TOTAL", nullable=False)  # TOTAL, CITY, GENDER
    quota_key: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. "Mumbai", "Female"
    target_count: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    survey = relationship("Survey", back_populates="quotas")

class SurveyApplication(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "survey_applications"
    __table_args__ = (UniqueConstraint("survey_id", "member_id", name="uq_survey_application_member"),)

    survey_id: Mapped[str] = mapped_column(String(36), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("member_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="APPLIED", index=True, nullable=False)  # APPLIED, APPROVED, WAITLISTED, REJECTED
    eligibility_reasons: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    survey = relationship("Survey", back_populates="applications")
    member = relationship("MemberProfile")
    participation = relationship("SurveyParticipation", back_populates="application", uselist=False)
