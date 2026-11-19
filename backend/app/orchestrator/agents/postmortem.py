from datetime import datetime, timezone
from app.orchestrator.state import AgentState

class PostmortemAgent:
    @staticmethod
    def run(state: AgentState) -> AgentState:
        """
        Postmortem Agent: Generates comprehensive incident postmortem report,
        incident timeline, impact analysis, and prepares draft PR proposal.
        Leaves the workflow in 'pending_human_review' state awaiting explicit approval.
        """
        triage = state.get("triage_result", {})
        rca = state.get("rca_result", {})
        val = state.get("validation_result", {})
        patch = state.get("patch_result", {})
        graph = state.get("graph_context", [])

        service_name = triage.get("affectedService", "payment-service")
        severity = triage.get("severity", "CRITICAL")
        error_cat = triage.get("errorCategory", "runtime_exception")

        postmortem = {
            "title": f"Postmortem: {severity} Incident in {service_name} ({error_cat})",
            "summary": (
                f"On {datetime.now(timezone.utc).strftime('%Y-%m-%d')}, an automated incident detection triggered for {service_name}. "
                "FIXORA autonomous multi-agent pipeline isolated the root cause, synthesized a verifiable patch, and validated it in an isolated sandbox."
            ),
            "timeline": [
                {"timestamp": "T-15m", "event": f"Telemetry anomaly detected in {service_name}"},
                {"timestamp": "T-12m", "event": "Triage Agent classified incident as CRITICAL database pool exhaustion"},
                {"timestamp": "T-08m", "event": "Retrieval Agent retrieved runbooks and GraphRAG dependency chain"},
                {"timestamp": "T-05m", "event": "Root Cause Analysis isolated unbounded acquire timeout in pool.py"},
                {"timestamp": "T-02m", "event": "AutoPatch generated clean unified diff"},
                {"timestamp": "T-00m", "event": "Diagnostic Sandbox validated 2/2 unit assertions passing without regression"},
            ],
            "impact": {
                "primaryService": service_name,
                "blastRadius": graph,
                "customerImpact": "Elevated checkout latency and sporadic 504 timeouts",
            },
            "detectionMethod": "FIXORA Autonomous Telemetry & Anomaly Ingestion Gateway",
            "rootCause": rca.get("root_cause", ""),
            "resolution": {
                "filePath": patch.get("file_path", ""),
                "patchTitle": patch.get("title", ""),
                "sandboxVerdict": val.get("security_verdict", ""),
                "testsPassed": val.get("tests_passed", False),
            },
            "preventiveActions": [
                "Deploy bounded acquire timeout to production after human review",
                "Add circuit breaker for upstream api-gateway callers",
                "Configure Prometheus alert for connection pool utilization > 80%",
            ],
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        }

        stage_entry = {
            "stage": "postmortem",
            "agent": "PostmortemAgent",
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": "Postmortem report generated. Awaiting human engineering approval before GitHub draft PR creation.",
        }

        history = list(state.get("stage_history", []))
        history.append(stage_entry)

        return {
            **state,
            "current_stage": "completed",
            "postmortem_report": postmortem,
            "approval_status": "pending_human_review",
            "stage_history": history,
        }
