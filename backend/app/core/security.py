import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_telegram_hash(data: dict, hash_value: str) -> bool:
    """
    Verify Telegram login widget hash.

    Telegram sends: id, first_name, last_name, username, photo_url, auth_date, hash
    We need to verify hash using HMAC-SHA256 with bot token.
    """
    # Create data check string
    data_check_list = sorted([f"{k}={v}" for k, v in data.items() if k != "hash"])
    data_check_string = "\n".join(data_check_list)

    # Create secret key
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()

    # Calculate hash
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # Verify hash and check auth_date (max 5 minutes old)
    if calculated_hash != hash_value:
        return False

    auth_date = int(data.get("auth_date", 0))
    current_time = int(datetime.now(timezone.utc).timestamp())

    # Auth data must be within 5 minutes
    if current_time - auth_date > 300:
        return False

    return True


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=30)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
