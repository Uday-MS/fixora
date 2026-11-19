import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patch_id = Column(String(36), ForeignKey("patches.id", ondelete="CASCADE"), nullable=False, index=True)
    command = Column(String(255), nullable=False)
    status = Column(String(50), default="queued", nullable=False)  # queued, running, passed, failed, error
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    output = Column(Text, default="")
    duration = Column(Float, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    patch = relationship("Patch", back_populates="test_runs")
