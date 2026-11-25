from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.permissions import require_role
from app.models.user import RoleEnum, User
from app.models.payout import Payout

router=APIRouter(prefix="/operations/payouts",tags=["Payouts"])

@router.get("")
def list_payouts(db:Session=Depends(get_db), user:User=Depends(require_role([RoleEnum.ADMIN.value,RoleEnum.OPERATIONS.value]))):
    rows=db.query(Payout).order_by(Payout.created_at.desc()).all()
    return [{"id":p.id,"member_id":p.member.member_id,"member_name":p.member.full_name,"type":p.payout_type,"amount":float(p.amount),"status":p.status,"survey_title":p.survey.title if p.survey else None,"referral_name":p.referral.referred.full_name if p.referral and p.referral.referred else None,"created_at":p.created_at} for p in rows]

@router.post("/{payout_id}/approve")
def approve_payout(payout_id:str, db:Session=Depends(get_db), user:User=Depends(require_role([RoleEnum.ADMIN.value,RoleEnum.OPERATIONS.value]))):
    p=db.query(Payout).filter_by(id=payout_id).with_for_update().first()
    if not p: raise HTTPException(404,"Payout not found")
    if p.status!="PENDING_APPROVAL": raise HTTPException(409,f"Payout is already {p.status}")
    p.status="APPROVED"; p.approved_by_user_id=user.id; p.approved_at=datetime.now(timezone.utc); db.commit()
    return {"id":p.id,"status":p.status,"approved_at":p.approved_at}
