from datetime import datetime, date as date_type, timezone, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.meal import Meal
from app.models.whoop import WhoopSleep, WhoopRecovery, WhoopWorkout, WhoopToken

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class MealSummary(BaseModel):
    id: int
    name: str
    description: Optional[str]
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float
    time: str
    source: str


class NutritionSummary(BaseModel):
    calories_consumed: float
    calories_target: float
    protein_g: float
    protein_target: float
    carbs_g: float
    carbs_target: float
    fats_g: float
    fats_target: float
    meals: List[MealSummary]


class SleepSummary(BaseModel):
    hours: float
    score: Optional[float]
    efficiency: Optional[float]
    deep_hours: float
    rem_hours: float
    light_hours: float
    awake_hours: float


class RecoverySummary(BaseModel):
    score: Optional[float]
    hrv: Optional[float]
    resting_hr: Optional[float]
    spo2: Optional[float]
    level: str  # green/yellow/red


class TodaySummary(BaseModel):
    date: str
    user_name: str
    nutrition: NutritionSummary
    sleep: Optional[SleepSummary]
    recovery: Optional[RecoverySummary]
    whoop_connected: bool


def _ms_to_hours(ms: Optional[int]) -> float:
    if not ms:
        return 0.0
    return round(ms / 3_600_000, 1)


def _recovery_level(score: Optional[float]) -> str:
    if score is None:
        return "unknown"
    if score >= 67:
        return "green"
    elif score >= 34:
        return "yellow"
    return "red"


