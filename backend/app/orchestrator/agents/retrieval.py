from datetime import datetime, timezone
from app.orchestrator.state import AgentState
from app.rag.rag_engine import rag_engine
from app.rag.graph_rag import graph_rag

class RetrievalAgent:
    @staticmethod
    def run(state: AgentState) -> AgentState:
        """
        Retrieval Agent: Retrieves relevant runbooks, code implementations,
        historical incidents, and service dependency graphs.
        """
        triage = state.get("triage_result", {})
        error_ctx = state.get("error_context", {})
        service_name = triage.get("affectedService") or state.get("repository_id") or "application"
        category = triage.get("errorCategory", "")
        message = error_ctx.get("message", "")
        project_id = state.get("project_id", "proj_demo_001")

        search_query = f"{service_name} {category.replace('_', ' ')} {message}"

        # Hybrid retrieval + Cross-encoder rerank
        retrieved_chunks = rag_engine.search(
            query=search_query,
            project_id=project_id,
            mode="hybrid_rerank",
            top_k=4,
        )

        # GraphRAG topology context
        deps = graph_rag.get_service_dependencies(service_name)
        incident_id = state.get("incident_id") or "inc_active"
        blast_radius = graph_rag.get_incident_blast_radius(incident_id)

        graph_context = []
        if deps["downstreamDependencies"]:
            graph_context.append(f"Service '{service_name}' depends on: {', '.join(deps['downstreamDependencies'])}")
        if deps["upstreamCallers"]:
            graph_context.append(f"Upstream callers impacted: {', '.join(deps['upstreamCallers'])}")
        if blast_radius["linkedCommits"]:
            graph_context.append(f"Linked suspicious commits: {', '.join(blast_radius['linkedCommits'])}")

        stage_entry = {
            "stage": "retrieval",
            "agent": "RetrievalAgent",
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": f"Retrieved {len(retrieved_chunks)} relevant knowledge chunks and {len(graph_context)} GraphRAG architectural dependencies.",
        }

        history = list(state.get("stage_history", []))
        history.append(stage_entry)

        return {
            **state,
            "current_stage": "retrieval",
            "retrieved_evidence": retrieved_chunks,
            "graph_context": graph_context,
            "stage_history": history,
        }
