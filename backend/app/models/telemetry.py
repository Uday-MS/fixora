import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    service_name = Column(String(100), nullable=False, index=True)
    environment = Column(String(50), default="production", nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    level = Column(String(20), default="INFO", nullable=False)  # INFO, WARN, ERROR, FATAL, DEBUG
    message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    logger_name = Column(String(100), nullable=True)
    attributes = Column(JSON, nullable=True)

    project = relationship("Project", back_populates="telemetry_logs")


class TelemetryMetric(Base):
    __tablename__ = "telemetry_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    service_name = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50), default="count", nullable=False)
    labels = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    is_anomaly = Column(Boolean, default=False, nullable=False)

    project = relationship("Project", back_populates="telemetry_metrics")


class TelemetryTrace(Base):
    __tablename__ = "telemetry_traces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    trace_id = Column(String(64), nullable=False, index=True)
    span_id = Column(String(64), nullable=False, index=True)
    parent_span_id = Column(String(64), nullable=True)
    service_name = Column(String(100), nullable=False, index=True)
    operation_name = Column(String(255), nullable=False)
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    duration_ms = Column(Float, default=0.0, nullable=False)
    status_code = Column(String(20), default="OK", nullable=False)  # OK, ERROR, UNSET
    error_message = Column(Text, nullable=True)
    attributes = Column(JSON, nullable=True)

    project = relationship("Project", back_populates="telemetry_traces")
