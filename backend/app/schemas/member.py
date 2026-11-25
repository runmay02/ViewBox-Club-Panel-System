from typing import List, Optional
from datetime import date
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from app.utils.normalizer import normalize_city, normalize_gender

class MemberOnboardingRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    gender: str
    city: str
    income_range: str
    interests: List[str] = Field(default_factory=list)
    email: Optional[str] = None
    source_token: Optional[str] = None
    source_id: Optional[str] = None
    referral_code: Optional[str] = None

    @model_validator(mode="after")
    def validate_date_of_birth(self):
        from datetime import date as date_type
        from app.utils.normalizer import calculate_age
        if self.date_of_birth > date_type.today() or calculate_age(self.date_of_birth) < 13:
            raise ValueError("Respondents must be at least 13 years old")
        return self

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        return normalize_gender(v) or "Other"

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        return normalize_city(v) or v.strip().title()

class MemberProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    city: Optional[str] = None
    income_range: Optional[str] = None
    interests: Optional[List[str]] = None
    email: Optional[str] = None

class MemberProfileOut(BaseModel):
    id: str
    member_id: str
    full_name: str
    phone: str
    email: Optional[str] = None
    gender: str
    date_of_birth: date
    age: int
    city: str
    income_range: str
    interests: List[str]
    acquisition_source: Optional[str] = None
    referral_token: Optional[str] = None
    referral_link: Optional[str] = None
    joined_on: date
    last_survey_completed_on: Optional[date] = None
    cool_off_until: Optional[date] = None
    total_earned: float = 0.0

    class Config:
        from_attributes = True
