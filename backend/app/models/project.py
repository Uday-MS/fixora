import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False)  # active, archived
    deployment_mode = Column(String(50), default="pre_deployment", nullable=False)  # pre_deployment, post_deployment
    health_score = Column(String(10), default="95", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    workspace = relationship("Workspace", back_populates="projects")
    repositories = relationship("Repository", back_populates="project", cascade="all, delete-orphan")
    bugs = relationship("Bug", back_populates="project", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="project", cascade="all, delete-orphan")
    investigations = relationship("Investigation", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("KnowledgeDocument", back_populates="project", cascade="all, delete-orphan")
    ingestion_jobs = relationship("IngestionJob", back_populates="project", cascade="all, delete-orphan")
    telemetry_logs = relationship("TelemetryLog", back_populates="project", cascade="all, delete-orphan")
    telemetry_metrics = relationship("TelemetryMetric", back_populates="project", cascade="all, delete-orphan")
    telemetry_traces = relationship("TelemetryTrace", back_populates="project", cascade="all, delete-orphan")
    service_nodes = relationship("ServiceNode", back_populates="project", cascade="all, delete-orphan")
