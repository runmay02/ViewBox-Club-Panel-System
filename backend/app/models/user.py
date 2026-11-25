from enum import Enum
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin

class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    OPERATIONS = "OPERATIONS"
    RESPONDENT = "RESPONDENT"

class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    phone: Mapped[str] = mapped_column(String(15), unique=True, index=True, nullable=False)
    hashed_otp: Mapped[str | None] = mapped_column(String(255), nullable=True)
    otp_expires_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    role: Mapped[str] = mapped_column(String(20), default=RoleEnum.RESPONDENT.value, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 1-to-1 relationship with MemberProfile
    profile = relationship("MemberProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
