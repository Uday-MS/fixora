import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class Bug(Base):
    __tablename__ = "bugs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=False)
    line_start = Column(Integer, default=1)
    line_end = Column(Integer, default=1)
    category = Column(String(50), default="logical_error", nullable=False)
    severity = Column(String(50), default="medium", nullable=False)  # critical, high, medium, low
    confidence = Column(Float, default=0.9)
    root_cause = Column(Text, nullable=True)
    trigger_conditions = Column(JSON, nullable=True)  # List[str]
    evidence = Column(JSON, nullable=True)            # List[BugEvidence dict]
    suggested_fix = Column(Text, nullable=True)
    patch_id = Column(String(36), nullable=True)
    status = Column(String(50), default="detected", nullable=False)  # detected, investigating, patch_generated, patch_verified, resolved, dismissed
    source = Column(String(50), default="static_analyzer", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="bugs")
    repository = relationship("Repository", back_populates="bugs")
    patches = relationship("Patch", back_populates="bug", cascade="all, delete-orphan")
