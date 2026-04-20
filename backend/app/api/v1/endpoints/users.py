from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


class UserProfileResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language: str
    onboarding_completed: bool
    date_of_birth: Optional[date]
    gender: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    activity_level: Optional[str]
    goal: Optional[str]
    water_tracking_enabled: bool
    supplements_tracking_enabled: bool

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    water_tracking_enabled: Optional[bool] = None
    supplements_tracking_enabled: Optional[bool] = None


class OnboardingUpdate(BaseModel):
    date_of_birth: date
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: str
    goal: str


@router.get("/me", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    """Get current user profile."""
    return UserProfileResponse.model_validate(current_user)


@router.put("/me", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Update current user profile."""
    update_data = profile_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.now(timezone.utc)
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return UserProfileResponse.model_validate(current_user)


@router.put("/me/onboarding", response_model=UserProfileResponse)
async def complete_onboarding(
    onboarding_data: OnboardingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Complete user onboarding."""
    current_user.date_of_birth = onboarding_data.date_of_birth
    current_user.gender = onboarding_data.gender
    current_user.height_cm = onboarding_data.height_cm
    current_user.weight_kg = onboarding_data.weight_kg
    current_user.activity_level = onboarding_data.activity_level
    current_user.goal = onboarding_data.goal
    current_user.onboarding_completed = True
    current_user.updated_at = datetime.now(timezone.utc)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return UserProfileResponse.model_validate(current_user)
