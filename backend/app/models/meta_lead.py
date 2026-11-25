from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDPrimaryKeyMixin

class MetaLead(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "meta_leads"

    leadgen_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    form_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ad_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    member_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("member_profiles.id", ondelete="SET NULL"), nullable=True)
    raw_payload: Mapped[str] = mapped_column(Text, nullable=False)
    lead_created_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    member = relationship("MemberProfile")
