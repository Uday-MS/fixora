from app.schemas.base import CamelModel

class DashboardStats(CamelModel):
    total_repositories: int = 12
    active_anomalies: int = 46
    critical_issues: int = 8
    autonomous_repairs: int = 38
    total_patches: int = 41
    pending_review: int = 8
    draft_prs: int = 4
    tests_pass_rate: float = 92.7
    mttr_minutes: int = 18
    active_incidents: int = 3
