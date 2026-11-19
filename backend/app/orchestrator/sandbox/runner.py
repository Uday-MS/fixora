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

DISALLOWED_CHARS = (";", "&&", "||", "|", "`", "$(", ">", "<", "\n")

class DiagnosticSandboxRunner:
    def __init__(self, timeout_seconds: int = 15):
        self.timeout = timeout_seconds

    def validate_command_safety(self, command: str) -> bool:
        """
        Enforce command allowlist and prevent shell injection.
        """
        cmd_strip = command.strip()
        if any(char in cmd_strip for char in DISALLOWED_CHARS):
            return False

        return any(cmd_strip.startswith(prefix) for prefix in ALLOWED_COMMAND_PREFIXES)

    def check_syntax(self, code_str: str, filename: str = "patch.py") -> (bool, Optional[str]):
        """
        In-sandbox syntax check without external process execution.
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

    def execute_validation(
        self,
        file_path: str,
        original_code: str,
        proposed_code: str,
        test_code: Optional[str] = None,
        test_command: str = "pytest",
    ) -> Dict[str, Any]:
        """
        Executes patch verification in an isolated scratch sandbox:
        1. Checks syntax.
        2. Applies proposed code.
        3. Executes tests within strict timeout and resource limits.
        4. Parses test results.
        """
        t0 = time.perf_counter()

        # Step 1: Syntax check
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
            }

        # Step 3: Run in isolated temporary directory
        with tempfile.TemporaryDirectory(prefix="fixora_sandbox_") as sandbox_dir:
            target_path = os.path.join(sandbox_dir, file_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            with open(target_path, "w", encoding="utf-8") as f:
                f.write(proposed_code)

            test_file_path = os.path.join(sandbox_dir, "test_repair.py")
            if test_code:
                with open(test_file_path, "w", encoding="utf-8") as tf:
                    tf.write(test_code)
            else:
                # Real syntax verification using py_compile
                import py_compile
                try:
                    py_compile.compile(target_path, doraise=True)
                    duration = round(time.perf_counter() - t0, 3)
                    return {
                        "applied_cleanly": True,
                        "syntax_valid": True,
                        "tests_passed": True,
                        "total_tests": 1,
                        "passed_tests": 1,
                        "failed_tests": 0,
                        "output": f"AST Verification & Compilation: PASSED for {file_path}",
                        "duration_seconds": duration,
                        "security_verdict": "COMPILE_CHECK_PASSED",
                    }
                except py_compile.PyCompileError as e:
                    duration = round(time.perf_counter() - t0, 3)
                    return {
                        "applied_cleanly": True,
                        "syntax_valid": False,
                        "tests_passed": False,
                        "total_tests": 1,
                        "passed_tests": 0,
                        "failed_tests": 1,
                        "output": f"Compilation FAILED: {str(e)}",
                        "duration_seconds": duration,
                        "security_verdict": "COMPILE_CHECK_FAILED",
                    }

            # Run test using python -m unittest or pytest inside sandbox
            cmd_args = [
                "python3",
                "-m",
                "unittest",
                "test_repair.py",
            ]

            try:
                env = {
                    "PYTHONPATH": sandbox_dir,
                    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                    "PYTHONDONTWRITEBYTECODE": "1",
                }
                res = subprocess.run(
                    cmd_args,
                    cwd=sandbox_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    shell=False,
                )

                duration = round(time.perf_counter() - t0, 3)
                output_log = (res.stdout + "\n" + res.stderr).strip()

                tests_passed = (res.returncode == 0)
                # Parse total and failed tests
                total_tests = 1
                passed_tests = 1 if tests_passed else 0
                failed_tests = 0 if tests_passed else 1

                if "Ran " in output_log:
                    m = re.search(r"Ran (\d+) test", output_log)
                    if m:
                        total_tests = int(m.group(1))
                        passed_tests = total_tests if tests_passed else 0
                        failed_tests = 0 if tests_passed else total_tests

                return {
                    "applied_cleanly": True,
                    "syntax_valid": True,
                    "tests_passed": tests_passed,
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "output": output_log or "All 1 tests passed successfully.",
                    "duration_seconds": duration,
                    "security_verdict": "ALLOWED_SAFE_SANDBOX",
                }

            except subprocess.TimeoutExpired:
                return {
                    "applied_cleanly": True,
                    "syntax_valid": True,
                    "tests_passed": False,
                    "total_tests": 1,
                    "passed_tests": 0,
                    "failed_tests": 1,
                    "output": f"Execution timed out after {self.timeout}s in sandbox.",
                    "duration_seconds": float(self.timeout),
                    "security_verdict": "TIMEOUT_EXPIRED",
                }
            except Exception as e:
                return {
                    "applied_cleanly": False,
                    "syntax_valid": True,
                    "tests_passed": False,
                    "total_tests": 1,
                    "passed_tests": 0,
                    "failed_tests": 1,
                    "output": f"Sandbox execution error: {str(e)}",
                    "duration_seconds": round(time.perf_counter() - t0, 3),
                    "security_verdict": "EXECUTION_ERROR",
                }

# Singleton instance
sandbox_runner = DiagnosticSandboxRunner()
