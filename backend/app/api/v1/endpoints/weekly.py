"""
Weekly stats endpoint for Trends view.
GET /stats/weekly — returns 7 or 30 day data for charts.
"""
from datetime import datetime, timezone, timedelta, date as date_type
from zoneinfo import ZoneInfo
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func, and_, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.meal import Meal
from app.models.water import WaterLog
from app.models.whoop import WhoopSleep, WhoopRecovery, WhoopWorkout, WhoopCycle

KYIV_TZ = ZoneInfo("Europe/Kyiv")

router = APIRouter(prefix="/stats", tags=["stats-weekly"])

DAY_NAMES_UK = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]


class DayPoint(BaseModel):
    day: str
    date: str
    value: float


class WeeklyTrends(BaseModel):
    calories: List[DayPoint]
    sleep: List[DayPoint]
    recovery: List[DayPoint]
    strain: List[DayPoint]
    water: List[DayPoint]
    avg_macros: dict


def _ms_to_hours(ms: Optional[int]) -> float:
    if not ms:
        return 0.0
    return round(ms / 3_600_000, 1)


@router.get("/weekly", response_model=WeeklyTrends)
async def get_weekly_trends(
    days: int = Query(7, ge=7, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get daily data points for the last N days (default 7)."""
    today = datetime.now(timezone.utc).date()

    # Build date range
    dates = []
    for i in range(days - 1, -1, -1):
        dates.append(today - timedelta(days=i))

    calories_points = []
    sleep_points = []
    recovery_points = []
    strain_points = []
    water_points = []

    total_protein = 0.0
    total_carbs = 0.0
    total_fats = 0.0
    days_with_meals = 0

    for d in dates:
        day_start = datetime.combine(d, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = datetime.combine(d, datetime.max.time()).replace(tzinfo=timezone.utc)
        day_name = DAY_NAMES_UK[d.weekday()]
        date_str = d.isoformat()

        # --- Calories ---
        stmt = select(
            func.sum(Meal.calories),
            func.sum(Meal.protein_g),
            func.sum(Meal.carbs_g),
            func.sum(Meal.fats_g),
        ).where(and_(
            Meal.user_id == current_user.id,
            Meal.created_at >= day_start,
            Meal.created_at <= day_end,
        ))
        result = await db.execute(stmt)
        row = result.one()
        day_cal = float(row[0] or 0)
        day_protein = float(row[1] or 0)
        day_carbs = float(row[2] or 0)
        day_fats = float(row[3] or 0)

        calories_points.append(DayPoint(day=day_name, date=date_str, value=round(day_cal)))

        if day_cal > 0:
            total_protein += day_protein
            total_carbs += day_carbs
            total_fats += day_fats
            days_with_meals += 1

        # --- Sleep (sleep that ended on this day) ---
        stmt = (
            select(WhoopSleep)
            .where(and_(
                WhoopSleep.user_id == current_user.id,
                WhoopSleep.end_time >= day_start,
                WhoopSleep.end_time <= day_end,
            ))
            .order_by(WhoopSleep.end_time.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        sleep = result.scalar_one_or_none()
        if sleep:
            total_ms = (
                (sleep.deep_duration_ms or 0)
                + (sleep.rem_duration_ms or 0)
                + (sleep.light_duration_ms or 0)
                + (sleep.wake_duration_ms or 0)
            )
            sleep_points.append(DayPoint(day=day_name, date=date_str, value=_ms_to_hours(total_ms)))
        else:
            sleep_points.append(DayPoint(day=day_name, date=date_str, value=0))

        # --- Recovery ---
        stmt = (
            select(WhoopRecovery)
            .where(and_(
                WhoopRecovery.user_id == current_user.id,
                WhoopRecovery.created_at >= day_start,
                WhoopRecovery.created_at <= day_end,
            ))
            .order_by(WhoopRecovery.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        rec = result.scalar_one_or_none()
        recovery_points.append(DayPoint(
            day=day_name, date=date_str,
            value=round(rec.score) if rec and rec.score else 0,
        ))

        # Strain from cycles — WHOOP cycle starts at sleep time the PREVIOUS evening,
        # so strain for day D comes from cycle with start_time on day D-1
        prev_day = d - timedelta(days=1)
        prev_start = datetime.combine(prev_day, datetime.min.time()).replace(tzinfo=timezone.utc)
        prev_end = datetime.combine(prev_day, datetime.max.time()).replace(tzinfo=timezone.utc)
        stmt = (
            select(WhoopCycle)
            .where(and_(
                WhoopCycle.user_id == current_user.id,
                WhoopCycle.start_time >= prev_start,
                WhoopCycle.start_time <= prev_end,
            ))
            .order_by(WhoopCycle.start_time.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        cycle = result.scalar_one_or_none()
        strain_val = round(cycle.day_strain, 1) if cycle and cycle.day_strain is not None else 0
        strain_points.append(DayPoint(day=day_name, date=date_str, value=strain_val))

        # --- Water ---
        stmt = select(func.sum(WaterLog.amount_ml)).where(and_(
            WaterLog.user_id == current_user.id,
            WaterLog.created_at >= day_start,
            WaterLog.created_at <= day_end,
        ))
        result = await db.execute(stmt)
        water_total = result.scalar() or 0
        water_points.append(DayPoint(day=day_name, date=date_str, value=int(water_total)))

    # Average macros
    avg_macros = {
        "protein": round(total_protein / days_with_meals) if days_with_meals > 0 else 0,
        "carbs": round(total_carbs / days_with_meals) if days_with_meals > 0 else 0,
        "fat": round(total_fats / days_with_meals) if days_with_meals > 0 else 0,
    }

    return WeeklyTrends(
        calories=calories_points,
        sleep=sleep_points,
        recovery=recovery_points,
        strain=strain_points,
        water=water_points,
        avg_macros=avg_macros,
    )


# --- Demo version (by telegram_id) ---

@router.get("/weekly/demo")
async def get_weekly_trends_demo(
    telegram_id: int = Query(...),
    days: int = Query(7, ge=7, le=30),
    db: AsyncSession = Depends(get_db),
):
    """Weekly trends by telegram_id (no auth)."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {"error": "User not found"}

    today = datetime.now(timezone.utc).date()
    dates = [today - timedelta(days=i) for i in range(days - 1, -1, -1)]

    calories_points = []
    sleep_points = []
    recovery_points = []
    strain_points = []
    water_points = []
    total_protein = 0.0
    total_carbs = 0.0
    total_fats = 0.0
    days_with_meals = 0

    for d in dates:
        day_start = datetime.combine(d, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = datetime.combine(d, datetime.max.time()).replace(tzinfo=timezone.utc)
        day_name = DAY_NAMES_UK[d.weekday()]
        date_str = d.isoformat()

        # Calories
        stmt = select(
            func.sum(Meal.calories),
            func.sum(Meal.protein_g),
            func.sum(Meal.carbs_g),
            func.sum(Meal.fats_g),
        ).where(and_(
            Meal.user_id == user.id,
            Meal.created_at >= day_start,
            Meal.created_at <= day_end,
        ))
        result = await db.execute(stmt)
        row = result.one()
        day_cal = float(row[0] or 0)
        calories_points.append({"day": day_name, "date": date_str, "value": round(day_cal)})
        if day_cal > 0:
            total_protein += float(row[1] or 0)
            total_carbs += float(row[2] or 0)
            total_fats += float(row[3] or 0)
            days_with_meals += 1

        # Sleep
        stmt = (
            select(WhoopSleep)
            .where(and_(
                WhoopSleep.user_id == user.id,
                WhoopSleep.end_time >= day_start,
                WhoopSleep.end_time <= day_end,
            ))
            .order_by(WhoopSleep.end_time.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        sleep = result.scalar_one_or_none()
        if sleep:
            total_ms = (
                (sleep.deep_duration_ms or 0) + (sleep.rem_duration_ms or 0)
                + (sleep.light_duration_ms or 0) + (sleep.wake_duration_ms or 0)
            )
            sleep_points.append({"day": day_name, "date": date_str, "value": _ms_to_hours(total_ms)})
        else:
            sleep_points.append({"day": day_name, "date": date_str, "value": 0})

        # Recovery
        stmt = (
            select(WhoopRecovery)
            .where(and_(
                WhoopRecovery.user_id == user.id,
                WhoopRecovery.created_at >= day_start,
                WhoopRecovery.created_at <= day_end,
            ))
            .order_by(WhoopRecovery.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        rec = result.scalar_one_or_none()
        recovery_points.append({"day": day_name, "date": date_str, "value": round(rec.score) if rec and rec.score else 0})

        # Strain from cycles — WHOOP cycle starts at sleep time the PREVIOUS evening,
        # so strain for day D comes from cycle with start_time on day D-1
        prev_day = d - timedelta(days=1)
        prev_start = datetime.combine(prev_day, datetime.min.time()).replace(tzinfo=timezone.utc)
        prev_end = datetime.combine(prev_day, datetime.max.time()).replace(tzinfo=timezone.utc)
        stmt = (
            select(WhoopCycle)
            .where(and_(
                WhoopCycle.user_id == user.id,
                WhoopCycle.start_time >= prev_start,
                WhoopCycle.start_time <= prev_end,
            ))
            .order_by(WhoopCycle.start_time.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        cycle = result.scalar_one_or_none()
        strain_points.append({"day": day_name, "date": date_str, "value": round(cycle.day_strain, 1) if cycle and cycle.day_strain is not None else 0})

        # Water
        stmt = select(func.sum(WaterLog.amount_ml)).where(and_(
            WaterLog.user_id == user.id,
            WaterLog.created_at >= day_start,
            WaterLog.created_at <= day_end,
        ))
        result = await db.execute(stmt)
        water_total = result.scalar() or 0
        water_points.append({"day": day_name, "date": date_str, "value": int(water_total)})

    return {
        "calories": calories_points,
        "sleep": sleep_points,
        "recovery": recovery_points,
        "strain": strain_points,
        "water": water_points,
        "avg_macros": {
            "protein": round(total_protein / days_with_meals) if days_with_meals > 0 else 0,
            "carbs": round(total_carbs / days_with_meals) if days_with_meals > 0 else 0,
            "fat": round(total_fats / days_with_meals) if days_with_meals > 0 else 0,
        },
    }
