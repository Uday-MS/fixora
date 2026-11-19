import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), default="sev2", nullable=False)  # sev1, sev2, sev3, sev4
    status = Column(String(50), default="active", nullable=False)    # active, investigating, mitigated, resolved, postmortem
    affected_service = Column(String(255), nullable=False)
    error_message = Column(Text, nullable=True)
    related_commits = Column(JSON, nullable=True)  # List[str]
    related_bug_ids = Column(JSON, nullable=True)  # List[str]
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="incidents")
