import re
from typing import Optional
from pydantic import BaseModel, field_validator
from app.utils.normalizer import normalize_phone

class OTPSendRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = normalize_phone(v)
        if not clean:
            raise ValueError("Invalid Indian mobile number. Must be 10 digits starting with 6, 7, 8, or 9.")
        return clean

class OTPSendResponse(BaseModel):
    message: str
    phone: str
    dev_otp: Optional[str] = None  # Mock OTP returned in development mode

class OTPVerifyRequest(BaseModel):
    phone: str
    otp: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = normalize_phone(v)
        if not clean:
            raise ValueError("Invalid Indian mobile number.")
        return clean

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    member_id: Optional[str] = None
    profile_completed: bool = False

class UserOut(BaseModel):
    id: str
    phone: str
    role: str
    is_active: bool
    profile_completed: bool = False

    class Config:
        from_attributes = True
