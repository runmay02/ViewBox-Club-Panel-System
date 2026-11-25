from datetime import date
from sqlalchemy import String, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class MemberProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "member_profiles"

    member_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    city: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    income_range: Mapped[str] = mapped_column(String(50), nullable=False)
    interests: Mapped[str] = mapped_column(Text, nullable=False, default="")
    acquisition_source_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("acquisition_sources.id", ondelete="SET NULL"), nullable=True)
    joined_on: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    last_survey_completed_on: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    user = relationship("User", back_populates="profile")
    acquisition_source = relationship("AcquisitionSource", back_populates="members")
    referrals_made = relationship("Referral", foreign_keys="Referral.referrer_member_id", back_populates="referrer")
    referral_received = relationship("Referral", foreign_keys="Referral.referred_member_id", back_populates="referred", uselist=False)
