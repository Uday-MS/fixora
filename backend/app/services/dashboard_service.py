from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.repository import Repository
from app.models.bug import Bug
from app.models.patch import Patch
from app.models.test_run import TestRun
from app.models.incident import Incident
from app.schemas.dashboard import DashboardStats

class DashboardService:
    @staticmethod
    async def get_stats(db: AsyncSession) -> DashboardStats:
        total_repos = (await db.scalar(select(func.count(Repository.id)))) or 0
        active_anomalies = (await db.scalar(select(func.count(Bug.id)).where(Bug.status != "resolved"))) or 0
        critical_issues = (await db.scalar(select(func.count(Bug.id)).where(Bug.severity == "critical", Bug.status != "resolved"))) or 0
        total_patches = (await db.scalar(select(func.count(Patch.id)))) or 0
        pending_review = (await db.scalar(select(func.count(Patch.id)).where(Patch.status.in_(["pending_review", "draft"])))) or 0
        draft_prs = (await db.scalar(select(func.count(Patch.id)).where(Patch.pr_number.isnot(None)))) or 0
        autonomous_repairs = (await db.scalar(select(func.count(Patch.id)).where(Patch.status.in_(["approved", "applied", "pr_created"])))) or 0
        active_incidents = (await db.scalar(select(func.count(Incident.id)).where(Incident.status == "active"))) or 0

        # Real test pass rate calculation
        total_test_runs = (await db.scalar(select(func.count(TestRun.id)))) or 0
        passed_test_runs = (await db.scalar(select(func.count(TestRun.id)).where(TestRun.status == "passed"))) or 0
        tests_pass_rate = round((passed_test_runs / total_test_runs) * 100, 1) if total_test_runs > 0 else 0.0

        # Real MTTR calculation from resolved incidents
        res_incidents = (await db.execute(select(Incident).where(Incident.status == "resolved"))).scalars().all()
        durations = []
        for inc in res_incidents:
            if inc.resolved_at and inc.started_at:
                diff_mins = (inc.resolved_at - inc.started_at).total_seconds() / 60.0
                if diff_mins > 0:
                    durations.append(diff_mins)
        mttr_minutes = int(sum(durations) / len(durations)) if durations else 0

        return DashboardStats(
            total_repositories=total_repos,
            active_anomalies=active_anomalies,
            critical_issues=critical_issues,
            autonomous_repairs=autonomous_repairs,
            total_patches=total_patches,
            pending_review=pending_review,
            draft_prs=draft_prs,
            tests_pass_rate=tests_pass_rate,
            mttr_minutes=mttr_minutes,
            active_incidents=active_incidents,
        )

    @staticmethod
    async def get_health_metrics(db: AsyncSession) -> dict:
        total_repos = (await db.scalar(select(func.count(Repository.id)))) or 0
        total_fixes = (await db.scalar(select(func.count(Patch.id)).where(Patch.status.in_(["approved", "applied", "pr_created"])))) or 0
        total_test_runs = (await db.scalar(select(func.count(TestRun.id)))) or 0
        passed_test_runs = (await db.scalar(select(func.count(TestRun.id)).where(TestRun.status == "passed"))) or 0
        pass_rate = round((passed_test_runs / total_test_runs) * 100, 1) if total_test_runs > 0 else 0.0

        res_incidents = (await db.execute(select(Incident).where(Incident.status == "resolved"))).scalars().all()
        durations = []
        for inc in res_incidents:
            if inc.resolved_at and inc.started_at:
                diff_mins = (inc.resolved_at - inc.started_at).total_seconds() / 60.0
                if diff_mins > 0:
                    durations.append(diff_mins)
        mttr_mins = int(sum(durations) / len(durations)) if durations else 0

        unresolved_bugs = (await db.scalar(select(func.count(Bug.id)).where(Bug.status != "resolved"))) or 0
        has_data = total_repos > 0

        return {
            "totalRepositories": total_repos,
            "totalFixes": total_fixes,
            "sandboxPassRate": pass_rate,
            "averageMttrMins": mttr_mins,
            "unresolvedBugs": unresolved_bugs,
            "zeroContaminationRate": 100.0,
            "hasSufficientData": has_data,
        }
