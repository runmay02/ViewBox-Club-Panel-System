from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import (
    generate_mock_otp,
    get_hash,
    verify_hash,
    create_access_token,
    create_refresh_token,
)
from app.models.user import User, RoleEnum
from app.schemas.auth import OTPSendResponse, TokenResponse

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def send_otp(self, phone: str) -> OTPSendResponse:
        # Check if user exists, else create default respondent account
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user:
            user = User(
                phone=phone,
                role=RoleEnum.RESPONDENT.value,
                is_active=True
            )
            self.db.add(user)
            self.db.flush()

        otp = generate_mock_otp()
        user.hashed_otp = get_hash(otp)
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        self.db.commit()

        # In dev/test mode, return the OTP in the API response for 1-click testability
        dev_otp = otp if settings.DEBUG or settings.ENVIRONMENT in ("development", "testing") else None

        return OTPSendResponse(
            message="Verification OTP sent successfully",
            phone=phone,
            dev_otp=dev_otp
        )

    def verify_otp(self, phone: str, otp: str) -> TokenResponse:
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user or not user.hashed_otp or not user.otp_expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending OTP request found for this phone number."
            )

        # Check expiration
        now_utc = datetime.now(timezone.utc)
        expires_at = user.otp_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if now_utc > expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new verification code."
            )

        # Verify OTP hash
        if not verify_hash(otp, user.hashed_otp):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect verification OTP."
            )

        # Clear active OTP upon successful verification
        user.hashed_otp = None
        user.otp_expires_at = None
        self.db.commit()

        # Check if profile is completed
        member_id = user.profile.member_id if user.profile else None
        profile_completed = user.profile is not None

        access_token = create_access_token(
            subject=user.id,
            role=user.role,
            member_id=member_id
        )
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            role=user.role,
            member_id=member_id,
            profile_completed=profile_completed
        )
