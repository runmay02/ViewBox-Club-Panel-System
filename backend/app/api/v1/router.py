from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.sources import router as sources_router
from app.api.v1.referrals import router as referrals_router
from app.api.v1.members import router as members_router
from app.api.v1.surveys import router as surveys_router
from app.api.v1.admin import router as admin_router
from app.api.v1.payouts import router as payouts_router
from app.api.v1.imports import router as imports_router
from app.api.v1.applications import router as applications_router
from app.api.v1.meta_leads import router as meta_leads_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(sources_router)
api_router.include_router(referrals_router)
api_router.include_router(members_router)
api_router.include_router(surveys_router)
api_router.include_router(admin_router)
api_router.include_router(payouts_router)
api_router.include_router(imports_router)
api_router.include_router(applications_router)
api_router.include_router(meta_leads_router)
