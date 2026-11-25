from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.api.v1.router import api_router
from app.models.source import AcquisitionSource
from app.models.user import User, RoleEnum
from app.core.security import get_hash

# Baseline seeds for demo evaluation
def seed_default_sources_and_users(db):
    default_sources = [
        {"name": "WhatsApp Group - Mumbai", "channel_type": "WHATSAPP", "code": "wa-mumbai"},
        {"name": "WhatsApp Group - Pune", "channel_type": "WHATSAPP", "code": "wa-pune"},
        {"name": "Staff DM - Agent 01", "channel_type": "STAFF", "code": "staff-agent-01"},
        {"name": "Staff DM - Agent 02", "channel_type": "STAFF", "code": "staff-agent-02"},
        {"name": "Instagram", "channel_type": "INSTAGRAM", "code": "instagram-organic"},
        {"name": "Facebook", "channel_type": "FACEBOOK", "code": "facebook-organic"},
        {"name": "Website", "channel_type": "WEBSITE", "code": "website-organic"},
        {"name": "Meta Ads", "channel_type": "META_ADS", "code": "meta-leadgen-ads"},
        {"name": "Referral", "channel_type": "REFERRAL", "code": "member-referral"},
    ]
    for s_data in default_sources:
        existing = db.query(AcquisitionSource).filter(AcquisitionSource.code == s_data["code"]).first()
        if not existing:
            db.add(AcquisitionSource(**s_data, is_active=True))

    # Seed Admin and Operations demo users if not present
    admin_user = db.query(User).filter(User.phone == "9999900001").first()
    if not admin_user:
        db.add(User(
            phone="9999900001",
            role=RoleEnum.ADMIN.value,
            hashed_otp=get_hash("123456"),
            is_active=True
        ))

    ops_user = db.query(User).filter(User.phone == "9999900002").first()
    if not ops_user:
        db.add(User(
            phone="9999900002",
            role=RoleEnum.OPERATIONS.value,
            hashed_otp=get_hash("123456"),
            is_active=True
        ))

    db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all tables exist on startup
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_sources_and_users(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Respondent Management & Survey Operations API for Concave Insights",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }
