"""
Stats endpoint for Telegram bot.
Returns today's real-time statistics by telegram_id (no JWT required).
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.meal import Meal
from app.models.water import WaterLog
from app.models.whoop import WhoopWorkout, WhoopToken
from app.services.calories_service import get_calories_burned_today
from app.services.nutrition import get_nutrition_plan, calculate_age_from_dob

router = APIRouter(prefix="/stats", tags=["stats"])


class CaloriesBurnedBreakdown(BaseModel):
    total: int
    bmr: int
    neat: int
    tef: int
    exercise: int
    bmr_full_day: int
    hours_elapsed: float
    source: str


class NutritionStats(BaseModel):
    calories_consumed: float
    calories_target: float
    protein_g: float
    protein_target: float
    carbs_g: float
    carbs_target: float
    fats_g: float
    fats_target: float
    meals_count: int
    goal: Optional[str] = None
    goal_label: Optional[str] = None


class WorkoutStats(BaseModel):
    count: int
    total_calories: float
    workouts: List[dict]


class TodayStats(BaseModel):
    date: str
    user_name: str
    nutrition: NutritionStats
    calories_burned: CaloriesBurnedBreakdown
    water_ml: float
    water_target_ml: float
    workouts: WorkoutStats
    whoop_connected: bool


@router.get("/today")
async def get_today_stats(
    telegram_id: int = Query(..., description="User's Telegram ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get today's real-time statistics for a user.
    Used by the Telegram bot (no JWT auth, uses telegram_id).
    """
    # Find user
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {"error": "User not found", "code": "USER_NOT_FOUND"}

    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)

    # --- Nutrition (meals today) ---
    stmt = (
        select(Meal)
        .where(and_(
            Meal.user_id == user.id,
            Meal.created_at >= today_start,
            Meal.created_at <= today_end,
        ))
        .order_by(Meal.created_at.asc())
    )
    result = await db.execute(stmt)
    meals_list = result.scalars().all()

    total_cal = sum(m.calories or 0 for m in meals_list)
    total_protein = sum(m.protein_g or 0 for m in meals_list)
    total_carbs = sum(m.carbs_g or 0 for m in meals_list)
    total_fats = sum(m.fats_g or 0 for m in meals_list)

    # Calculate targets from nutrition plan
    cal_target = 2100.0
    macros = {"protein_g": 160, "carbs_g": 220, "fats_g": 70}
    goal = user.goal or "maintain"
    goal_label = ""

    if user.weight_kg and user.height_cm and user.date_of_birth and user.gender:
        from app.services.nutrition import GOAL_LABELS_UK
        plan = get_nutrition_plan(
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            date_of_birth=user.date_of_birth,
            gender=user.gender,
            activity_level=user.activity_level or "moderate",
            goal=goal,
        )
        cal_target = plan["target_calories"]
        macros = plan["macros"]
        goal_label = GOAL_LABELS_UK.get(goal, goal)

    # --- Calories burned (full breakdown) ---
    burned = await get_calories_burned_today(db, user, today_start, today_end)

    # --- Water today ---
    stmt = select(func.sum(WaterLog.amount_ml)).where(
        and_(
            WaterLog.user_id == user.id,
            WaterLog.created_at >= today_start,
            WaterLog.created_at <= today_end,
        )
    )
    result = await db.execute(stmt)
    water_total = result.scalar()
    water_ml = float(water_total) if water_total else 0.0
    water_target_ml = 3000.0  # Default 3L target

    # --- Workouts today ---
    stmt = (
        select(WhoopWorkout)
        .where(and_(
            WhoopWorkout.user_id == user.id,
            WhoopWorkout.start_time >= today_start,
            WhoopWorkout.start_time <= today_end,
        ))
        .order_by(WhoopWorkout.start_time.asc())
    )
    result = await db.execute(stmt)
    workouts = result.scalars().all()

    workouts_data = []
    total_workout_cal = 0.0
    for w in workouts:
        cal = w.calories or 0
        total_workout_cal += cal
        duration_min = 0
        if w.start_time and w.end_time:
            duration_min = round((w.end_time - w.start_time).total_seconds() / 60)
        workouts_data.append({
            "sport": w.sport_name or "Тренування",
            "calories": round(cal),
            "duration_min": duration_min,
            "strain": round(w.strain, 1) if w.strain else None,
        })

    # --- WHOOP connected? ---
    stmt = select(WhoopToken).where(WhoopToken.user_id == user.id)
    result = await db.execute(stmt)
    whoop_connected = result.scalar_one_or_none() is not None

    return {
        "date": today.isoformat(),
        "user_name": user.first_name or "Користувач",
        "nutrition": {
            "calories_consumed": round(total_cal),
            "calories_target": round(cal_target),
            "protein_g": round(total_protein),
            "protein_target": macros["protein_g"],
            "carbs_g": round(total_carbs),
            "carbs_target": macros["carbs_g"],
            "fats_g": round(total_fats),
            "fats_target": macros["fats_g"],
            "meals_count": len(meals_list),
            "goal": goal,
            "goal_label": goal_label,
        },
        "calories_burned": burned,
        "water_ml": round(water_ml),
        "water_target_ml": round(water_target_ml),
        "workouts": {
            "count": len(workouts),
            "total_calories": round(total_workout_cal),
            "workouts": workouts_data,
        },
        "whoop_connected": whoop_connected,
    }
