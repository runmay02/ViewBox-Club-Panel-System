from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import OTPSendRequest, OTPSendResponse, OTPVerifyRequest, TokenResponse, UserOut
from app.services.auth_service import AuthService
from app.core.permissions import get_current_user
from app.models.user import User
from app.core.security import create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/otp/send", response_model=OTPSendResponse)
def send_otp(payload: OTPSendRequest, db: Session = Depends(get_db)):
    """Request a 6-digit mock OTP for passwordless login."""
    service = AuthService(db)
    return service.send_otp(phone=payload.phone)

@router.post("/otp/verify", response_model=TokenResponse)
def verify_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    """Verify 6-digit OTP and receive JWT access and refresh tokens."""
    service = AuthService(db)
    return service.verify_otp(phone=payload.phone, otp=payload.otp)

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Retrieve authenticated user account details."""
    return UserOut(
        id=current_user.id,
        phone=current_user.phone,
        role=current_user.role,
        is_active=current_user.is_active,
        profile_completed=current_user.profile is not None
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    claims = decode_token(payload.refresh_token)
    if not claims or claims.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.query(User).filter_by(id=claims.get("sub"), is_active=True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User is unavailable")
    member_id = user.profile.member_id if user.profile else None
    return TokenResponse(
        access_token=create_access_token(user.id, user.role, member_id),
        refresh_token=payload.refresh_token,
        role=user.role,
        member_id=member_id,
        profile_completed=user.profile is not None,
    )
