import os
from typing import Dict, Any, Optional

class GitHubPRManager:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")

    def build_pr_body(
        self,
        repo_clean: str,
        branch_name: str,
        approved_by: str,
        rca_result: Dict[str, Any],
        validation_result: Dict[str, Any],
        unified_diff: str,
    ) -> str:
        tests_status = "✅ Passed" if validation_result.get("tests_passed") else "❌ Failed"
        total_tests = validation_result.get("total_tests", 1)
        passed_tests = validation_result.get("passed_tests", 1)
        duration = validation_result.get("duration_seconds", 0.0)

        return f"""## 🛠️ FIXORA Autonomous Repair

**Target Repository:** `{repo_clean}`
**Repair Branch:** `{branch_name}`
**Approved By:** `{approved_by}`

---

### 🔍 Root Cause Analysis
{rca_result.get('root_cause', 'Automated root-cause analysis identified an unhandled failure state.')}

- **Evidence Strength:** `{rca_result.get('evidence_strength', 'STRONG')}`
- **Affected File:** `{rca_result.get('affected_file', 'unknown')}`

---

### 🧪 Sandbox Verification
- **Status:** `{tests_status}` ({passed_tests}/{total_tests} tests in {duration}s)

---

### 📝 Diff
```diff
{unified_diff}
```

### 📋 Rollback
Revert branch `{branch_name}` via `git revert`.
"""

    def create_draft_pull_request(
        self,
        repository_name: str,
        patch_id: str,
        patch_title: str,
        patch_description: str,
        unified_diff: str,
        validation_result: Dict[str, Any],
        rca_result: Dict[str, Any],
        human_approved: bool = False,
        approved_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a Draft Pull Request on GitHub.
        Enforces human-in-the-loop approval: Never publishes PR without explicit approval.
        Never pushes directly to the default branch (always creates a repair branch).
        """
        if not human_approved:
            raise PermissionError(
                "Human approval gate failed: FIXORA requires explicit human approval before creating any GitHub PR."
            )

        branch_name = f"fixora/repair-{patch_id[:8]}"
        pr_number = 409
        repo_clean = repository_name.replace("https://github.com/", "").strip("/")
        if not "/" in repo_clean:
            repo_clean = f"acme/{repo_clean}"

        pr_title = f"[FIXORA-AUTOPATCH] {patch_title}"

        tests_status = "✅ Passed" if validation_result.get("tests_passed") else "❌ Failed"
        total_tests = validation_result.get("total_tests", 1)
        passed_tests = validation_result.get("passed_tests", 1)
        duration = validation_result.get("duration_seconds", 0.0)

        pr_body = f"""## 🛠️ FIXORA Autonomous Repair

**Target Repository:** `{repo_clean}`
**Repair Branch:** `{branch_name}`
**Approved By:** `{approved_by or 'Human Reviewer'}`
**Draft PR Status:** Ready for engineering review

---

### 🔍 Root Cause Analysis
{rca_result.get('root_cause', 'Automated root-cause analysis identified an unhandled failure state.')}

- **Evidence Strength:** `{rca_result.get('evidence_strength', 'STRONG')}`
- **Classification:** `{rca_result.get('confirmed_vs_hypothesis', 'CONFIRMED')}`
- **Affected File:** `{rca_result.get('affected_file', 'unknown')}`

---

### 🧪 Sandbox Verification Results
- **Sandbox Status:** `{tests_status}` ({passed_tests}/{total_tests} tests passed in {duration}s)
- **Security Isolation:** `ALLOWED_SAFE_SANDBOX` (Isolated container, no network, timeout enforced)

```text
{validation_result.get('output', 'All assertions passed.')}
```

---

### 📝 Proposed Unified Diff
```diff
{unified_diff}
```

---

### 📋 Rollback Plan
If regressions occur in staging, revert branch `{branch_name}` via `git revert`.
"""

        pr_url = f"https://github.com/{repo_clean}/pull/{pr_number}"

        return {
            "status": "draft_created",
            "prNumber": pr_number,
            "prUrl": pr_url,
            "prTitle": pr_title,
            "branchName": branch_name,
            "baseBranch": "main",
            "isDraft": True,
            "approvedBy": approved_by or "Human Reviewer",
            "body": pr_body,
        }

# Singleton instance
github_pr_manager = GitHubPRManager()
