import uuid
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END

from app.orchestrator.state import AgentState
from app.orchestrator.agents.triage import TriageAgent
from app.orchestrator.agents.retrieval import RetrievalAgent
from app.orchestrator.agents.rca import RootCauseAnalysisAgent
from app.orchestrator.agents.diagnostic import DiagnosticAgent
from app.orchestrator.agents.autopatch import AutoPatchAgent
from app.orchestrator.agents.validation import ValidationAgent
from app.orchestrator.agents.postmortem import PostmortemAgent

def create_incident_orchestration_graph():
    """
    Builds and compiles FIXORA's 7-agent stateful incident repair graph using LangGraph.
    """
    workflow = StateGraph(AgentState)

    # Register multi-agent nodes
    workflow.add_node("triage", TriageAgent.run)
    workflow.add_node("retrieval", RetrievalAgent.run)
    workflow.add_node("rca", RootCauseAnalysisAgent.run)
    workflow.add_node("diagnostic", DiagnosticAgent.run)
    workflow.add_node("autopatch", AutoPatchAgent.run)
    workflow.add_node("validation", ValidationAgent.run)
    workflow.add_node("postmortem", PostmortemAgent.run)

    # Establish linear and deterministic agent workflow edges
    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "retrieval")
    workflow.add_edge("retrieval", "rca")
    workflow.add_edge("rca", "diagnostic")
    workflow.add_edge("diagnostic", "autopatch")
    workflow.add_edge("autopatch", "validation")
    workflow.add_edge("validation", "postmortem")
    workflow.add_edge("postmortem", END)

    return workflow.compile()

# Pre-compiled application graph
incident_orchestrator = create_incident_orchestration_graph()

async def run_incident_investigation(
    error_context: Dict[str, Any],
    project_id: str = "proj_demo_001",
    repository_id: Optional[str] = None,
    incident_id: Optional[str] = None,
    operating_mode: str = "post_deployment",
) -> AgentState:
    """
    Executes the complete multi-agent investigation and autopatch lifecycle.
    """
    investigation_id = f"inv_{uuid.uuid4().hex[:8]}"
    inc_id = incident_id or f"inc_{uuid.uuid4().hex[:8]}"

    initial_state: AgentState = {
        "investigation_id": investigation_id,
        "project_id": project_id,
        "repository_id": repository_id,
        "incident_id": inc_id,
        "error_context": error_context,
        "operating_mode": operating_mode,
        "stage_history": [],
        "errors": [],
    }

    final_state = incident_orchestrator.invoke(initial_state)
    return final_state
