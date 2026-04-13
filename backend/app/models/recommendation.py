from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Boolean, Text
from sqlalchemy.sql import func

from app.core.database import Base


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)
    content = Column(Text, nullable=False)  # JSON or Markdown
    sent_via_telegram = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # sleep, nutrition, recovery, training
    content = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, sent, read, dismissed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
