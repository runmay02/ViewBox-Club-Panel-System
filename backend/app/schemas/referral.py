from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ReferralOut(BaseModel):
    id: str
    referred_member_id: str
    referred_name: str
    masked_phone: str
    stage: str
    failure_reason: Optional[str] = None
    registered_on: str
    bonus_status: str
    bonus_amount: float = 0.0

    class Config:
        from_attributes = True

class ReferralStageUpdate(BaseModel):
    stage: str  # FIT, COMPLETED, FAILED
    failure_reason: Optional[str] = None

class ReferralQueueItemOut(BaseModel):
    id: str
    candidate_id: str
    candidate_name: str
    phone: str
    city: str
    referrer_id: str
    referrer_name: str
    registered_at: datetime
    stage: str
    failure_reason: Optional[str] = None
    survey_completed: bool = False

    class Config:
        from_attributes = True
