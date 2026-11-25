from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.referral import Referral, ReferralStageEnum
from app.models.member import MemberProfile
from app.models.payout import Payout
from app.models.participation import SurveyParticipation
from app.schemas.referral import ReferralOut, ReferralQueueItemOut
from app.utils.normalizer import mask_phone

class ReferralService:
    def __init__(self, db: Session):
        self.db = db

    def create_referral_link(self, referrer_id: str, referred_id: str, referral_token: str) -> Referral:
        # Enforce check: no self-referral
        if referrer_id == referred_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Self-referral is strictly prohibited."
            )

        # Check duplicate referral
        existing = self.db.query(Referral).filter(Referral.referred_member_id == referred_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This member has already been referred."
            )

        referral = Referral(
            referrer_member_id=referrer_id,
            referred_member_id=referred_id,
            referral_token=referral_token,
            stage=ReferralStageEnum.LEAD.value,
        )
        self.db.add(referral)
        self.db.commit()
        self.db.refresh(referral)
        return referral

    def get_my_referrals(self, member_profile_id: str) -> List[ReferralOut]:
        referrals = (
            self.db.query(Referral)
            .filter(Referral.referrer_member_id == member_profile_id)
            .order_by(Referral.created_at.desc())
            .all()
        )

        output: List[ReferralOut] = []
        for r in referrals:
            bonus_status = "PENDING_FIT"
            bonus_amount = 0.0
            if r.stage == ReferralStageEnum.COMPLETED.value:
                bonus_status = "EARNED"
                bonus_amount = 100.0
            elif r.stage == ReferralStageEnum.FIT.value:
                bonus_status = "PENDING_COMPLETION"
            elif r.stage == ReferralStageEnum.FAILED.value:
                bonus_status = "INELIGIBLE"

            output.append(
                ReferralOut(
                    id=r.id,
                    referred_member_id=r.referred.member_id if r.referred else "N/A",
                    referred_name=r.referred.full_name if r.referred else "Member",
                    masked_phone=mask_phone(r.referred.phone if r.referred else ""),
                    stage=r.stage,
                    failure_reason=r.failure_reason,
                    registered_on=r.created_at.strftime("%Y-%m-%d"),
                    bonus_status=bonus_status,
                    bonus_amount=bonus_amount,
                )
            )
        return output

    def get_operations_queue(self) -> List[ReferralQueueItemOut]:
        referrals = (
            self.db.query(Referral)
            .filter(Referral.stage.in_([ReferralStageEnum.LEAD.value, ReferralStageEnum.FIT.value]))
            .order_by(Referral.created_at.desc())
            .all()
        )

        items = []
        for r in referrals:
            items.append(
                ReferralQueueItemOut(
                    id=r.id,
                    candidate_id=r.referred.member_id if r.referred else "N/A",
                    candidate_name=r.referred.full_name if r.referred else "Candidate",
                    phone=r.referred.phone if r.referred else "",
                    city=r.referred.city if r.referred else "",
                    referrer_id=r.referrer.member_id if r.referrer else "N/A",
                    referrer_name=r.referrer.full_name if r.referrer else "Referrer",
                    registered_at=r.created_at,
                    stage=r.stage,
                    failure_reason=r.failure_reason,
                    survey_completed=r.referred.last_survey_completed_on is not None if r.referred else False
                )
            )
        return items

    def update_referral_stage(self, referral_id: str, new_stage: str, failure_reason: Optional[str] = None, ops_user_id: Optional[str] = None) -> Referral:
        referral = self.db.query(Referral).filter(Referral.id == referral_id).first()
        if not referral:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referral record not found")

        current = referral.stage
        valid_transitions = {
            ReferralStageEnum.LEAD.value: [ReferralStageEnum.FIT.value, ReferralStageEnum.FAILED.value],
            ReferralStageEnum.FIT.value: [ReferralStageEnum.COMPLETED.value, ReferralStageEnum.FAILED.value],
        }

        if current not in valid_transitions or new_stage not in valid_transitions[current]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stage transition from {current} to {new_stage}."
            )

        if new_stage == ReferralStageEnum.FAILED.value and not failure_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A failure reason is mandatory when disqualifying a referral."
            )

        if new_stage == ReferralStageEnum.COMPLETED.value and not referral.referred.last_survey_completed_on:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A verified survey completion is required before completing a referral."
            )

        now = datetime.now(timezone.utc)
        referral.stage = new_stage

        if new_stage == ReferralStageEnum.FIT.value:
            referral.fit_verified_at = now
            # If the referred member completed a survey before operations
            # verified FIT, finish the bonus lifecycle now.
            participation = (
                self.db.query(SurveyParticipation)
                .filter_by(member_id=referral.referred_member_id, status="COMPLETED")
                .order_by(SurveyParticipation.verified_at.desc())
                .first()
            )
            if participation:
                referral.stage = ReferralStageEnum.COMPLETED.value
                referral.completion_verified_at = participation.verified_at or now
                if not referral.payout:
                    self.db.add(Payout(
                        member_id=referral.referrer_member_id,
                        referral_id=referral.id,
                        payout_type="REFERRAL_BONUS",
                        amount=participation.survey.referral_bonus_amount,
                        status="PENDING_APPROVAL",
                    ))
        elif new_stage == ReferralStageEnum.COMPLETED.value:
            referral.completion_verified_at = now
            # Automatically queue referral bonus payout for the referring member!
            payout = Payout(
                member_id=referral.referrer_member_id,
                referral_id=referral.id,
                payout_type="REFERRAL_BONUS",
                amount=100.00,
                status="PENDING_APPROVAL"
            )
            self.db.add(payout)
        elif new_stage == ReferralStageEnum.FAILED.value:
            referral.failure_reason = failure_reason

        self.db.commit()
        self.db.refresh(referral)
        return referral