@router.get("/today/demo")
async def get_today_summary_demo(
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Demo endpoint: get today's summary by telegram_id (no auth required)."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {"error": "User not found"}

    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

    stmt = (
        select(Meal)
        .where(and_(Meal.user_id == user.id, Meal.created_at >= today_start, Meal.created_at <= today_end))
        .order_by(Meal.created_at.asc())
    )
    result = await db.execute(stmt)
    meals_list = result.scalars().all()

    total_cal = sum(m.calories or 0 for m in meals_list)
    total_protein = sum(m.protein_g or 0 for m in meals_list)
    total_carbs = sum(m.carbs_g or 0 for m in meals_list)
    total_fats = sum(m.fats_g or 0 for m in meals_list)

    meals_data = [
        {
            "id": m.id,
            "name": m.name or "Страва",
            "description": m.description,
            "calories": m.calories or 0,
            "protein_g": m.protein_g or 0,
            "carbs_g": m.carbs_g or 0,
            "fats_g": m.fats_g or 0,
            "time": m.created_at.strftime("%H:%M") if m.created_at else "",
            "source": m.source or "unknown",
        }
        for m in meals_list
    ]

    # --- WHOOP connected? ---
    stmt = select(WhoopToken).where(WhoopToken.user_id == user.id)
    result = await db.execute(stmt)
    whoop_connected = result.scalar_one_or_none() is not None

    # --- Sleep (last night) ---
    sleep_data = None
    yesterday_start = today_start - timedelta(days=1)
    stmt = (
        select(WhoopSleep)
        .where(and_(
            WhoopSleep.user_id == user.id,
            WhoopSleep.end_time >= yesterday_start,
            WhoopSleep.end_time <= today_end,
        ))
        .order_by(WhoopSleep.end_time.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    sleep = result.scalar_one_or_none()

    if sleep:
        total_sleep_ms = (
            (sleep.deep_duration_ms or 0)
            + (sleep.rem_duration_ms or 0)
            + (sleep.light_duration_ms or 0)
        )
        sleep_data = {
            "hours": _ms_to_hours(total_sleep_ms + (sleep.wake_duration_ms or 0)),
            "score": sleep.score,
            "efficiency": sleep.efficiency,
            "deep_hours": _ms_to_hours(sleep.deep_duration_ms),
            "rem_hours": _ms_to_hours(sleep.rem_duration_ms),
            "light_hours": _ms_to_hours(sleep.light_duration_ms),
            "awake_hours": _ms_to_hours(sleep.wake_duration_ms),
        }

    # --- Recovery ---
    recovery_data = None
    stmt = (
        select(WhoopRecovery)
        .where(WhoopRecovery.user_id == user.id)
        .order_by(WhoopRecovery.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    recovery = result.scalar_one_or_none()

    if recovery:
        recovery_data = {
            "score": recovery.score,
            "hrv": recovery.hrv_rmssd,
            "resting_hr": recovery.resting_heart_rate,
            "spo2": recovery.spo2,
            "level": _recovery_level(recovery.score),
        }

    return {
        "date": today.isoformat(),
        "user_name": user.first_name or "Користувач",
        "nutrition": {
            "calories_consumed": total_cal,
            "calories_target": 2100,
            "protein_g": total_protein,
            "protein_target": 160,
            "carbs_g": total_carbs,
            "carbs_target": 220,
            "fats_g": total_fats,
            "fats_target": 70,
            "meals": meals_data,
        },
        "sleep": sleep_data,
        "recovery": recovery_data,
        "whoop_connected": whoop_connected,
    }


@router.get("/today", response_model=TodaySummary)
async def get_today_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TodaySummary:
    """Get today's dashboard summary: nutrition, sleep, recovery."""
    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

    # --- Meals ---
    stmt = (
        select(Meal)
        .where(and_(
            Meal.user_id == current_user.id,
            Meal.created_at >= today_start,
            Meal.created_at <= today_end,
        ))
        .order_by(Meal.created_at.asc())
    )
    result = await db.execute(stmt)
    meals = result.scalars().all()

    total_cal = sum(m.calories or 0 for m in meals)
    total_protein = sum(m.protein_g or 0 for m in meals)
    total_carbs = sum(m.carbs_g or 0 for m in meals)
    total_fats = sum(m.fats_g or 0 for m in meals)

    # Calorie target based on user profile (Mifflin-St Jeor)
    cal_target = 2100.0  # Default
    if current_user.weight_kg and current_user.height_cm:
        bmr = 10 * current_user.weight_kg + 6.25 * current_user.height_cm - 5 * 30  # assume age 30
        if current_user.gender == "male":
            bmr += 5
        else:
            bmr -= 161
        activity_multipliers = {
            "sedentary": 1.2, "light": 1.375, "moderate": 1.55,
            "active": 1.725, "very_active": 1.9,
        }
        multiplier = activity_multipliers.get(current_user.activity_level or "moderate", 1.55)
        cal_target = round(bmr * multiplier)

    protein_target = round(current_user.weight_kg * 2) if current_user.weight_kg else 160
    fats_target = round(cal_target * 0.25 / 9)
    carbs_target = round((cal_target - protein_target * 4 - fats_target * 9) / 4)

    meal_summaries = [
        MealSummary(
            id=m.id,
            name=m.name or "Страва",
            description=m.description,
            calories=m.calories or 0,
            protein_g=m.protein_g or 0,
            carbs_g=m.carbs_g or 0,
            fats_g=m.fats_g or 0,
            time=m.created_at.strftime("%H:%M") if m.created_at else "",
            source=m.source or "unknown",
        )
        for m in meals
    ]

    nutrition = NutritionSummary(
        calories_consumed=total_cal,
        calories_target=cal_target,
        protein_g=total_protein,
        protein_target=protein_target,
        carbs_g=total_carbs,
        carbs_target=carbs_target,
        fats_g=total_fats,
        fats_target=fats_target,
        meals=meal_summaries,
    )

    # --- Sleep (last night) ---
    sleep_summary = None
    yesterday_start = today_start - timedelta(days=1)
    stmt = (
        select(WhoopSleep)
        .where(and_(
            WhoopSleep.user_id == current_user.id,
            WhoopSleep.end_time >= yesterday_start,
            WhoopSleep.end_time <= today_end,
        ))
        .order_by(WhoopSleep.end_time.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    sleep = result.scalar_one_or_none()

    if sleep:
        total_sleep_ms = (
            (sleep.deep_duration_ms or 0)
            + (sleep.rem_duration_ms or 0)
            + (sleep.light_duration_ms or 0)
        )
        sleep_summary = SleepSummary(
            hours=_ms_to_hours(total_sleep_ms + (sleep.wake_duration_ms or 0)),
            score=sleep.score,
            efficiency=sleep.efficiency,
            deep_hours=_ms_to_hours(sleep.deep_duration_ms),
            rem_hours=_ms_to_hours(sleep.rem_duration_ms),
            light_hours=_ms_to_hours(sleep.light_duration_ms),
            awake_hours=_ms_to_hours(sleep.wake_duration_ms),
        )

    # --- Recovery ---
    recovery_summary = None
    stmt = (
        select(WhoopRecovery)
        .where(WhoopRecovery.user_id == current_user.id)
        .order_by(WhoopRecovery.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    recovery = result.scalar_one_or_none()

    if recovery:
        recovery_summary = RecoverySummary(
            score=recovery.score,
            hrv=recovery.hrv_rmssd,
            resting_hr=recovery.resting_heart_rate,
            spo2=recovery.spo2,
            level=_recovery_level(recovery.score),
        )

    # --- WHOOP connected? ---
    from app.models.whoop import WhoopToken
    stmt = select(WhoopToken).where(WhoopToken.user_id == current_user.id)
    result = await db.execute(stmt)
    whoop_connected = result.scalar_one_or_none() is not None

    return TodaySummary(
        date=today.isoformat(),
        user_name=current_user.first_name or "Користувач",
        nutrition=nutrition,
        sleep=sleep_summary,
        recovery=recovery_summary,
        whoop_connected=whoop_connected,
    )
