from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDPrimaryKeyMixin

class FraudFlag(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "fraud_flags"

    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("member_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    flag_type: Mapped[str] = mapped_column(String(40), nullable=False)  # DUPLICATE_PHONE, SELF_REFERRAL, REFERRAL_RING, VELOCITY_BURST
    status: Mapped[str] = mapped_column(String(20), default="PENDING_REVIEW", index=True, nullable=False)  # PENDING_REVIEW, CONFIRMED_FRAUD, DISMISSED
    details: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    member = relationship("MemberProfile")
