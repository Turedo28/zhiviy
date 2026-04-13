from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_telegram_hash
from app.models.user import User
from app.models.whoop import WhoopToken
from app.services.whoop_service import (
    exchange_code_for_token,
    fetch_user_profile,
    sync_whoop_data,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class TelegramLoginData(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    telegram_id: int


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language: str
    onboarding_completed: bool

    class Config:
        from_attributes = True


@router.post("/telegram", response_model=AuthTokenResponse)
async def telegram_login(
    data: TelegramLoginData,
    db: AsyncSession = Depends(get_db),
) -> AuthTokenResponse:
    """
    Verify Telegram login widget hash and create/update user.
    """
    # Verify Telegram hash
    hash_data = {
        "id": str(data.id),
        "first_name": data.first_name or "",
        "last_name": data.last_name or "",
        "username": data.username or "",
        "photo_url": data.photo_url or "",
        "auth_date": str(data.auth_date),
    }
    hash_data = {k: v for k, v in hash_data.items() if v}

    if not verify_telegram_hash(hash_data, data.hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram hash",
        )

    # Find or create user
    stmt = select(User).where(User.telegram_id == data.id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=data.id,
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            photo_url=data.photo_url,
            language="uk",
        )
        db.add(user)
        await db.flush()
    else:
        # Update user info
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.username = data.username
        user.photo_url = data.photo_url
        user.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    # Create JWT token
    access_token = create_access_token(data={"sub": user.id, "telegram_id": user.telegram_id})

    return AuthTokenResponse(
        access_token=access_token,
        user_id=user.id,
        telegram_id=user.telegram_id,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    token: str = None,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get current authenticated user info."""
    from app.api.deps import get_current_user

    user = await get_current_user(token, db)
    return UserResponse.from_attributes(user)


# --- WHOOP OAuth Callback (redirect_uri = /api/v1/auth/whoop/callback) ---

@router.get("/whoop/callback")
async def whoop_oauth_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle WHOOP OAuth callback — exchange code for tokens and sync data."""
    # Handle OAuth errors from WHOOP
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"WHOOP OAuth error: {error} - {error_description or 'Unknown error'}"
        )

    if not code or not state:
        raise HTTPException(
            status_code=400,
            detail="Missing code or state parameter from WHOOP OAuth"
        )

    try:
        # State format: "user_id_randomhex"
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

        # Do initial sync (30 days)
        try:
            await sync_whoop_data(user.id, token_data["access_token"], db, days_back=30)
        except Exception:
            pass  # Non-critical

        # Redirect to dashboard
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard?whoop=connected")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WHOOP connection failed: {str(e)}")
