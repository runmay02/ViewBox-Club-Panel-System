from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDPrimaryKeyMixin

class AcquisitionSource(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "acquisition_sources"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    channel_type: Mapped[str] = mapped_column(String(30), nullable=False, default="OTHER")
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    links = relationship("SourceLink", back_populates="source", cascade="all, delete-orphan")
    attribution_events = relationship("AttributionEvent", back_populates="source")
    members = relationship("MemberProfile", back_populates="acquisition_source")

class SourceLink(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "source_links"

    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("acquisition_sources.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    target_url: Mapped[str] = mapped_column(String(255), nullable=False, default="/join")
    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    source = relationship("AcquisitionSource", back_populates="links")
    attribution_events = relationship("AttributionEvent", back_populates="source_link")

class AttributionEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "attribution_events"

    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("acquisition_sources.id", ondelete="CASCADE"), nullable=False)
    source_link_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("source_links.id", ondelete="SET NULL"), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    source = relationship("AcquisitionSource", back_populates="attribution_events")
    source_link = relationship("SourceLink", back_populates="attribution_events")
