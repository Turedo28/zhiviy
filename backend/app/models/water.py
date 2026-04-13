from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Time
from sqlalchemy.sql import func

from app.core.database import Base


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount_ml = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Supplement(Base):
    __tablename__ = "supplements"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=True)
    reminder_time = Column(Time, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SupplementLog(Base):
    __tablename__ = "supplement_logs"

    id = Column(Integer, primary_key=True)
    supplement_id = Column(Integer, ForeignKey("supplements.id"), nullable=False, index=True)
    taken_at = Column(DateTime(timezone=True), server_default=func.now())
