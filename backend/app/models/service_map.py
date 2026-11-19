import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class ServiceNode(Base):
    __tablename__ = "service_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=False)
    tier = Column(String(50), default="backend", nullable=False)  # frontend, backend, gateway, worker, database, cache
    status = Column(String(50), default="healthy", nullable=False)  # healthy, degraded, critical
    runtime = Column(String(50), default="python", nullable=False)
    dependencies = Column(JSON, nullable=True)  # list of dependency service names or ids
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="service_nodes")
