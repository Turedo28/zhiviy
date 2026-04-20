from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    photo_url = Column(Text, nullable=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    calories = Column(Float, nullable=False)
    protein_g = Column(Float, default=0)
    carbs_g = Column(Float, default=0)
    fats_g = Column(Float, default=0)
    fiber_g = Column(Float, default=0)
    weight_g = Column(Float, nullable=True)
    confidence = Column(String(10), default="medium")

    source = Column(String(10), default="telegram")  # telegram or web
    ai_raw_response = Column(Text, nullable=True)  # Store Claude's full response for debugging

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="meals")
