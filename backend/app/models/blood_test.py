from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.sql import func

from app.core.database import Base


class BloodTest(Base):
    __tablename__ = "blood_tests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    test_date = Column(Date, nullable=True)
    file_url = Column(Text, nullable=True)
    parsed_data = Column(Text, nullable=True)  # JSON of extracted biomarkers
    ai_insights = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Biomarker(Base):
    __tablename__ = "biomarkers"

    id = Column(Integer, primary_key=True)
    blood_test_id = Column(Integer, ForeignKey("blood_tests.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    reference_min = Column(Float, nullable=True)
    reference_max = Column(Float, nullable=True)
    status = Column(String(20), nullable=True)  # normal, low, high
