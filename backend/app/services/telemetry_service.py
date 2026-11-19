from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from fastapi import HTTPException

from app.models.project import Project
from app.models.telemetry import TelemetryLog, TelemetryMetric, TelemetryTrace
from app.models.service_map import ServiceNode
from app.schemas.telemetry import (
    TelemetryLogCreate,
    TelemetryMetricCreate,
    TelemetryTraceCreate,
    TelemetryBatchIngest,
)

class TelemetryService:

    @staticmethod
    async def ingest_logs(
        db: AsyncSession,
        project_id: str,
        logs: List[TelemetryLogCreate],
    ) -> List[TelemetryLog]:
        # Validate project
        proj_stmt = select(Project).where(Project.id == project_id)
        proj = (await db.execute(proj_stmt)).scalars().first()
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")

        # If project receives runtime telemetry, mark mode as post_deployment
        if proj.deployment_mode != "post_deployment":
            proj.deployment_mode = "post_deployment"
            db.add(proj)

        created_logs: List[TelemetryLog] = []
        for item in logs:
            level = item.level.upper()
            stack_trace = item.stackTrace

            # Automatically extract stack trace from message if present
            message = item.message
            if not stack_trace and ("Traceback (most recent call last):" in message or "Exception:" in message):
                parts = message.split("Traceback (most recent call last):", 1)
                if len(parts) == 2:
                    message = parts[0].strip() or "Unhandled Exception"
                    stack_trace = "Traceback (most recent call last):" + parts[1]

            log_entry = TelemetryLog(
                project_id=project_id,
                service_name=item.serviceName,
                environment=item.environment,
                timestamp=item.timestamp or datetime.now(timezone.utc),
                level=level,
                message=message,
                stack_trace=stack_trace,
                logger_name=item.loggerName,
                attributes=item.attributes,
            )
            db.add(log_entry)
            created_logs.append(log_entry)

        await db.commit()
        for log in created_logs:
            await db.refresh(log)
        return created_logs

    @staticmethod
    async def ingest_metrics(
        db: AsyncSession,
        project_id: str,
        metrics: List[TelemetryMetricCreate],
    ) -> List[TelemetryMetric]:
        proj_stmt = select(Project).where(Project.id == project_id)
        proj = (await db.execute(proj_stmt)).scalars().first()
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")

        if proj.deployment_mode != "post_deployment":
            proj.deployment_mode = "post_deployment"
            db.add(proj)

        created_metrics: List[TelemetryMetric] = []
        for item in metrics:
            # Anomaly detection heuristic
            is_anomaly = False
            m_name = item.metricName.lower()
            val = item.value

            if "error_rate" in m_name and val > 0.05:  # > 5% error rate
                is_anomaly = True
            elif ("cpu" in m_name or "memory" in m_name) and val > 90.0:  # > 90% utilization
                is_anomaly = True
            elif "latency" in m_name and val > 1500.0:  # > 1500ms latency
                is_anomaly = True

            metric_entry = TelemetryMetric(
                project_id=project_id,
                service_name=item.serviceName,
                metric_name=item.metricName,
                value=item.value,
                unit=item.unit,
                labels=item.labels,
                timestamp=item.timestamp or datetime.now(timezone.utc),
                is_anomaly=is_anomaly,
            )
            db.add(metric_entry)
            created_metrics.append(metric_entry)

        await db.commit()
        for metric in created_metrics:
            await db.refresh(metric)
        return created_metrics

    @staticmethod
    async def ingest_traces(
        db: AsyncSession,
        project_id: str,
        traces: List[TelemetryTraceCreate],
    ) -> List[TelemetryTrace]:
        proj_stmt = select(Project).where(Project.id == project_id)
        proj = (await db.execute(proj_stmt)).scalars().first()
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")

        if proj.deployment_mode != "post_deployment":
            proj.deployment_mode = "post_deployment"
            db.add(proj)

        created_traces: List[TelemetryTrace] = []
        services_seen = set()

        for item in traces:
            services_seen.add(item.serviceName)
            trace_entry = TelemetryTrace(
                project_id=project_id,
                trace_id=item.traceId,
                span_id=item.spanId,
                parent_span_id=item.parentSpanId,
                service_name=item.serviceName,
                operation_name=item.operationName,
                start_time=item.startTime or datetime.now(timezone.utc),
                duration_ms=item.durationMs,
                status_code=item.statusCode.upper(),
                error_message=item.errorMessage,
                attributes=item.attributes,
            )
            db.add(trace_entry)
            created_traces.append(trace_entry)

        # Update or register discovered service nodes
        for s_name in services_seen:
            existing_node_stmt = select(ServiceNode).where(
                ServiceNode.project_id == project_id,
                ServiceNode.name == s_name,
            )
            existing_node = (await db.execute(existing_node_stmt)).scalars().first()
            if not existing_node:
                s_node = ServiceNode(
                    project_id=project_id,
                    name=s_name,
                    tier="backend",
                    status="healthy",
                    runtime="python",
                )
                db.add(s_node)

        await db.commit()
        for trace in created_traces:
            await db.refresh(trace)
        return created_traces

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        project_id: str,
        service_name: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 50,
    ) -> List[TelemetryLog]:
        stmt = select(TelemetryLog).where(TelemetryLog.project_id == project_id)
        if service_name:
            stmt = stmt.where(TelemetryLog.service_name == service_name)
        if level:
            stmt = stmt.where(TelemetryLog.level == level.upper())
        stmt = stmt.order_by(desc(TelemetryLog.timestamp)).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_metrics(
        db: AsyncSession,
        project_id: str,
        metric_name: Optional[str] = None,
        service_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[TelemetryMetric]:
        stmt = select(TelemetryMetric).where(TelemetryMetric.project_id == project_id)
        if metric_name:
            stmt = stmt.where(TelemetryMetric.metric_name == metric_name)
        if service_name:
            stmt = stmt.where(TelemetryMetric.service_name == service_name)
        stmt = stmt.order_by(desc(TelemetryMetric.timestamp)).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_traces(
        db: AsyncSession,
        project_id: str,
        service_name: Optional[str] = None,
        trace_id: Optional[str] = None,
        status_code: Optional[str] = None,
        limit: int = 50,
    ) -> List[TelemetryTrace]:
        stmt = select(TelemetryTrace).where(TelemetryTrace.project_id == project_id)
        if trace_id:
            stmt = stmt.where(TelemetryTrace.trace_id == trace_id)
        if service_name:
            stmt = stmt.where(TelemetryTrace.service_name == service_name)
        if status_code:
            stmt = stmt.where(TelemetryTrace.status_code == status_code.upper())
        stmt = stmt.order_by(desc(TelemetryTrace.start_time)).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())
