from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, BigInteger, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    photo_url = Column(Text, nullable=True)
    language = Column(String(2), default="uk")  # uk or en

    # Onboarding
    onboarding_completed = Column(Boolean, default=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)  # male, female, other

    # Body metrics
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    activity_level = Column(String(20), nullable=True)  # sedentary, light, moderate, active, very_active
    goal = Column(String(20), nullable=True)  # lose, maintain, gain

    # Settings
    water_tracking_enabled = Column(Boolean, default=False)
    supplements_tracking_enabled = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")
    whoop_token = relationship("WhoopToken", back_populates="user", uselist=False, cascade="all, delete-orphan")
    body_metrics_history = relationship("BodyMetricsHistory", back_populates="user", cascade="all, delete-orphan")
    water_logs = relationship("WaterLog", cascade="all, delete-orphan")
    supplements = relationship("Supplement", cascade="all, delete-orphan")
    blood_tests = relationship("BloodTest", cascade="all, delete-orphan")
    weekly_reports = relationship("WeeklyReport", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", cascade="all, delete-orphan")
