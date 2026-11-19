from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from app.schemas.base import CamelModel

class TelemetryLogCreate(CamelModel):
    serviceName: str
    level: str = "INFO"  # INFO, WARN, ERROR, FATAL, DEBUG
    message: str
    environment: str = "production"
    timestamp: Optional[datetime] = None
    stackTrace: Optional[str] = None
    loggerName: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class TelemetryLogResponse(CamelModel):
    id: str
    projectId: str
    serviceName: str
    environment: str
    timestamp: datetime
    level: str
    message: str
    stackTrace: Optional[str] = None
    loggerName: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class TelemetryMetricCreate(CamelModel):
    serviceName: str
    metricName: str
    value: float
    unit: str = "count"
    labels: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

class TelemetryMetricResponse(CamelModel):
    id: str
    projectId: str
    serviceName: str
    metricName: str
    value: float
    unit: str
    labels: Optional[Dict[str, Any]] = None
    timestamp: datetime
    isAnomaly: bool

class TelemetryTraceCreate(CamelModel):
    traceId: str
    spanId: str
    parentSpanId: Optional[str] = None
    serviceName: str
    operationName: str
    startTime: Optional[datetime] = None
    durationMs: float = 0.0
    statusCode: str = "OK"  # OK, ERROR, UNSET
    errorMessage: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class TelemetryTraceResponse(CamelModel):
    id: str
    projectId: str
    traceId: str
    spanId: str
    parentSpanId: Optional[str] = None
    serviceName: str
    operationName: str
    startTime: datetime
    durationMs: float
    statusCode: str
    errorMessage: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class TelemetryBatchIngest(CamelModel):
    logs: Optional[List[TelemetryLogCreate]] = None
    metrics: Optional[List[TelemetryMetricCreate]] = None
    traces: Optional[List[TelemetryTraceCreate]] = None
