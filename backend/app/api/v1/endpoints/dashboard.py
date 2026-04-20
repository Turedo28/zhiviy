from datetime import datetime, date as date_type, timezone, timedelta
from zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")
from typing import Optional, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.meal import Meal
from app.models.whoop import WhoopSleep, WhoopRecovery, WhoopWorkout, WhoopToken, WhoopCycle
from app.models.water import WaterLog
from app.services.nutrition import get_nutrition_plan, calculate_age_from_dob

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


class NutritionRecommendation(BaseModel):
    type: str
    icon: str
    text: str


class NutritionPlan(BaseModel):
    bmr: int
    tdee: int
    target_calories: int
    protein_target: float
    carbs_target: float
    fats_target: float
    goal: str
    goal_label: str
    calories_burned: float
    day_strain: Optional[float]
    recommendations: List[NutritionRecommendation]


class SleepSummary(BaseModel):
    hours: float
    score: Optional[float]
    efficiency: Optional[float]
    deep_hours: float
    rem_hours: float
    light_hours: float
    awake_hours: float
    bed_time: Optional[str] = None
    wake_time: Optional[str] = None


class RecoverySummary(BaseModel):
    score: Optional[float]
    hrv: Optional[float]
    resting_hr: Optional[float]
    spo2: Optional[float]
    level: str  # green/yellow/red


class WaterSummary(BaseModel):
    consumed_ml: int
    target_ml: int
    percentage: int


class WorkoutSummary(BaseModel):
    sport_name: str
    duration_min: int
    strain: Optional[float]
    calories: int
    start_time: str


class TodaySummary(BaseModel):
    date: str
    user_name: str
    nutrition: NutritionSummary
    sleep: Optional[SleepSummary]
    recovery: Optional[RecoverySummary]
    water: Optional[WaterSummary] = None
    workouts: Optional[List[WorkoutSummary]] = None
    whoop_connected: bool
    strain: Optional[float] = None
    nutrition_plan: Optional[NutritionPlan] = None


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


