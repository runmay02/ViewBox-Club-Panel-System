from typing import List, Optional
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.source import SourceCreate, SourceOut, SourceLinkCreate, SourceLinkOut, SourcePerformanceStats
from app.services.attribution_service import AttributionService
from app.models.source import SourceLink
from app.core.permissions import require_role
from app.models.user import RoleEnum

router = APIRouter(prefix="/sources", tags=["Acquisition Sources & Attribution"])

@router.get("", response_model=List[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    """List all dynamic acquisition sources and their real-time volume."""
    service = AttributionService(db)
    return service.list_sources()

@router.post("", response_model=SourceOut, dependencies=[Depends(require_role([RoleEnum.ADMIN.value]))])
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    """Admin creates a new dynamic acquisition source record."""
    service = AttributionService(db)
    source = service.create_source(payload)
    return SourceOut(
        id=source.id,
        name=source.name,
        channel_type=source.channel_type,
        code=source.code,
        is_active=source.is_active,
        created_at=source.created_at,
        active_links_count=0,
        total_clicks=0,
        total_signups=0
    )

@router.post("/{source_id}/links", response_model=SourceLinkOut, dependencies=[Depends(require_role([RoleEnum.ADMIN.value]))])
def generate_source_link(source_id: str, payload: SourceLinkCreate, db: Session = Depends(get_db)):
    """Admin generates a unique, cryptographically random tracking URL for a source."""
    service = AttributionService(db)
    return service.generate_source_link(source_id=source_id, target_url=payload.target_url)

@router.get("/track/{token}")
def track_source_click(token: str, request: Request, db: Session = Depends(get_db)):
    """Public click tracker: records attribution event and resolves the target acquisition source."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    service = AttributionService(db)
    source = service.track_attribution_click(token=token, ip_address=client_ip, user_agent=user_agent)
    if not source:
        return {"status": "INVALID_TOKEN", "message": "Source token not found or expired"}

    link = db.query(SourceLink).filter_by(token=token).first()
    target = link.target_url if link else "/join"
    separator = "&" if "?" in target else "?"
    return RedirectResponse(url=f"{target}{separator}source_token={token}", status_code=302)

@router.get("/analytics/performance", response_model=List[SourcePerformanceStats], dependencies=[Depends(require_role([RoleEnum.ADMIN.value, RoleEnum.OPERATIONS.value]))])
def get_source_performance(db: Session = Depends(get_db)):
    """Real-time database aggregated conversion analytics by source."""
    service = AttributionService(db)
    return service.get_source_performance()
