from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDPrimaryKeyMixin

class SurveyParticipation(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "survey_participations"

    survey_id: Mapped[str] = mapped_column(String(36), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("member_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("survey_applications.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="COMPLETED", index=True, nullable=False)  # COMPLETED, REJECTED
    quality_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    verified_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    survey = relationship("Survey", back_populates="participations")
    member = relationship("MemberProfile")
    application = relationship("SurveyApplication", back_populates="participation")