async def _get_nutrition_context(db: AsyncSession, user, today_start, today_end):
    """
    Shared helper: fetch latest day_strain, burned calories, and compute nutrition plan.
    Uses Cycle API data (intraday) with fallback to Recovery/Workouts.
    Returns (day_strain, calories_burned, nutrition_plan_dict, cal_target, macros).
    """
    day_strain = None
    calories_burned = 0.0

    # --- PRIMARY: Get strain + calories from latest Cycle (updates intraday) ---
    # WHOOP cycles start at sleep time the PREVIOUS evening, so today's strain
    # comes from a cycle with start_time yesterday evening.
    # Look back 24h to catch it.
    yesterday_start = today_start - timedelta(days=1)
    stmt = (
        select(WhoopCycle)
        .where(
            and_(
                WhoopCycle.user_id == user.id,
                WhoopCycle.start_time >= yesterday_start,
            )
        )
        .order_by(WhoopCycle.start_time.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    cycle = result.scalar_one_or_none()

    if cycle:
        if cycle.day_strain is not None:
            day_strain = cycle.day_strain
        if cycle.kilojoule is not None:
            # Convert kJ to kcal (1 kJ = 0.239006 kcal)
            calories_burned = round(cycle.kilojoule * 0.239006, 1)

    # --- FALLBACK: Recovery for strain if no Cycle ---
    if day_strain is None:
        stmt = (
            select(WhoopRecovery)
            .where(WhoopRecovery.user_id == user.id)
            .order_by(WhoopRecovery.whoop_cycle_id.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        recovery = result.scalar_one_or_none()
        if recovery and recovery.day_strain is not None:
            day_strain = recovery.day_strain

    # --- FALLBACK: Workouts sum for calories if no Cycle ---
    if calories_burned == 0.0:
        stmt = select(func.sum(WhoopWorkout.calories)).where(
            and_(
                WhoopWorkout.user_id == user.id,
                WhoopWorkout.start_time >= today_start,
                WhoopWorkout.start_time <= today_end,
            )
        )
        result = await db.execute(stmt)
        burned = result.scalar()
        if burned:
            calories_burned = float(burned)

    # Build nutrition plan if user profile is complete
    n_plan = None
    cal_target = 2100.0
    macros = {"protein_g": 160, "carbs_g": 220, "fats_g": 70}

    if user.weight_kg and user.height_cm and user.date_of_birth and user.gender:
        plan = get_nutrition_plan(
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            date_of_birth=user.date_of_birth,
            gender=user.gender,
            activity_level=user.activity_level or "moderate",
            goal=user.goal or "maintain",
            day_strain=day_strain,
            calories_burned=calories_burned,
        )
        cal_target = plan["target_calories"]
        macros = plan["macros"]
        n_plan = {
            "bmr": plan["bmr"],
            "tdee": plan["tdee"],
            "target_calories": plan["target_calories"],
            "protein_target": macros["protein_g"],
            "carbs_target": macros["carbs_g"],
            "fats_target": macros["fats_g"],
            "goal": plan["goal"],
            "goal_label": plan["goal_label"],
            "calories_burned": plan["calories_burned"],
            "day_strain": plan["day_strain"],
            "recommendations": plan["recommendations"],
        }

    return day_strain, calories_burned, n_plan, cal_target, macros


async def _get_water_summary(db: AsyncSession, user_id: int, weight_kg, today_start, today_end):
    """Fetch today's water consumption."""
    stmt = select(func.sum(WaterLog.amount_ml)).where(
        and_(
            WaterLog.user_id == user_id,
            WaterLog.created_at >= today_start,
            WaterLog.created_at <= today_end,
        )
    )
    result = await db.execute(stmt)
    total = result.scalar() or 0
    consumed = int(total)

    # Target: 30ml per kg, min 2000ml
    target = max(2000, int(weight_kg * 30)) if weight_kg else 2500

    return {
        "consumed_ml": consumed,
        "target_ml": target,
        "percentage": min(100, round(consumed / target * 100)) if target > 0 else 0,
    }


async def _get_workouts_today(db: AsyncSession, user_id: int, today_start, today_end):
    """Fetch today's WHOOP workouts."""
    stmt = (
        select(WhoopWorkout)
        .where(and_(
            WhoopWorkout.user_id == user_id,
            WhoopWorkout.start_time >= today_start,
            WhoopWorkout.start_time <= today_end,
        ))
        .order_by(WhoopWorkout.start_time.asc())
    )
    result = await db.execute(stmt)
    workouts = result.scalars().all()

    workouts_data = []
    for w in workouts:
        duration_min = 0
        if w.start_time and w.end_time:
            duration_min = round((w.end_time - w.start_time).total_seconds() / 60)
        workouts_data.append({
            "sport_name": w.sport_name or "Тренування",
            "duration_min": duration_min,
            "strain": round(w.strain, 1) if w.strain else None,
            "calories": round(w.calories) if w.calories else 0,
            "start_time": w.start_time.astimezone(KYIV_TZ).strftime("%H:%M") if w.start_time else "",
        })
    return workouts_data


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

    # --- Nutrition context (strain, burned calories, plan) ---
    day_strain, calories_burned, n_plan, cal_target, macros = await _get_nutrition_context(
        db, current_user, today_start, today_end
    )

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
        protein_target=macros["protein_g"],
        carbs_g=total_carbs,
        carbs_target=macros["carbs_g"],
        fats_g=total_fats,
        fats_target=macros["fats_g"],
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
            bed_time=sleep.start_time.astimezone(KYIV_TZ).strftime("%H:%M") if sleep.start_time else None,
            wake_time=sleep.end_time.astimezone(KYIV_TZ).strftime("%H:%M") if sleep.end_time else None,
        )

    # --- Recovery ---
    recovery_summary = None
    stmt = (
        select(WhoopRecovery)
        .where(WhoopRecovery.user_id == current_user.id)
        .order_by(WhoopRecovery.whoop_cycle_id.desc())
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
    stmt = select(WhoopToken).where(WhoopToken.user_id == current_user.id)
    result = await db.execute(stmt)
    whoop_connected = result.scalar_one_or_none() is not None

    # --- Water ---
    water_raw = await _get_water_summary(db, current_user.id, current_user.weight_kg, today_start, today_end)
    water_summary = WaterSummary(**water_raw)

    # --- Workouts ---
    workouts_raw = await _get_workouts_today(db, current_user.id, today_start, today_end)
    workouts_list = [WorkoutSummary(**w) for w in workouts_raw]

    return TodaySummary(
        date=today.isoformat(),
        user_name=current_user.first_name or "Користувач",
        nutrition=nutrition,
        sleep=sleep_summary,
        recovery=recovery_summary,
        water=water_summary,
        workouts=workouts_list,
        whoop_connected=whoop_connected,
        strain=day_strain,
        nutrition_plan=NutritionPlan(**n_plan) if n_plan else None,
    )
