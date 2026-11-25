import json
import secrets
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.fraud import FraudFlag
from app.models.member import MemberProfile
from app.models.meta_lead import MetaLead
from app.models.source import AcquisitionSource, AttributionEvent
from app.utils.normalizer import normalize_phone

router = APIRouter(prefix="/integrations/meta", tags=["Meta Lead Ads"])


class FieldValue(BaseModel):
    name: str
    values: list[str] = Field(default_factory=list)


class MetaLeadPayload(BaseModel):
    leadgen_id: str = Field(min_length=1, max_length=64)
    form_id: str | None = Field(default=None, max_length=64)
    campaign_id: str | None = Field(default=None, max_length=64)
    ad_id: str | None = Field(default=None, max_length=64)
    created_time: datetime | None = None
    field_data: list[FieldValue] = Field(default_factory=list)


@router.post("/leads")
def ingest_meta_lead(
    payload: MetaLeadPayload,
    db: Session = Depends(get_db),
    webhook_secret: str | None = Header(default=None, alias="X-Webhook-Secret"),
):
    expected = settings.META_WEBHOOK_SECRET
    if expected and not secrets.compare_digest(webhook_secret or "", expected):
        raise HTTPException(401, "Invalid webhook secret")
    existing = db.query(MetaLead).filter_by(leadgen_id=payload.leadgen_id).first()
    if existing:
        return {"status": "DUPLICATE", "id": existing.id, "leadgen_id": existing.leadgen_id, "duplicate": True}

    fields = {item.name.strip().lower(): item.values[0].strip() for item in payload.field_data if item.values}
    full_name = fields.get("full_name") or fields.get("name")
    phone = normalize_phone(fields.get("phone_number") or fields.get("phone"))
    if not full_name or not phone:
        raise HTTPException(422, "Meta lead requires full_name and a valid phone_number")
    meta_source = db.query(AcquisitionSource).filter_by(code="meta-leadgen-ads").first()
    if not meta_source:
        meta_source = db.query(AcquisitionSource).filter_by(name="Meta Ads", is_active=True).first()
    if not meta_source:
        raise HTTPException(503, "Meta Ads acquisition source is not configured")

    member = db.query(MemberProfile).filter_by(phone=phone).first()
    lead = MetaLead(
        leadgen_id=payload.leadgen_id,
        form_id=payload.form_id,
        campaign_id=payload.campaign_id,
        ad_id=payload.ad_id,
        member_id=member.id if member else None,
        raw_payload=json.dumps(payload.model_dump(mode="json"), ensure_ascii=False),
        lead_created_time=payload.created_time,
    )
    db.add(lead)
    db.add(AttributionEvent(source_id=meta_source.id, source_link_id=None))
    if member:
        db.add(FraudFlag(member_id=member.id, flag_type="DUPLICATE_PHONE", status="PENDING_REVIEW", details=f"Meta lead {payload.leadgen_id} used a phone number already registered to member {member.member_id}."))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(MetaLead).filter_by(leadgen_id=payload.leadgen_id).first()
        if existing:
            return {"status": "DUPLICATE", "id": existing.id, "leadgen_id": existing.leadgen_id, "duplicate": True}
        raise HTTPException(409, "Meta lead could not be saved due to a duplicate record")
    db.refresh(lead)
    return {"status": "ACCEPTED", "id": lead.id, "leadgen_id": lead.leadgen_id, "source": meta_source.name, "duplicate_phone": member is not None, "duplicate": False}
