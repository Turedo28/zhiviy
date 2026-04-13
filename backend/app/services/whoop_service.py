import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.whoop import WhoopToken, WhoopSleep, WhoopRecovery, WhoopWorkout

logger = logging.getLogger(__name__)

WHOOP_API_BASE = "https://api.prod.whoop.com"
WHOOP_AUTH_URL = f"{WHOOP_API_BASE}/oauth/oauth2/auth"
WHOOP_TOKEN_URL = f"{WHOOP_API_BASE}/oauth/oauth2/token"
WHOOP_API_V1 = f"{WHOOP_API_BASE}/developer/v1"
WHOOP_API_V2 = f"{WHOOP_API_BASE}/developer/v2"

WHOOP_SCOPES = "read:recovery read:cycles read:sleep read:workout read:profile read:body_measurement offline"


def get_whoop_auth_url(state: str) -> str:
    """Generate WHOOP OAuth authorization URL.
    State must be at least 8 chars per WHOOP requirements.
    We pad user_id with a random suffix: 'userid_randomhex'
    """
    # Ensure state is at least 8 chars: "user_id_random"
    safe_state = f"{state}_{secrets.token_hex(8)}"
    params = {
        "client_id": settings.WHOOP_CLIENT_ID,
        "scope": WHOOP_SCOPES,
        "redirect_uri": settings.WHOOP_REDIRECT_URI,
        "response_type": "code",
        "state": safe_state,
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{WHOOP_AUTH_URL}?{query_string}"


async def exchange_code_for_token(code: str) -> Dict[str, Any]:
    """Exchange authorization code for access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            WHOOP_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": settings.WHOOP_CLIENT_ID,
                "client_secret": settings.WHOOP_CLIENT_SECRET,
                "redirect_uri": settings.WHOOP_REDIRECT_URI,
            },
        )

        if response.status_code != 200:
            logger.error(f"WHOOP token exchange failed: {response.text}")
            raise Exception(f"WHOOP token exchange failed: {response.status_code}")

        data = response.json()
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"]),
            "token_type": data.get("token_type", "Bearer"),
        }


async def refresh_whoop_token(refresh_token: str) -> Dict[str, Any]:
    """Refresh WHOOP access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            WHOOP_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": settings.WHOOP_CLIENT_ID,
                "client_secret": settings.WHOOP_CLIENT_SECRET,
            },
        )

        if response.status_code != 200:
            logger.error(f"WHOOP token refresh failed: {response.text}")
            raise Exception(f"WHOOP token refresh failed: {response.status_code}")

        data = response.json()
        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", refresh_token),
            "expires_at": datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"]),
        }


async def get_valid_token(whoop_token: WhoopToken, db: AsyncSession) -> str:
    """Get valid access token, refreshing if expired."""
    if whoop_token.expires_at and whoop_token.expires_at < datetime.now(timezone.utc):
        logger.info("WHOOP token expired, refreshing...")
        new_tokens = await refresh_whoop_token(whoop_token.refresh_token)
        whoop_token.access_token = new_tokens["access_token"]
        whoop_token.refresh_token = new_tokens["refresh_token"]
        whoop_token.expires_at = new_tokens["expires_at"]
        await db.commit()
    return whoop_token.access_token


async def _whoop_get(access_token: str, endpoint: str, params: dict = None, api_version: str = "v1") -> dict:
    """Make authenticated GET request to WHOOP API."""
    base = WHOOP_API_V2 if api_version == "v2" else WHOOP_API_V1
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base}{endpoint}",
            headers=headers,
            params=params or {},
        )
        if response.status_code != 200:
            logger.error(f"WHOOP API error {endpoint}: {response.status_code} - {response.text}")
            raise Exception(f"WHOOP API error: {response.status_code}")
        return response.json()


async def fetch_user_profile(access_token: str) -> dict:
    """Fetch WHOOP user profile."""
    return await _whoop_get(access_token, "/user/profile/basic")


