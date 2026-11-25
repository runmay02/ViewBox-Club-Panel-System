from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.referral import ReferralOut, ReferralQueueItemOut, ReferralStageUpdate
from app.services.referral_service import ReferralService
from app.core.permissions import get_current_user, require_role
from app.models.user import User, RoleEnum

router = APIRouter(prefix="/referrals", tags=["Referral Operations & Tracking"])

@router.get("/my-referrals", response_model=List[ReferralOut])
def get_my_referrals(current_user: User = Depends(require_role([RoleEnum.RESPONDENT.value])), db: Session = Depends(get_db)):
    """Respondent retrieves referred friends with phone numbers strictly masked (98XXXXXX21)."""
    if not current_user.profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Respondent profile not completed yet.")

    service = ReferralService(db)
    return service.get_my_referrals(member_profile_id=current_user.profile.id)

@router.get("/operations/queue", response_model=List[ReferralQueueItemOut], dependencies=[Depends(require_role([RoleEnum.OPERATIONS.value, RoleEnum.ADMIN.value]))])
def get_referral_triage_queue(db: Session = Depends(get_db)):
    """Operations queue of pending respondent suitability and survey completion verifications."""
    service = ReferralService(db)
    return service.get_operations_queue()

@router.patch("/operations/{referral_id}/stage", dependencies=[Depends(require_role([RoleEnum.OPERATIONS.value, RoleEnum.ADMIN.value]))])
def update_referral_stage(
    referral_id: str,
    payload: ReferralStageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Operations changes referral stage (Lead -> Fit, Lead -> Failed, Fit -> Completed, Fit -> Failed)."""
    service = ReferralService(db)
    referral = service.update_referral_stage(
        referral_id=referral_id,
        new_stage=payload.stage.upper(),
        failure_reason=payload.failure_reason,
        ops_user_id=current_user.id
    )
    return {
        "status": "SUCCESS",
        "referral_id": referral.id,
        "stage": referral.stage,
        "failure_reason": referral.failure_reason,
        "message": f"Referral stage transitioned to {referral.stage}."
    }
