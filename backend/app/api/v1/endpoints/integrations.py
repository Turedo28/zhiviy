from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.whoop import WhoopToken
from app.services.whoop_service import (
    get_whoop_auth_url,
    exchange_code_for_token,
    get_valid_token,
    sync_whoop_data,
    fetch_user_profile,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


class WhoopAuthUrlResponse(BaseModel):
    auth_url: str


class WhoopStatusResponse(BaseModel):
    connected: bool
    whoop_user_id: Optional[int] = None
    expires_at: Optional[str] = None


class WhoopSyncResponse(BaseModel):
    message: str
    synced_items: dict


# --- WHOOP OAuth Flow ---

@router.get("/whoop/auth-url", response_model=WhoopAuthUrlResponse)
async def get_whoop_auth_url_endpoint(
    current_user: User = Depends(get_current_user),
) -> WhoopAuthUrlResponse:
    """Generate WHOOP OAuth authorization URL."""
    state = str(current_user.id)
    auth_url = get_whoop_auth_url(state)
    return WhoopAuthUrlResponse(auth_url=auth_url)


@router.get("/whoop/connect")
async def whoop_connect_demo(
    telegram_id: int = None,
    db: AsyncSession = Depends(get_db),
):
    """Demo: generate WHOOP OAuth URL for a user by telegram_id."""
    if telegram_id is None:
        raise HTTPException(status_code=400, detail="telegram_id is required")
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        return {"error": "User not found"}
    auth_url = get_whoop_auth_url(str(user.id))
    return {"auth_url": auth_url, "instructions": "Open auth_url in browser to connect WHOOP"}


@router.get("/whoop/callback")
async def whoop_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """Handle WHOOP OAuth callback — exchange code for tokens and store them."""
    try:
        user_id = int(state.split("_")[0])
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Exchange code for tokens
        token_data = await exchange_code_for_token(code)

        # Get WHOOP user profile
        try:
            profile = await fetch_user_profile(token_data["access_token"])
            whoop_user_id = profile.get("user_id")
        except Exception:
            whoop_user_id = None

        # Store or update WHOOP token
        stmt = select(WhoopToken).where(WhoopToken.user_id == user.id)
        result = await db.execute(stmt)
        whoop_token = result.scalar_one_or_none()

        if whoop_token:
            whoop_token.access_token = token_data["access_token"]
            whoop_token.refresh_token = token_data["refresh_token"]
            whoop_token.expires_at = token_data["expires_at"]
            whoop_token.whoop_user_id = whoop_user_id
        else:
            whoop_token = WhoopToken(
                user_id=user.id,
                access_token=token_data["access_token"],
                refresh_token=token_data["refresh_token"],
                expires_at=token_data["expires_at"],
                whoop_user_id=whoop_user_id,
            )
            db.add(whoop_token)

        await db.commit()

        # Do initial sync
        try:
            await sync_whoop_data(user.id, token_data["access_token"], db, days_back=30)
        except Exception as e:
            pass  # Non-critical, user can sync manually

        # Redirect to dashboard
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?whoop=connected")

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"WHOOP connection failed: {e}")
        raise HTTPException(status_code=500, detail="WHOOP connection failed")


# --- WHOOP Status & Sync ---

@router.get("/whoop/status", response_model=WhoopStatusResponse)
async def whoop_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WhoopStatusResponse:
    """Check WHOOP connection status."""
    stmt = select(WhoopToken).where(WhoopToken.user_id == current_user.id)
    result = await db.execute(stmt)
    whoop_token = result.scalar_one_or_none()

    if not whoop_token:
        return WhoopStatusResponse(connected=False)

    return WhoopStatusResponse(
        connected=True,
        whoop_user_id=whoop_token.whoop_user_id,
        expires_at=whoop_token.expires_at.isoformat() if whoop_token.expires_at else None,
    )


@router.post("/whoop/sync", response_model=WhoopSyncResponse)
async def sync_whoop(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WhoopSyncResponse:
    """Trigger manual WHOOP data sync (last 7 days)."""
    stmt = select(WhoopToken).where(WhoopToken.user_id == current_user.id)
    result = await db.execute(stmt)
    whoop_token = result.scalar_one_or_none()

    if not whoop_token:
        raise HTTPException(status_code=400, detail="WHOOP not connected")

    try:
        access_token = await get_valid_token(whoop_token, db)
        counts = await sync_whoop_data(current_user.id, access_token, db, days_back=7)

        return WhoopSyncResponse(
            message="Sync completed successfully",
            synced_items=counts,
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"WHOOP sync failed: {e}")
        raise HTTPException(status_code=500, detail="Sync failed")


@router.delete("/whoop/disconnect")
async def disconnect_whoop(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect WHOOP account."""
    stmt = select(WhoopToken).where(WhoopToken.user_id == current_user.id)
    result = await db.execute(stmt)
    whoop_token = result.scalar_one_or_none()

    if not whoop_token:
        raise HTTPException(status_code=400, detail="WHOOP not connected")

    await db.delete(whoop_token)
    await db.commit()

    return {"detail": "WHOOP disconnected successfully"}


@router.get("/whoop/debug")
async def whoop_debug(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Debug: show WHOOP connection status (requires auth)."""
    stmt = select(WhoopToken).where(WhoopToken.user_id == current_user.id)
    result = await db.execute(stmt)
    whoop_token = result.scalar_one_or_none()
    if not whoop_token:
        return {"error": "WHOOP not connected"}

    return {
        "connected": True,
        "whoop_user_id": whoop_token.whoop_user_id,
        "expires_at": whoop_token.expires_at.isoformat() if whoop_token.expires_at else None,
    }
