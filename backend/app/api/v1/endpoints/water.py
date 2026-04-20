"""
Water tracking API endpoints.
POST /water — add water intake
GET /water/today — get today's water summary
DELETE /water/{id} — remove a water log entry
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.redis import get_redis
from app.models.user import User
from app.models.water import WaterLog

router = APIRouter(prefix="/water", tags=["water"])


# --- Schemas ---

class WaterAddRequest(BaseModel):
    amount_ml: int = Field(..., gt=0, le=5000, description="Amount of water in ml")


class WaterLogResponse(BaseModel):
    id: int
    amount_ml: int
    created_at: str


class WaterTodayResponse(BaseModel):
    consumed_ml: int
    target_ml: int
    percentage: int
    logs: list[WaterLogResponse]


# --- Helpers ---

def _get_today_range():
    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
    return today_start, today_end


def _calculate_water_target(user: User) -> int:
    """Calculate daily water target: 30ml per kg body weight, min 2000ml."""
    if user.weight_kg:
        return max(2000, int(user.weight_kg * 30))
    return 2500  # default


# --- JWT-authenticated endpoints ---

@router.post("", status_code=201)
async def add_water(
    body: WaterAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add water intake for the authenticated user."""
    log = WaterLog(user_id=current_user.id, amount_ml=body.amount_ml)
    db.add(log)
    await db.commit()
    await db.refresh(log)

    # Return updated today total
    today_start, today_end = _get_today_range()
    stmt = select(func.sum(WaterLog.amount_ml)).where(
        and_(
            WaterLog.user_id == current_user.id,
            WaterLog.created_at >= today_start,
            WaterLog.created_at <= today_end,
        )
    )
    result = await db.execute(stmt)
    total = result.scalar() or 0
    target = _calculate_water_target(current_user)

    try:
        redis = await get_redis()
        await redis.delete(f"dashboard:today:{current_user.id}")
    except Exception:
        pass

    return {
        "id": log.id,
        "amount_ml": log.amount_ml,
        "total_today_ml": int(total),
        "target_ml": target,
        "percentage": min(100, round(total / target * 100)) if target > 0 else 0,
    }


@router.get("/today", response_model=WaterTodayResponse)
async def get_water_today(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get today's water intake summary."""
    today_start, today_end = _get_today_range()
    target = _calculate_water_target(current_user)

    # Get all logs for today
    stmt = (
        select(WaterLog)
        .where(and_(
            WaterLog.user_id == current_user.id,
            WaterLog.created_at >= today_start,
            WaterLog.created_at <= today_end,
        ))
        .order_by(WaterLog.created_at.asc())
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    consumed = sum(l.amount_ml for l in logs)

    return WaterTodayResponse(
        consumed_ml=consumed,
        target_ml=target,
        percentage=min(100, round(consumed / target * 100)) if target > 0 else 0,
        logs=[
            WaterLogResponse(
                id=l.id,
                amount_ml=l.amount_ml,
                created_at=l.created_at.strftime("%H:%M") if l.created_at else "",
            )
            for l in logs
        ],
    )


@router.delete("/{log_id}", status_code=200)
async def delete_water_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific water log entry."""
    stmt = select(WaterLog).where(
        and_(WaterLog.id == log_id, WaterLog.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Water log not found")

    await db.delete(log)
    await db.commit()
    return {"deleted": True, "id": log_id}


# --- Bot endpoints (by telegram_id, no JWT) ---

@router.get("/today/bot/{telegram_id}")
async def get_water_today_bot(
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get today's water summary for Telegram bot (by telegram_id)."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {"consumed_ml": 0, "target_ml": 2500, "percentage": 0}

    today_start, today_end = _get_today_range()
    stmt = select(func.sum(WaterLog.amount_ml)).where(
        and_(
            WaterLog.user_id == user.id,
            WaterLog.created_at >= today_start,
            WaterLog.created_at <= today_end,
        )
    )
    result = await db.execute(stmt)
    total = int(result.scalar() or 0)
    target = _calculate_water_target(user)
    return {
        "consumed_ml": total,
        "target_ml": target,
        "percentage": min(100, round(total / target * 100)) if target > 0 else 0,
    }


@router.post("/bot/{telegram_id}", status_code=201)
async def add_water_bot(
    telegram_id: int,
    body: WaterAddRequest,
    db: AsyncSession = Depends(get_db),
):
    """Add water intake via Telegram bot (by telegram_id)."""
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        user = User(telegram_id=telegram_id, language="uk")
        db.add(user)
        await db.flush()

    log = WaterLog(user_id=user.id, amount_ml=body.amount_ml)
    db.add(log)
    await db.commit()

    # Return today total
    today_start, today_end = _get_today_range()
    stmt = select(func.sum(WaterLog.amount_ml)).where(
        and_(
            WaterLog.user_id == user.id,
            WaterLog.created_at >= today_start,
            WaterLog.created_at <= today_end,
        )
    )
    result = await db.execute(stmt)
    total = result.scalar() or 0
    target = _calculate_water_target(user)

    return {
        "total_today_ml": int(total),
        "target_ml": target,
        "percentage": min(100, round(total / target * 100)) if target > 0 else 0,
    }
