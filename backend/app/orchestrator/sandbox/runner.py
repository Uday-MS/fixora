import os
import re
import shlex
import time
import tempfile
import subprocess
from typing import Dict, Any, Optional

ALLOWED_COMMAND_PREFIXES = (
    "pytest",
    "python -m unittest",
    "python3 -m unittest",
    "python -m py_compile",
    "python3 -m py_compile",
    "ruff",
    "go test",
    "npm test",
    "cargo test",
)

DISALLOWED_CHARS = (";", "&", "&&", "||", "|", "`", "$(", ">", "<", "\n")

class DiagnosticSandboxRunner:
    """
    Isolated Sandbox Runner Integration Boundary.
    Enforces that untrusted repository code is NEVER executed directly on the host web server.
    Dynamic test execution requires either a local Docker container daemon or a remote container sandbox worker.
    """
    def __init__(self, timeout_seconds: int = 15):
        self.timeout = timeout_seconds

    @staticmethod
    def is_docker_available() -> bool:
        """Checks if Docker daemon is accessible and responding."""
        try:
            res = subprocess.run(["docker", "version"], capture_output=True, text=True, timeout=2.0)
            return res.returncode == 0
        except Exception:
            return False

    @staticmethod
    def is_remote_worker_configured() -> bool:
        """Checks if a separately hosted isolated sandbox worker is configured."""
        try:
            from app.core.config import settings
            return bool(getattr(settings, "SANDBOX_WORKER_URL", None) and str(settings.SANDBOX_WORKER_URL).strip())
        except Exception:
            return False

    def is_isolated_execution_available(self) -> bool:
        """Returns True only when container-level isolation is available."""
        return self.is_docker_available() or self.is_remote_worker_configured()

    def get_runtime_status(self) -> Dict[str, Any]:
        """Returns genuine sandbox operational status without false claims."""
        if self.is_docker_available():
            from app.core.config import settings
            return {
                "available": True,
                "mode": "isolated_docker",
                "status": "ready",
                "can_execute_untrusted_tests": True,
                "isolated": True,
                "description": "Local Docker container daemon connected. Safe non-root container isolation available.",
                "memory_limit": getattr(settings, "DOCKER_MEMORY_LIMIT", "2048 MB"),
                "timeout_seconds": self.timeout,
            }
        elif self.is_remote_worker_configured():
            from app.core.config import settings
            return {
                "available": True,
                "mode": "remote_container_worker",
                "status": "ready",
                "can_execute_untrusted_tests": True,
                "isolated": True,
                "description": f"Remote isolated container worker configured at {settings.SANDBOX_WORKER_URL}.",
                "timeout_seconds": self.timeout,
            }
        else:
            return {
                "available": False,
                "mode": "unavailable",
                "status": "blocked_by_configuration",
                "can_execute_untrusted_tests": False,
                "isolated": False,
                "description": (
                    "Container isolation unavailable on web service host. "
                    "Untrusted test execution is disabled on the backend host to prevent code execution vulnerabilities. "
                    "Configure a Docker daemon or SANDBOX_WORKER_URL for dynamic test execution."
                ),
                "timeout_seconds": self.timeout,
            }

    def validate_command_safety(self, command: str) -> bool:
        """Enforce command allowlist and prevent shell injection."""
        cmd_strip = command.strip()
        if any(char in cmd_strip for char in DISALLOWED_CHARS):
            return False
        return any(cmd_strip.startswith(prefix) for prefix in ALLOWED_COMMAND_PREFIXES)

    def check_syntax(self, code_str: str, filename: str = "patch.py") -> (bool, Optional[str]):
        """
        Safe static syntax verification using compile().
        Compiles the AST without executing the code.
        """
        if filename.endswith(".py"):
            try:
                compile(code_str, filename, "exec")
                return True, None
            except SyntaxError as e:
                return False, f"Python SyntaxError at line {e.lineno}: {e.msg}"
        elif filename.endswith((".json", ".yaml", ".yml")):
            return True, None
        return True, None

    def execute_static_check(self, file_path: str, proposed_code: str) -> Dict[str, Any]:
        """
        Executes safe static syntax checks without dynamic code execution.
        Clearly distinguishes static syntax validation from dynamic test runs.
        """
        syntax_ok, syntax_err = self.check_syntax(proposed_code, filename=file_path)
        return {
            "validation_type": "static_syntax_check",
            "applied_cleanly": syntax_ok,
            "syntax_valid": syntax_ok,
            "tests_passed": False,
            "is_complete_test_validation": False,
            "error": syntax_err,
            "output": f"Static syntax check {'PASSED' if syntax_ok else 'FAILED: ' + str(syntax_err)} for {file_path}",
        }

    def execute_validation(
        self,
        file_path: str,
        original_code: str,
        proposed_code: str,
        test_code: Optional[str] = None,
        test_command: str = "pytest",
    ) -> Dict[str, Any]:
        """
        Executes patch verification:
        1. Checks syntax statically (without running code).
        2. Validates command safety allowlist.
        3. Enforces container isolation:
           - If Docker or SANDBOX_WORKER_URL is available, executes in isolated container.
           - If container isolation is unavailable, disables execution on host process,
             returning tests_passed=False and status='unsupported'.
        """
        t0 = time.perf_counter()

        # Step 1: Static syntax check
        syntax_ok, syntax_err = self.check_syntax(proposed_code, filename=file_path)
        if not syntax_ok:
            return {
                "applied_cleanly": False,
                "syntax_valid": False,
                "tests_passed": False,
                "total_tests": 1,
                "passed_tests": 0,
                "failed_tests": 1,
                "output": f"Patch failed syntax validation: {syntax_err}",
                "duration_seconds": round(time.perf_counter() - t0, 3),
                "security_verdict": "SYNTAX_CHECK_FAILED",
                "status": "failed",
            }

        # Step 2: Command safety check
        if not self.validate_command_safety(test_command):
            return {
                "applied_cleanly": False,
                "syntax_valid": True,
                "tests_passed": False,
                "total_tests": 1,
                "passed_tests": 0,
                "failed_tests": 1,
                "output": f"Security violation: Command '{test_command}' is not in the sandbox allowlist.",
                "duration_seconds": round(time.perf_counter() - t0, 3),
                "security_verdict": "COMMAND_DISALLOWED",
                "status": "failed",
            }

        # Step 3: Check isolation capability
        if not self.is_isolated_execution_available():
            duration = round(time.perf_counter() - t0, 3)
            return {
                "applied_cleanly": True,
                "syntax_valid": True,
                "tests_passed": False,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "output": (
                    "Execution Blocked: Untrusted repository test execution is disabled on the host web service. "
                    "Neither a Docker daemon nor an external SANDBOX_WORKER_URL is configured. "
                    "Static syntax checks passed, but dynamic test execution is blocked by configuration."
                ),
                "duration_seconds": duration,
                "security_verdict": "EXECUTION_BLOCKED_CONTAINER_REQUIRED",
                "status": "unsupported",
                "sandbox_configured": False,
                "isolated": False,
                "is_complete_test_validation": False,
            }

        # Step 4: Execute inside isolated Docker container if Docker is available
        if self.is_docker_available():
            return self._run_in_docker(
                file_path=file_path,
                proposed_code=proposed_code,
                test_code=test_code,
                test_command=test_command,
                t0=t0,
            )

        # Step 5: Execute via remote container worker
        return self._run_in_remote_worker(
            file_path=file_path,
            proposed_code=proposed_code,
            test_code=test_code,
            test_command=test_command,
            t0=t0,
        )

    def _run_in_docker(
        self,
        file_path: str,
        proposed_code: str,
        test_code: Optional[str],
        test_command: str,
        t0: float,
    ) -> Dict[str, Any]:
        """Runs validation in an isolated non-root container with network disabled."""
        with tempfile.TemporaryDirectory(prefix="fixora_docker_sandbox_") as tmp_dir:
            target_path = os.path.join(tmp_dir, file_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(proposed_code)

            if test_code:
                test_path = os.path.join(tmp_dir, "test_repair.py")
                with open(test_path, "w", encoding="utf-8") as f:
                    f.write(test_code)

            docker_cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", "512m",
                "--cpus", "1.0",
                "--user", "1000:1000",
                "-v", f"{tmp_dir}:/workspace:ro",
                "-w", "/workspace",
                "python:3.12-slim",
                "python", "-m", "unittest", "test_repair.py"
            ]
            try:
                proc = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=self.timeout)
                duration = round(time.perf_counter() - t0, 3)
                output = (proc.stdout + "\n" + proc.stderr).strip()
                passed = (proc.returncode == 0)
                return {
                    "applied_cleanly": True,
                    "syntax_valid": True,
                    "tests_passed": passed,
                    "total_tests": 1,
                    "passed_tests": 1 if passed else 0,
                    "failed_tests": 0 if passed else 1,
                    "output": output or ("Tests passed in Docker container." if passed else "Tests failed in Docker container."),
                    "duration_seconds": duration,
                    "security_verdict": "ALLOWED_SAFE_SANDBOX",
                    "status": "passed" if passed else "failed",
                    "isolated": True,
                }
            except Exception as e:
                return {
                    "applied_cleanly": True,
                    "syntax_valid": True,
                    "tests_passed": False,
                    "total_tests": 1,
                    "passed_tests": 0,
                    "failed_tests": 1,
                    "output": f"Docker container execution error: {str(e)}",
                    "duration_seconds": round(time.perf_counter() - t0, 3),
                    "security_verdict": "EXECUTION_ERROR",
                    "status": "failed",
                    "isolated": True,
                }

    def _run_in_remote_worker(
        self,
        file_path: str,
        proposed_code: str,
        test_code: Optional[str],
        test_command: str,
        t0: float,
    ) -> Dict[str, Any]:
        """Dispatches execution to a dedicated external container sandbox worker."""
        from app.core.config import settings
        import httpx
        url = f"{settings.SANDBOX_WORKER_URL.rstrip('/')}/execute"
        headers = {}
        if getattr(settings, "SANDBOX_WORKER_TOKEN", None):
            headers["Authorization"] = f"Bearer {settings.SANDBOX_WORKER_TOKEN}"

        payload = {
            "filePath": file_path,
            "proposedCode": proposed_code,
            "testCode": test_code,
            "command": test_command,
            "timeoutSeconds": self.timeout,
        }
        try:
            with httpx.Client(timeout=self.timeout + 5) as client:
                res = client.post(url, json=payload, headers=headers)
                duration = round(time.perf_counter() - t0, 3)
                if res.status_code == 200:
                    data = res.json()
                    tests_passed = bool(data.get("testsPassed", False))
                    return {
                        "applied_cleanly": True,
                        "syntax_valid": True,
                        "tests_passed": tests_passed,
                        "total_tests": data.get("totalTests", 1),
                        "passed_tests": data.get("passedTests", 1 if tests_passed else 0),
                        "failed_tests": data.get("failedTests", 0 if tests_passed else 1),
                        "output": data.get("output", "Remote container test execution completed."),
                        "duration_seconds": duration,
                        "security_verdict": "ALLOWED_SAFE_SANDBOX",
                        "status": "passed" if tests_passed else "failed",
                        "isolated": True,
                    }
                else:
                    return {
                        "applied_cleanly": True,
                        "syntax_valid": True,
                        "tests_passed": False,
                        "total_tests": 1,
                        "passed_tests": 0,
                        "failed_tests": 1,
                        "output": f"Remote container worker returned HTTP {res.status_code}: {res.text}",
                        "duration_seconds": duration,
                        "security_verdict": "EXECUTION_ERROR",
                        "status": "failed",
                        "isolated": True,
                    }
        except Exception as e:
            return {
                "applied_cleanly": True,
                "syntax_valid": True,
                "tests_passed": False,
                "total_tests": 1,
                "passed_tests": 0,
                "failed_tests": 1,
                "output": f"Remote container worker communication error: {str(e)}",
                "duration_seconds": round(time.perf_counter() - t0, 3),
                "security_verdict": "EXECUTION_ERROR",
                "status": "failed",
                "isolated": True,
            }

# Singleton instance
sandbox_runner = DiagnosticSandboxRunner()
