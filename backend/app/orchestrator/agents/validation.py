from datetime import datetime, timezone
from app.orchestrator.state import AgentState
from app.orchestrator.sandbox.runner import sandbox_runner

class ValidationAgent:
    @staticmethod
    def run(state: AgentState) -> AgentState:
        """
        Validation Agent: Executes proposed patch in the isolated Docker/ephemeral sandbox.
        Validates syntax, executes unit tests, checks for regressions, and records execution output.
        Never marks a patch as successful if validation fails.
        """
        patch_res = state.get("patch_result", {})
        file_path = patch_res.get("file_path", "src/application/handler.py")
        proposed_code = patch_res.get("proposed_code", "")
        original_code = patch_res.get("original_code", "")

        is_pool_case = (
            "pool" in file_path.lower()
            and "ConnectionTimeoutError" in proposed_code
        )

        if is_pool_case:
            test_code = """
import unittest
import time
from pool import ConnectionPool, ConnectionTimeoutError

class TestPoolRepair(unittest.TestCase):
    def test_acquire_and_release(self):
        pool = ConnectionPool(max_connections=2, acquire_timeout_seconds=0.1)
        c1 = pool.acquire()
        c2 = pool.acquire()
        self.assertEqual(pool.active_connections, 2)
        pool.release(c1)
        self.assertEqual(pool.active_connections, 1)

    def test_timeout_raised_under_saturation(self):
        pool = ConnectionPool(max_connections=1, acquire_timeout_seconds=0.05)
        c1 = pool.acquire()
        with self.assertRaises(ConnectionTimeoutError):
            pool.acquire(timeout=0.05)
        pool.release(c1)

if __name__ == '__main__':
    unittest.main()
"""
        else:
            test_code = None

        validation_res = sandbox_runner.execute_validation(
            file_path="pool.py" if is_pool_case else (file_path or "repair.py"),
            original_code=original_code,
            proposed_code=proposed_code,
            test_code=test_code,
            test_command="python -m unittest",
        )

        stage_status = "completed" if validation_res.get("tests_passed") else "failed"
        passed_cnt = validation_res.get("passed_tests", 0)
        total_cnt = validation_res.get("total_tests", 1)

        stage_entry = {
            "stage": "validation",
            "agent": "ValidationAgent",
            "status": stage_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": f"Sandbox validation {stage_status}: {passed_cnt}/{total_cnt} tests passed in {validation_res.get('duration_seconds')}s.",
        }

        history = list(state.get("stage_history", []))
        history.append(stage_entry)

        return {
            **state,
            "current_stage": "validation",
            "validation_result": validation_res,
            "stage_history": history,
        }
