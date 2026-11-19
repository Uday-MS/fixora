import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON
from app.db.session import Base

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)  # github, opentelemetry, prometheus, qdrant, sentry
    status = Column(String(50), default="connected", nullable=False)
    config_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
