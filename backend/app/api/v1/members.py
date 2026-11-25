from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.member import MemberOnboardingRequest, MemberProfileOut, MemberProfileUpdate
from app.services.member_service import MemberService
from app.core.permissions import get_current_user, require_role
from app.models.user import User, RoleEnum

router = APIRouter(prefix="/members", tags=["Respondent Profiles & Onboarding"])

@router.post("/onboarding", response_model=MemberProfileOut)
def complete_onboarding(
    payload: MemberOnboardingRequest,
    current_user: User = Depends(require_role([RoleEnum.RESPONDENT.value])),
    db: Session = Depends(get_db)
):
    """Respondent completes first-time demographic onboarding."""
    service = MemberService(db)
    return service.complete_onboarding(user_id=current_user.id, payload=payload)

@router.get("/me", response_model=MemberProfileOut)
def get_my_profile(
    current_user: User = Depends(require_role([RoleEnum.RESPONDENT.value])),
    db: Session = Depends(get_db)
):
    """Retrieve logged-in respondent's profile, cool-off date, and referral link."""
    if not current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete onboarding first."
        )

    service = MemberService(db)
    return service.get_profile_out(current_user.profile)

@router.patch("/me", response_model=MemberProfileOut)
def update_my_profile(
    payload: MemberProfileUpdate,
    current_user: User = Depends(require_role([RoleEnum.RESPONDENT.value])),
    db: Session = Depends(get_db)
):
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Complete onboarding before editing your profile")
    return MemberService(db).update_profile(current_user.profile, payload)
