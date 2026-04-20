from datetime import datetime, date as date_type, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.meal import Meal
from app.models.user import User
from app.services.claude_service import analyze_food_photo

router = APIRouter(prefix="/meals", tags=["meals"])


class MealResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class MealCreate(BaseModel):
    name: str
    description: Optional[str] = None
    calories: float
    protein_g: float = 0
    carbs_g: float = 0
    fats_g: float = 0


class MealAnalysisResponse(BaseModel):
    name: str
    description: Optional[str]
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float
    confidence: str


@router.get("", response_model=List[MealResponse])
async def list_meals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    date_from: Optional[date_type] = None,
    date_to: Optional[date_type] = None,
) -> List[MealResponse]:
    """List user meals with optional date filter."""
    stmt = select(Meal).where(Meal.user_id == current_user.id)

    if date_from:
        stmt = stmt.where(Meal.created_at >= datetime.combine(date_from, datetime.min.time()))

    if date_to:
        stmt = stmt.where(Meal.created_at <= datetime.combine(date_to, datetime.max.time()))

    stmt = stmt.order_by(Meal.created_at.desc())

    result = await db.execute(stmt)
    meals = result.scalars().all()

    return [MealResponse.model_validate(meal) for meal in meals]


@router.post("", response_model=MealResponse)
async def create_meal(
    meal_data: MealCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MealResponse:
    """Create meal manually."""
    meal = Meal(
        user_id=current_user.id,
        name=meal_data.name,
        description=meal_data.description,
        calories=meal_data.calories,
        protein_g=meal_data.protein_g,
        carbs_g=meal_data.carbs_g,
        fats_g=meal_data.fats_g,
        source="web",
    )

    db.add(meal)
    await db.commit()
    await db.refresh(meal)

    return MealResponse.model_validate(meal)


class BotMealCreate(BaseModel):
    telegram_id: int
    name: str
    description: Optional[str] = None
    calories: float
    protein_g: float = 0
    carbs_g: float = 0
    fats_g: float = 0
    fiber_g: float = 0
    weight_g: float = 0
    confidence: str = "medium"


@router.post("/bot", response_model=MealResponse)
async def create_meal_from_bot(
    meal_data: BotMealCreate,
    db: AsyncSession = Depends(get_db),
) -> MealResponse:
    """Create meal from Telegram bot (uses telegram_id instead of JWT)."""
    # Find or create user by telegram_id
    stmt = select(User).where(User.telegram_id == meal_data.telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=meal_data.telegram_id,
            language="uk",
        )
        db.add(user)
        await db.flush()

    meal = Meal(
        user_id=user.id,
        name=meal_data.name,
        description=meal_data.description,
        calories=meal_data.calories,
        protein_g=meal_data.protein_g,
        carbs_g=meal_data.carbs_g,
        fats_g=meal_data.fats_g,
        fiber_g=meal_data.fiber_g,
        weight_g=meal_data.weight_g,
        confidence=meal_data.confidence,
        source="telegram",
    )

    db.add(meal)
    await db.commit()
    await db.refresh(meal)

    return MealResponse.model_validate(meal)


@router.post("/analyze", response_model=MealAnalysisResponse)
async def analyze_meal_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MealAnalysisResponse:
    """Analyze food photo using Claude Vision."""
    content = await file.read()

    try:
        analysis = await analyze_food_photo(content)
        return analysis
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Photo analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze photo",
        )


@router.delete("/{meal_id}")
async def delete_meal(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a meal."""
    stmt = select(Meal).where(and_(Meal.id == meal_id, Meal.user_id == current_user.id))
    result = await db.execute(stmt)
    meal = result.scalar_one_or_none()

    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )

    await db.delete(meal)
    await db.commit()

    return {"detail": "Meal deleted"}
