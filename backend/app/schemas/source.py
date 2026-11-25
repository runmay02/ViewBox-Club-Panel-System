from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SourceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    channel_type: str = Field(default="OTHER")
    code: Optional[str] = None

class SourceUpdate(BaseModel):
    name: Optional[str] = None
    channel_type: Optional[str] = None
    is_active: Optional[bool] = None

class SourceOut(BaseModel):
    id: str
    name: str
    channel_type: str
    code: str
    is_active: bool
    created_at: datetime
    active_links_count: int = 0
    total_clicks: int = 0
    total_signups: int = 0

    class Config:
        from_attributes = True

class SourceLinkCreate(BaseModel):
    target_url: str = "/join"

class SourceLinkOut(BaseModel):
    id: str
    source_id: str
    source_name: str
    token: str
    tracking_url: str
    click_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class SourcePerformanceStats(BaseModel):
    source_id: str
    source_name: str
    channel_type: str
    signups: int
    fit_count: int
    completed_count: int
    conversion_rate: float
