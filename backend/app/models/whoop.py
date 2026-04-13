from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class WhoopToken(Base):
    __tablename__ = "whoop_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_type = Column(String(50), default="Bearer")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    scope = Column(Text, nullable=True)
    whoop_user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="whoop_token")


class WhoopSleep(Base):
    __tablename__ = "whoop_sleep"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    whoop_id = Column(String(100), unique=True, nullable=True)

    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    score = Column(Float, nullable=True)
    quality_duration_ms = Column(BigInteger, nullable=True)
    rem_duration_ms = Column(BigInteger, nullable=True)
    light_duration_ms = Column(BigInteger, nullable=True)
    deep_duration_ms = Column(BigInteger, nullable=True)
    wake_duration_ms = Column(BigInteger, nullable=True)
    efficiency = Column(Float, nullable=True)

    raw_data = Column(Text, nullable=True)  # Full JSON from WHOOP
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WhoopRecovery(Base):
    __tablename__ = "whoop_recovery"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    whoop_cycle_id = Column(BigInteger, unique=True, nullable=True)

    score = Column(Float, nullable=True)
    hrv_rmssd = Column(Float, nullable=True)
    resting_heart_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    skin_temp = Column(Float, nullable=True)

    raw_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WhoopWorkout(Base):
    __tablename__ = "whoop_workouts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    whoop_id = Column(String(100), unique=True, nullable=True)

    sport_id = Column(Integer, nullable=True)
    sport_name = Column(String(255), nullable=True)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    strain = Column(Float, nullable=True)
    average_hr = Column(Float, nullable=True)
    max_hr = Column(Float, nullable=True)
    calories = Column(Float, nullable=True)

    raw_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
