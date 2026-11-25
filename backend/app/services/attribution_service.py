import secrets
import re
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.source import AcquisitionSource, SourceLink, AttributionEvent
from app.models.member import MemberProfile
from app.models.referral import Referral, ReferralStageEnum
from app.schemas.source import SourceCreate, SourceOut, SourceLinkOut, SourcePerformanceStats

class AttributionService:
    def __init__(self, db: Session):
        self.db = db

    def list_sources(self) -> List[SourceOut]:
        sources = self.db.query(AcquisitionSource).order_by(AcquisitionSource.created_at.desc()).all()
        result = []
        for s in sources:
            signups = self.db.query(func.count(MemberProfile.id)).filter(MemberProfile.acquisition_source_id == s.id).scalar() or 0
            clicks = sum(link.click_count for link in s.links)
            result.append(
                SourceOut(
                    id=s.id,
                    name=s.name,
                    channel_type=s.channel_type,
                    code=s.code,
                    is_active=s.is_active,
                    created_at=s.created_at,
                    active_links_count=len(s.links),
                    total_clicks=clicks,
                    total_signups=signups,
                )
            )
        return result

    def create_source(self, payload: SourceCreate) -> AcquisitionSource:
        # Generate clean slug code if not provided
        code = payload.code
        if not code:
            code = re.sub(r"[^a-zA-Z0-9]+", "-", payload.name).strip("-").lower()

        # Check uniqueness
        existing = self.db.query(AcquisitionSource).filter(
            (AcquisitionSource.name == payload.name) | (AcquisitionSource.code == code)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Acquisition source with name '{payload.name}' or code '{code}' already exists."
            )

        source = AcquisitionSource(
            name=payload.name,
            channel_type=payload.channel_type.upper(),
            code=code,
            is_active=True
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def generate_source_link(self, source_id: str, target_url: str = "/join") -> SourceLinkOut:
        source = self.db.query(AcquisitionSource).filter(AcquisitionSource.id == source_id).first()
        if not source:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

        # Cryptographically non-guessable 16-char token
        token = f"src_{secrets.token_urlsafe(12)}"

        link = SourceLink(
            source_id=source.id,
            token=token,
            target_url=target_url,
            click_count=0
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)

        return SourceLinkOut(
            id=link.id,
            source_id=source.id,
            source_name=source.name,
            token=link.token,
            tracking_url=f"/api/v1/sources/track/{link.token}",
            click_count=link.click_count,
            created_at=link.created_at
        )

    def track_attribution_click(self, token: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Optional[AcquisitionSource]:
        link = self.db.query(SourceLink).filter(SourceLink.token == token).first()
        if not link:
            return None

        link.click_count += 1
        event = AttributionEvent(
            source_id=link.source_id,
            source_link_id=link.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(event)
        self.db.commit()
        return link.source

    def get_source_performance(self) -> List[SourcePerformanceStats]:
        sources = self.db.query(AcquisitionSource).all()
        stats = []
        for s in sources:
            signups = self.db.query(func.count(MemberProfile.id)).filter(MemberProfile.acquisition_source_id == s.id).scalar() or 0

            # Query Fit and Completed counts for members acquired via this source
            fit_count = self.db.query(func.count(Referral.id)).join(
                MemberProfile, Referral.referred_member_id == MemberProfile.id
            ).filter(
                MemberProfile.acquisition_source_id == s.id,
                Referral.stage.in_([ReferralStageEnum.FIT.value, ReferralStageEnum.COMPLETED.value])
            ).scalar() or 0

            completed_count = self.db.query(func.count(Referral.id)).join(
                MemberProfile, Referral.referred_member_id == MemberProfile.id
            ).filter(
                MemberProfile.acquisition_source_id == s.id,
                Referral.stage == ReferralStageEnum.COMPLETED.value
            ).scalar() or 0

            conv_rate = round((completed_count / signups * 100), 1) if signups > 0 else 0.0

            stats.append(
                SourcePerformanceStats(
                    source_id=s.id,
                    source_name=s.name,
                    channel_type=s.channel_type,
                    signups=signups,
                    fit_count=fit_count,
                    completed_count=completed_count,
                    conversion_rate=conv_rate
                )
            )
        return stats
