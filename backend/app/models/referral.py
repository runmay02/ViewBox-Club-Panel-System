from enum import Enum
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class ReferralStageEnum(str, Enum):
    LEAD = "LEAD"
    FIT = "FIT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Referral(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "referrals"
    __table_args__ = (
        CheckConstraint("referrer_member_id <> referred_member_id", name="check_no_self_referral"),
    )

    referrer_member_id: Mapped[str] = mapped_column(String(36), ForeignKey("member_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    referred_member_id: Mapped[str] = mapped_column(String(36), ForeignKey("member_profiles.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    referral_token: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    stage: Mapped[str] = mapped_column(String(20), default=ReferralStageEnum.LEAD.value, index=True, nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    fit_verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completion_verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    referrer = relationship("MemberProfile", foreign_keys=[referrer_member_id], back_populates="referrals_made")
    referred = relationship("MemberProfile", foreign_keys=[referred_member_id], back_populates="referral_received")
    payout = relationship("Payout", back_populates="referral", uselist=False)
