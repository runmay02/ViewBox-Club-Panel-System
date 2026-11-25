import random
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.member import MemberProfile
from app.models.user import User
from app.models.source import AcquisitionSource, SourceLink
from app.models.payout import Payout
from app.schemas.member import MemberOnboardingRequest, MemberProfileOut, MemberProfileUpdate
from app.models.referral import Referral
from app.utils.normalizer import calculate_age, calculate_next_eligible_date

class MemberService:
    def __init__(self, db: Session):
        self.db = db

    def generate_member_id(self) -> str:
        """Generate unique business ID VB10xxx."""
        count = self.db.query(func.count(MemberProfile.id)).scalar() or 0
        candidate_num = 10000 + count + 1
        candidate = f"VB{candidate_num}"
        while self.db.query(MemberProfile).filter(MemberProfile.member_id == candidate).first():
            candidate_num += 1
            candidate = f"VB{candidate_num}"
        return candidate

    def complete_onboarding(self, user_id: str, payload: MemberOnboardingRequest) -> MemberProfileOut:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found")

        if user.profile:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Member profile already exists")

        # Resolve acquisition source from source_token if provided
        acquisition_source_id = None
        if payload.source_token:
            link = self.db.query(SourceLink).filter(SourceLink.token == payload.source_token).first()
            if link and link.source.is_active:
                acquisition_source_id = link.source_id

        if not acquisition_source_id and payload.source_id:
            source = self.db.query(AcquisitionSource).filter_by(id=payload.source_id, is_active=True).first()
            if source:
                acquisition_source_id = source.id

        # If still no source, fallback to Website organic source
        if not acquisition_source_id:
            default_src = self.db.query(AcquisitionSource).filter(AcquisitionSource.name == "Website").first()
            if default_src:
                acquisition_source_id = default_src.id

        member_id = self.generate_member_id()

        profile = MemberProfile(
            member_id=member_id,
            user_id=user.id,
            full_name=payload.full_name,
            phone=user.phone,
            email=payload.email,
            gender=payload.gender,
            date_of_birth=payload.date_of_birth,
            city=payload.city,
            income_range=payload.income_range,
            interests=";".join(payload.interests),
            acquisition_source_id=acquisition_source_id,
        )
        self.db.add(profile)
        self.db.flush()

        # Source and referral attribution are independent, persisted in one transaction.
        if payload.referral_code:
            clean_code = payload.referral_code.strip().upper()
            referrer = self.db.query(MemberProfile).filter(MemberProfile.member_id == clean_code).first()
            already_referred = self.db.query(Referral).filter_by(referred_member_id=profile.id).first()
            if referrer and referrer.id != profile.id and not already_referred:
                self.db.add(Referral(
                    referrer_member_id=referrer.id,
                    referred_member_id=profile.id,
                    referral_token=f"ref_{clean_code}_{profile.member_id}",
                    stage="LEAD",
                ))

        self.db.commit()
        self.db.refresh(profile)
        return self.get_profile_out(profile)

    def get_profile_by_user_id(self, user_id: str) -> Optional[MemberProfileOut]:
        profile = self.db.query(MemberProfile).filter(MemberProfile.user_id == user_id).first()
        if not profile:
            return None
        return self.get_profile_out(profile)

    def update_profile(self, profile: MemberProfile, payload: MemberProfileUpdate) -> MemberProfileOut:
        changes = payload.model_dump(exclude_unset=True)
        if changes.get("full_name") is not None:
            profile.full_name = " ".join(changes["full_name"].split())
        if changes.get("city") is not None:
            from app.utils.normalizer import normalize_city
            profile.city = normalize_city(changes["city"]) or changes["city"].strip().title()
        if changes.get("income_range") is not None:
            profile.income_range = changes["income_range"].strip()
        if changes.get("interests") is not None:
            profile.interests = ";".join(dict.fromkeys(item.strip() for item in changes["interests"] if item.strip()))
        if "email" in changes:
            profile.email = changes["email"]
        self.db.commit()
        self.db.refresh(profile)
        return self.get_profile_out(profile)

    def get_profile_out(self, profile: MemberProfile) -> MemberProfileOut:
        age = calculate_age(profile.date_of_birth)
        cool_off_until = (
            calculate_next_eligible_date(profile.last_survey_completed_on)
            if profile.last_survey_completed_on
            else None
        )

        # Calculate total earned payouts
        total_earned = (
            self.db.query(func.sum(Payout.amount))
            .filter(Payout.member_id == profile.id, Payout.status == "PAID")
            .scalar()
            or 0.0
        )

        return MemberProfileOut(
            id=profile.id,
            member_id=profile.member_id,
            full_name=profile.full_name,
            phone=profile.phone,
            email=profile.email,
            gender=profile.gender,
            date_of_birth=profile.date_of_birth,
            age=age,
            city=profile.city,
            income_range=profile.income_range,
            interests=profile.interests.split(";") if profile.interests else [],
            acquisition_source=profile.acquisition_source.name if profile.acquisition_source else None,
            referral_token=f"ref_{profile.member_id}",
            referral_link=f"/join?ref={profile.member_id}",
            joined_on=profile.joined_on,
            last_survey_completed_on=profile.last_survey_completed_on,
            cool_off_until=cool_off_until,
            total_earned=float(total_earned),
        )
