from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict, total=False):
    # Identifiers
    investigation_id: str
    project_id: str
    repository_id: Optional[str]
    incident_id: Optional[str]
    bug_id: Optional[str]
    patch_id: Optional[str]

    # Input Error & Mode Context
    error_context: Dict[str, Any]
    operating_mode: str  # pre_deployment, post_deployment

    # Node Output Payloads
    triage_result: Dict[str, Any]
    retrieved_evidence: List[Dict[str, Any]]
    graph_context: List[str]
    rca_result: Dict[str, Any]
    diagnostic_result: Dict[str, Any]
    patch_result: Dict[str, Any]
    validation_result: Dict[str, Any]
    postmortem_report: Dict[str, Any]

    # Human Gate & GitHub Draft PR
    approval_status: str  # pending_human_review, approved, rejected
    draft_pr: Optional[Dict[str, Any]]

    # Audit & Stage Progress
    current_stage: str
    stage_history: List[Dict[str, Any]]
    errors: List[str]
