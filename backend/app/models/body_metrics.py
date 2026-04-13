from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BodyMetricsHistory(Base):
    __tablename__ = "body_metrics_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(20), default="manual")  # manual, whoop, apple_health

    user = relationship("User", back_populates="body_metrics_history")
