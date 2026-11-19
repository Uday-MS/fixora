from datetime import datetime, timezone
from typing import Dict, Any
from app.orchestrator.state import AgentState

class TriageAgent:
    @staticmethod
    def run(state: AgentState) -> AgentState:
        """
        Triage Agent: Analyzes error message, stack trace, and telemetry/code context.
        Determines error category, assigns severity, and pinpoints affected service.
        Supports both pre-deployment static analysis and post-deployment telemetry.
        """
        error_ctx = state.get("error_context", {})
        message = (error_ctx.get("message", "") or "").lower()
        stack_trace = (error_ctx.get("stack_trace", "") or "").lower()
        service_name = error_ctx.get("service_name") or "payment-service"
        mode = state.get("operating_mode") or "post_deployment"

        combined_text = f"{message} {stack_trace}"

        # Category detection
        category = "runtime_exception"
        severity = "MEDIUM"

        if "connection pool" in combined_text or "pool exhausted" in combined_text or "database timeout" in combined_text:
            category = "database_connection_pool_exhaustion"
            severity = "CRITICAL"
        elif "timeout" in combined_text or "timed out" in combined_text or "deadline exceeded" in combined_text:
            category = "gateway_timeout"
            severity = "HIGH"
        elif "nullpointer" in combined_text or "none_type" in combined_text or "attributeerror" in combined_text:
            category = "null_reference"
            severity = "HIGH"
        elif "syntaxerror" in combined_text or "typeerror" in combined_text or "validation" in combined_text:
            category = "code_syntax_validation"
            severity = "HIGH" if mode == "pre_deployment" else "MEDIUM"
        elif "out of memory" in combined_text or "oom" in combined_text:
            category = "memory_saturation"
            severity = "CRITICAL"

        triage_output = {
            "errorCategory": category,
            "severity": severity,
            "affectedService": service_name,
            "operatingMode": mode,
            "detectionTimestamp": datetime.now(timezone.utc).isoformat(),
            "hasStackTrace": bool(error_ctx.get("stack_trace")),
            "triageSummary": f"Identified {severity} severity incident ({category}) impacting service '{service_name}'.",
        }

        stage_entry = {
            "stage": "triage",
            "agent": "TriageAgent",
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": triage_output["triageSummary"],
        }

        history = list(state.get("stage_history", []))
        history.append(stage_entry)

        return {
            **state,
            "current_stage": "triage",
            "triage_result": triage_output,
            "stage_history": history,
        }
