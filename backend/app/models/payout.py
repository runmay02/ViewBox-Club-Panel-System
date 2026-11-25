from datetime import datetime
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class Payout(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payouts"
    __table_args__ = (
        CheckConstraint(
            "(payout_type = 'SURVEY_COMPLETION' AND survey_id IS NOT NULL AND referral_id IS NULL) OR "
            "(payout_type = 'REFERRAL_BONUS' AND referral_id IS NOT NULL AND survey_id IS NULL)",
            name="check_payout_mutual_exclusivity"
        ),
    )

    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("member_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    survey_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("surveys.id", ondelete="SET NULL"), nullable=True)
    referral_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("referrals.id", ondelete="SET NULL"), nullable=True)
    payout_type: Mapped[str] = mapped_column(String(30), nullable=False)  # SURVEY_COMPLETION, REFERRAL_BONUS
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING_APPROVAL", index=True, nullable=False)  # PENDING_APPROVAL, APPROVED, PROCESSING, PAID, FAILED
    approved_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    payment_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    member = relationship("MemberProfile")
    survey = relationship("Survey", back_populates="payouts")
    referral = relationship("Referral", back_populates="payout")
