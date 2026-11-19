from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.telemetry_service import TelemetryService
from app.schemas.telemetry import (
    TelemetryLogCreate,
    TelemetryLogResponse,
    TelemetryMetricCreate,
    TelemetryMetricResponse,
    TelemetryTraceCreate,
    TelemetryTraceResponse,
    TelemetryBatchIngest,
)

router = APIRouter()

# --- LOGS ---

@router.post("/telemetry/{project_id}/logs", response_model=List[TelemetryLogResponse])
async def ingest_logs(
    project_id: str,
    payload: List[TelemetryLogCreate],
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest application logs, extract stack traces, normalize timestamps,
    and associate with services.
    """
    logs = await TelemetryService.ingest_logs(db=db, project_id=project_id, logs=payload)
    return [
        TelemetryLogResponse(
            id=l.id,
            projectId=l.project_id,
            serviceName=l.service_name,
            environment=l.environment,
            timestamp=l.timestamp,
            level=l.level,
            message=l.message,
            stackTrace=l.stack_trace,
            loggerName=l.logger_name,
            attributes=l.attributes,
        )
        for l in logs
    ]

@router.get("/telemetry/{project_id}/logs", response_model=List[TelemetryLogResponse])
async def query_logs(
    project_id: str,
    serviceName: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Query telemetry logs filtered by service and log level.
    """
    logs = await TelemetryService.get_logs(
        db=db,
        project_id=project_id,
        service_name=serviceName,
        level=level,
        limit=limit,
    )
    return [
        TelemetryLogResponse(
            id=l.id,
            projectId=l.project_id,
            serviceName=l.service_name,
            environment=l.environment,
            timestamp=l.timestamp,
            level=l.level,
            message=l.message,
            stackTrace=l.stack_trace,
            loggerName=l.logger_name,
            attributes=l.attributes,
        )
        for l in logs
    ]

# --- METRICS ---

@router.post("/telemetry/{project_id}/metrics", response_model=List[TelemetryMetricResponse])
async def ingest_metrics(
    project_id: str,
    payload: List[TelemetryMetricCreate],
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest timeseries metrics and automatically detect anomalies (e.g. error rate spikes, latency).
    """
    metrics = await TelemetryService.ingest_metrics(db=db, project_id=project_id, metrics=payload)
    return [
        TelemetryMetricResponse(
            id=m.id,
            projectId=m.project_id,
            serviceName=m.service_name,
            metricName=m.metric_name,
            value=m.value,
            unit=m.unit,
            labels=m.labels,
            timestamp=m.timestamp,
            isAnomaly=m.is_anomaly,
        )
        for m in metrics
    ]

@router.get("/telemetry/{project_id}/metrics", response_model=List[TelemetryMetricResponse])
async def query_metrics(
    project_id: str,
    metricName: Optional[str] = Query(None),
    serviceName: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Query time-series metric data points.
    """
    metrics = await TelemetryService.get_metrics(
        db=db,
        project_id=project_id,
        metric_name=metricName,
        service_name=serviceName,
        limit=limit,
    )
    return [
        TelemetryMetricResponse(
            id=m.id,
            projectId=m.project_id,
            serviceName=m.service_name,
            metricName=m.metric_name,
            value=m.value,
            unit=m.unit,
            labels=m.labels,
            timestamp=m.timestamp,
            isAnomaly=m.is_anomaly,
        )
        for m in metrics
    ]

# --- TRACES ---

@router.post("/telemetry/{project_id}/traces", response_model=List[TelemetryTraceResponse])
async def ingest_traces(
    project_id: str,
    payload: List[TelemetryTraceCreate],
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest OpenTelemetry-compatible distributed trace spans and map service dependencies.
    """
    traces = await TelemetryService.ingest_traces(db=db, project_id=project_id, traces=payload)
    return [
        TelemetryTraceResponse(
            id=t.id,
            projectId=t.project_id,
            traceId=t.trace_id,
            spanId=t.span_id,
            parentSpanId=t.parent_span_id,
            serviceName=t.service_name,
            operationName=t.operation_name,
            startTime=t.start_time,
            durationMs=t.duration_ms,
            statusCode=t.status_code,
            errorMessage=t.error_message,
            attributes=t.attributes,
        )
        for t in traces
    ]

@router.get("/telemetry/{project_id}/traces", response_model=List[TelemetryTraceResponse])
async def query_traces(
    project_id: str,
    serviceName: Optional[str] = Query(None),
    traceId: Optional[str] = Query(None),
    statusCode: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Query distributed trace spans.
    """
    traces = await TelemetryService.get_traces(
        db=db,
        project_id=project_id,
        service_name=serviceName,
        trace_id=traceId,
        status_code=statusCode,
        limit=limit,
    )
    return [
        TelemetryTraceResponse(
            id=t.id,
            projectId=t.project_id,
            traceId=t.trace_id,
            spanId=t.span_id,
            parentSpanId=t.parent_span_id,
            serviceName=t.service_name,
            operationName=t.operation_name,
            startTime=t.start_time,
            durationMs=t.duration_ms,
            statusCode=t.status_code,
            errorMessage=t.error_message,
            attributes=t.attributes,
        )
        for t in traces
    ]

# --- BATCH ---

@router.post("/telemetry/{project_id}/batch")
async def batch_ingest(
    project_id: str,
    payload: TelemetryBatchIngest,
    db: AsyncSession = Depends(get_db),
):
    """
    Unified batch ingestion for telemetry logs, metrics, and traces.
    """
    res = {}
    if payload.logs:
        logs = await TelemetryService.ingest_logs(db=db, project_id=project_id, logs=payload.logs)
        res["logsIngested"] = len(logs)
    if payload.metrics:
        metrics = await TelemetryService.ingest_metrics(db=db, project_id=project_id, metrics=payload.metrics)
        res["metricsIngested"] = len(metrics)
    if payload.traces:
        traces = await TelemetryService.ingest_traces(db=db, project_id=project_id, traces=payload.traces)
        res["tracesIngested"] = len(traces)
    return {"status": "success", "counts": res}
