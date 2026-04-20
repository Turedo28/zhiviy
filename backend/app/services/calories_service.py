"""
Calories burned calculation service.
Calculates total calories burned today using BMR + NEAT + TEF + Exercise.
Supports WHOOP, future Apple Health, and fallback calculation.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.whoop import WhoopWorkout
from app.models.meal import Meal
from app.services.nutrition import calculate_bmr, calculate_age_from_dob


# NEAT multipliers based on activity level (% of BMR)
NEAT_MULTIPLIERS = {
    "sedentary": 0.10,
    "light": 0.20,
    "moderate": 0.30,
    "active": 0.40,
    "very_active": 0.50,
}

# MET values for manual workout estimation
MET_VALUES = {
    "walking": 3.5,
    "running_8kmh": 8.3,
    "running_10kmh": 10.0,
    "cycling": 6.8,
    "swimming": 7.0,
    "strength_moderate": 5.0,
    "strength_intense": 6.0,
    "hiit": 8.0,
    "yoga": 3.0,
    "crossfit": 8.0,
    "boxing": 9.0,
    "dancing": 5.5,
    "tennis": 7.3,
    "football": 7.0,
    "basketball": 6.5,
}

# TEF coefficient (Thermic Effect of Food)
TEF_COEFFICIENT = 0.10


def calculate_calories_burned_now(
    bmr: float,
    hours_elapsed: float,
    exercise_calories: float,
    calories_consumed: float,
    activity_level: str,
    steps: int = 0,
    weight_kg: float = 70.0,
) -> Dict[str, Any]:
    """
    Calculate total calories burned so far today.

    Components:
    - BMR: Proportional to hours elapsed in the day
    - NEAT: Based on steps (if available) or activity level
    - TEF: 10% of calories consumed today
    - EAT: Exercise calories from WHOOP/Apple Health/manual

    Returns dict with total and breakdown.
    """
    # 1. BMR proportional to time of day
    bmr_so_far = bmr * (hours_elapsed / 24.0)

    # 2. NEAT (Non-Exercise Activity Thermogenesis)
    if steps > 0:
        # ~0.04 kcal/step for average 70kg person, scaled by weight
        neat_calories = steps * 0.04 * (weight_kg / 70.0)
    else:
        neat_pct = NEAT_MULTIPLIERS.get(activity_level, 0.20)
        neat_calories = bmr_so_far * neat_pct

    # 3. TEF (Thermic Effect of Food)
    tef_calories = calories_consumed * TEF_COEFFICIENT

    # 4. EAT (Exercise Activity Thermogenesis)
    eat_calories = exercise_calories

    total_burned = bmr_so_far + neat_calories + tef_calories + eat_calories

    return {
        "total": round(total_burned),
        "bmr": round(bmr_so_far),
        "neat": round(neat_calories),
        "tef": round(tef_calories),
        "exercise": round(eat_calories),
        "bmr_full_day": round(bmr),
        "hours_elapsed": round(hours_elapsed, 1),
        "source": "calculated",
    }


def estimate_exercise_calories(
    exercise_type: str,
    duration_minutes: float,
    weight_kg: float,
) -> float:
    """Estimate calories burned from exercise using MET formula."""
    met = MET_VALUES.get(exercise_type, 5.0)
    duration_hours = duration_minutes / 60.0
    return round(met * weight_kg * duration_hours)


async def get_calories_burned_today(
    db: AsyncSession,
    user,
    today_start: datetime,
    today_end: datetime,
    user_timezone_offset_hours: int = 2,  # Default UTC+2 (Ukraine)
) -> Dict[str, Any]:
    """
    Get complete calories burned breakdown for today.

    Priority: Apple Health > WHOOP > Calculated.
    Currently supports WHOOP + calculated fallback.
    Apple Health integration is prepared for future.
    """
    # Calculate hours elapsed today
    now = datetime.now(timezone.utc)
    hours_elapsed = (now - today_start).total_seconds() / 3600.0
    hours_elapsed = min(max(hours_elapsed, 0), 24.0)

    # Calculate BMR from user profile
    if not (user.weight_kg and user.height_cm and user.date_of_birth and user.gender):
        # Incomplete profile — return basic estimate
        return {
            "total": 0,
            "bmr": 0,
            "neat": 0,
            "tef": 0,
            "exercise": 0,
            "bmr_full_day": 0,
            "hours_elapsed": round(hours_elapsed, 1),
            "source": "incomplete_profile",
        }

    age = calculate_age_from_dob(user.date_of_birth)
    bmr = calculate_bmr(user.weight_kg, user.height_cm, age, user.gender)

    # TODO: Future — check Apple Health data first
    # apple_data = await get_apple_health_today(db, user.id, today_start)
    # if apple_data and apple_data.total_energy_kcal:
    #     return { ... source: "apple_health" }

    # Get WHOOP exercise calories for today
    exercise_calories = 0.0
    stmt = select(func.sum(WhoopWorkout.calories)).where(
        and_(
            WhoopWorkout.user_id == user.id,
            WhoopWorkout.start_time >= today_start,
            WhoopWorkout.start_time <= today_end,
        )
    )
    result = await db.execute(stmt)
    whoop_burned = result.scalar()
    if whoop_burned:
        exercise_calories = float(whoop_burned)

    # Get calories consumed today (for TEF calculation)
    stmt = select(func.sum(Meal.calories)).where(
        and_(
            Meal.user_id == user.id,
            Meal.created_at >= today_start,
            Meal.created_at <= today_end,
        )
    )
    result = await db.execute(stmt)
    consumed = result.scalar()
    calories_consumed = float(consumed) if consumed else 0.0

    # Calculate full breakdown
    burned = calculate_calories_burned_now(
        bmr=bmr,
        hours_elapsed=hours_elapsed,
        exercise_calories=exercise_calories,
        calories_consumed=calories_consumed,
        activity_level=user.activity_level or "moderate",
        steps=0,  # TODO: from Apple Health
        weight_kg=user.weight_kg,
    )

    # Set source
    burned["source"] = "whoop" if exercise_calories > 0 else "calculated"

    return burned