async def fetch_sleep_collection(
    access_token: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    """Fetch sleep records from WHOOP API."""
    params = {}
    if start_date:
        params["start"] = f"{start_date}T00:00:00.000Z"
    if end_date:
        params["end"] = f"{end_date}T23:59:59.999Z"

    data = await _whoop_get(access_token, "/activity/sleep", params, api_version="v2")
    return data.get("records", [])


async def fetch_recovery_collection(
    access_token: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    """Fetch recovery records from WHOOP API."""
    params = {}
    if start_date:
        params["start"] = f"{start_date}T00:00:00.000Z"
    if end_date:
        params["end"] = f"{end_date}T23:59:59.999Z"

    data = await _whoop_get(access_token, "/recovery", params, api_version="v2")
    return data.get("records", [])


async def fetch_workout_collection(
    access_token: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    """Fetch workout records from WHOOP API."""
    params = {}
    if start_date:
        params["start"] = f"{start_date}T00:00:00.000Z"
    if end_date:
        params["end"] = f"{end_date}T23:59:59.999Z"

    data = await _whoop_get(access_token, "/activity/workout", params, api_version="v2")
    return data.get("records", [])


async def fetch_cycle_collection(
    access_token: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[dict]:
    """Fetch physiological cycle records from WHOOP API."""
    params = {}
    if start_date:
        params["start"] = f"{start_date}T00:00:00.000Z"
    if end_date:
        params["end"] = f"{end_date}T23:59:59.999Z"

    data = await _whoop_get(access_token, "/cycle", params, api_version="v2")
    return data.get("records", [])


def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse WHOOP datetime string."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


async def sync_whoop_data(
    user_id: int,
    access_token: str,
    db: AsyncSession,
    days_back: int = 7,
) -> Dict[str, int]:
    """
    Sync WHOOP data (sleep, recovery, workouts) for a user.
    Returns count of synced items.
    """
    start_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
    counts = {"sleep": 0, "recovery": 0, "workouts": 0}

    # --- Sync Sleep (v2 format) ---
    try:
        sleeps = await fetch_sleep_collection(access_token, start_date=start_date)
        for s in sleeps:
            whoop_id = str(s.get("id", ""))
            if not whoop_id:
                continue

            # Check if already exists
            existing = await db.execute(
                select(WhoopSleep).where(WhoopSleep.whoop_id == whoop_id)
            )
            if existing.scalar_one_or_none():
                continue

            score_data = s.get("score", {}) or {}
            stage = score_data.get("stage_summary", {}) or {}
            sleep_record = WhoopSleep(
                user_id=user_id,
                whoop_id=whoop_id,
                start_time=_parse_datetime(s.get("start")),
                end_time=_parse_datetime(s.get("end")),
                score=score_data.get("sleep_performance_percentage"),
                quality_duration_ms=stage.get("total_in_bed_time_milli", 0),
                rem_duration_ms=stage.get("total_rem_sleep_time_milli", 0),
                light_duration_ms=stage.get("total_light_sleep_time_milli", 0),
                deep_duration_ms=stage.get("total_slow_wave_sleep_time_milli", 0),
                wake_duration_ms=stage.get("total_awake_time_milli", 0),
                efficiency=score_data.get("sleep_efficiency_percentage"),
                raw_data=json.dumps(s),
            )
            db.add(sleep_record)
            counts["sleep"] += 1
    except Exception as e:
        logger.error(f"Error syncing sleep: {e}")

    # --- Sync Recovery (v2 format) ---
    try:
        recoveries = await fetch_recovery_collection(access_token, start_date=start_date)
        for r in recoveries:
            cycle_id = r.get("cycle_id")
            if not cycle_id:
                continue

            existing = await db.execute(
                select(WhoopRecovery).where(WhoopRecovery.whoop_cycle_id == cycle_id)
            )
            if existing.scalar_one_or_none():
                continue

            score_data = r.get("score", {}) or {}
            recovery_record = WhoopRecovery(
                user_id=user_id,
                whoop_cycle_id=cycle_id,
                score=score_data.get("recovery_score"),
                hrv_rmssd=score_data.get("hrv_rmssd_milli"),
                resting_heart_rate=score_data.get("resting_heart_rate"),
                spo2=score_data.get("spo2_percentage"),
                skin_temp=score_data.get("skin_temp_celsius"),
                raw_data=json.dumps(r),
            )
            db.add(recovery_record)
            counts["recovery"] += 1
    except Exception as e:
        logger.error(f"Error syncing recovery: {e}")

    # --- Sync Workouts (v2 format) ---
    try:
        workouts = await fetch_workout_collection(access_token, start_date=start_date)
        for w in workouts:
            whoop_id = str(w.get("id", ""))
            if not whoop_id:
                continue

            existing = await db.execute(
                select(WhoopWorkout).where(WhoopWorkout.whoop_id == whoop_id)
            )
            if existing.scalar_one_or_none():
                continue

            score_data = w.get("score", {}) or {}
            workout_record = WhoopWorkout(
                user_id=user_id,
                whoop_id=whoop_id,
                sport_id=w.get("sport_id"),
                sport_name=w.get("sport_name"),
                start_time=_parse_datetime(w.get("start")),
                end_time=_parse_datetime(w.get("end")),
                strain=score_data.get("strain"),
                average_hr=score_data.get("average_heart_rate"),
                max_hr=score_data.get("max_heart_rate"),
                calories=score_data.get("kilojoule", 0) / 4.184 if score_data.get("kilojoule") else None,
                raw_data=json.dumps(w),
            )
            db.add(workout_record)
            counts["workouts"] += 1
    except Exception as e:
        logger.error(f"Error syncing workouts: {e}")

    await db.commit()
    logger.info(f"WHOOP sync complete for user {user_id}: {counts}")
    return counts
