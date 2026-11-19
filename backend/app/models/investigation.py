import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    bug_id = Column(String(36), nullable=True)
    incident_id = Column(String(36), nullable=True)
    question = Column(Text, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, in_progress, completed, failed
    current_stage = Column(String(50), default="triage", nullable=False)  # triage, retrieval, root_cause, patch, validation, report
    stages = Column(JSON, nullable=True)  # List of stage details
    findings = Column(Text, nullable=True)
    root_cause_hypothesis = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    patch_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="investigations")
