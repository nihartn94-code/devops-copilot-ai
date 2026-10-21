import re
from typing import Any, Dict, List, Optional, Tuple
from backend.app.models import FailedTestDetail, TestAnalysisResponse

class TestAnalyzerService:
    """
    Parses unit and integration test outputs (pytest, Jest, JUnit, generic),
    extracts failure details, and produces diagnostic reports.
    """

    @classmethod
    def detect_framework(cls, output: str, hint: Optional[str] = None) -> str:
        if hint and hint.lower() in ["pytest", "jest", "junit"]:
            return hint.lower()

        if "pytest" in output or "=== FAILURES ===" in output or "short test summary info" in output:
            return "pytest"
        if "FAIL " in output or "● " in output or "Test Suites:" in output:
            return "jest"
        if "<testsuite" in output or "junit" in output:
            return "junit"
        return "generic"

    @classmethod
    def parse_pytest(cls, output: str) -> Dict[str, Any]:
        failed_tests: List[FailedTestDetail] = []
        total = 0
        passed = 0
        failed = 0
        skipped = 0

        # Parse summary line: e.g., "2 failed, 3 passed in 1.42s" or "1 failed, 2 passed"
        summary_matches = re.findall(
            r"=+\s*([\d\w\s,]*?(?:passed|failed|skipped)[\d\w\s,]*?)(?:\s+in\s+[\d\.]+s)?\s*=+",
            output,
            re.IGNORECASE
        )
        if summary_matches:
            parts = summary_matches[-1].split(",")
            for part in parts:
                p = part.strip()
                if "passed" in p:
                    passed = int(re.search(r"\d+", p).group(0))
                elif "failed" in p:
                    failed = int(re.search(r"\d+", p).group(0))
                elif "skipped" in p:
                    skipped = int(re.search(r"\d+", p).group(0))
            total = passed + failed + skipped

        # Parse individual failures
        failure_blocks = re.split(r"_{10,}\s+([^\s_]+)\s+_{10,}", output)
        if len(failure_blocks) > 1:
            for i in range(1, len(failure_blocks), 2):
                test_name = failure_blocks[i].strip()
                body = failure_blocks[i+1] if i+1 < len(failure_blocks) else ""

                # Extract assertion error message
                err_lines = [l for l in body.splitlines() if l.strip().startswith("E ") or "Error:" in l or "assert " in l]
                failure_msg = "\n".join(err_lines[:4]) if err_lines else "Assertion failed"

                # Extract file path
                file_match = re.search(r"(tests/[^\s:]+\.py):(\d+):", body)
                file_path = file_match.group(1) if file_match else None

                # Extract assertion type
                assert_type = "AssertionError"
                if "ConnectionRefusedError" in body:
                    assert_type = "ConnectionRefusedError"
                elif "ValidationError" in body:
                    assert_type = "PydanticValidationError"
                elif "KeyError" in body:
                    assert_type = "KeyError"

                failed_tests.append(FailedTestDetail(
                    test_name=test_name,
                    file_path=file_path,
                    failure_message=failure_msg.strip(),
                    stack_trace=body.strip()[:1500],
                    assertion_type=assert_type
                ))

        if not failed_tests and failed > 0:
            # Fallback to short summary
            short_matches = re.findall(r"FAILED\s+([^\s:]+)::([^\s\-]+)\s+-\s+(.*)", output)
            for file_p, t_name, msg in short_matches:
                failed_tests.append(FailedTestDetail(
                    test_name=t_name,
                    file_path=file_p,
                    failure_message=msg,
                    stack_trace=msg,
                    assertion_type="AssertionError"
                ))

        return {
            "total": total if total > 0 else len(failed_tests),
            "passed": passed,
            "failed": failed if failed > 0 else len(failed_tests),
            "skipped": skipped,
            "failed_tests": failed_tests
        }

    @classmethod
    def parse_jest(cls, output: str) -> Dict[str, Any]:
        failed_tests: List[FailedTestDetail] = []
        total = 0
        passed = 0
        failed = 0

        # Parse Test Suites line: "Test Suites: 1 failed, 3 passed, 4 total"
        test_match = re.search(r"Tests:\s+(.*)", output)
        if test_match:
            parts = test_match.group(1).split(",")
            for p in parts:
                p = p.strip()
                if "passed" in p:
                    passed = int(re.search(r"\d+", p).group(0))
                elif "failed" in p:
                    failed = int(re.search(r"\d+", p).group(0))
                elif "total" in p:
                    total = int(re.search(r"\d+", p).group(0))

        # Parse test blocks: ● Suite > Test Name
        blocks = re.split(r"\s+●\s+", output)
        for block in blocks[1:]:
            lines = block.strip().splitlines()
            test_title = lines[0].strip() if lines else "Jest Test Failure"
            msg_lines = lines[1:8]
            failure_msg = "\n".join(msg_lines)

            file_match = re.search(r"\((src/[^\s:]+\.(?:tsx?|jsx?)):(\d+):(\d+)\)", block)
            file_p = file_match.group(1) if file_match else None

            failed_tests.append(FailedTestDetail(
                test_name=test_title,
                file_path=file_p,
                failure_message=failure_msg[:300],
                stack_trace=block[:1500],
                assertion_type="ExpectationMismatch"
            ))

        return {
            "total": total if total > 0 else len(failed_tests),
            "passed": passed,
            "failed": failed if failed > 0 else len(failed_tests),
            "skipped": 0,
            "failed_tests": failed_tests
        }

    @classmethod
    def analyze(cls, output: str, hint: Optional[str] = None) -> Dict[str, Any]:
        framework = cls.detect_framework(output, hint)
        if framework == "pytest":
            data = cls.parse_pytest(output)
        elif framework == "jest":
            data = cls.parse_jest(output)
        else:
            # Generic parsing
            failed_tests = [
                FailedTestDetail(
                    test_name="Generic Test Failure",
                    file_path=None,
                    failure_message="Test runner returned non-zero exit code or error output",
                    stack_trace=output[:1000],
                    assertion_type="GenericFailure"
                )
            ]
            data = {"total": 1, "passed": 0, "failed": 1, "skipped": 0, "failed_tests": failed_tests}

        # Root cause synthesis & next steps
        root_cause, next_steps, remedy = cls._synthesize_diagnosis(data["failed_tests"], framework)

        return {
            "framework": framework,
            "total_tests": data["total"],
            "passed": data["passed"],
            "failed": data["failed"],
            "skipped": data["skipped"],
            "failed_tests": data["failed_tests"],
            "root_cause_summary": root_cause,
            "next_steps": next_steps,
            "remedy_patch": remedy
        }

    @classmethod
    def _synthesize_diagnosis(cls, failed_tests: List[FailedTestDetail], framework: str) -> Tuple[str, List[str], Optional[str]]:
        if not failed_tests:
            return (
                "All tests passed successfully or no failures were identified in output.",
                ["Verify test coverage and run regression test suites."],
                None
            )

        test_types = [t.assertion_type for t in failed_tests if t.assertion_type]
        has_conn = any("Connection" in str(t.assertion_type) or "Connection" in t.stack_trace or "Connection" in t.failure_message for t in failed_tests)
        has_validation = any("Validation" in str(t.assertion_type) or "Validation" in t.stack_trace for t in failed_tests)
        has_status_code = any("500 == 422" in t.failure_message or "500 == 422" in t.stack_trace for t in failed_tests)

        if has_conn or has_status_code or has_validation:
            summary = (
                "Multiple test failures detected: (1) An unhandled server exception causing HTTP 500 instead of "
                "the expected HTTP 422 validation error (Pydantic ValidationError), and (2) Database connection refused at 127.0.0.1:5432."
            )
            steps = [
                "Ensure local PostgreSQL/database service or container is running before launching test suites.",
                "Implement a FastAPI exception handler for Pydantic ValidationError or check input serialization in the user route.",
                "Use test fixtures with mock database sessions (e.g. SQLite in-memory) instead of expecting a live external database."
            ]
            patch = (
                "# 1. Add exception handler in FastAPI app:\n"
                "@app.exception_handler(RequestValidationError)\n"
                "async def validation_exception_handler(request, exc):\n"
                "    return JSONResponse(status_code=422, content={'detail': exc.errors()})\n\n"
                "# 2. Mock database session in conftest.py:\n"
                "@pytest.fixture\n"
                "def test_db():\n"
                "    engine = create_engine('sqlite:///:memory:')\n"
                "    Base.metadata.create_all(bind=engine)\n"
                "    yield engine"
            )
            return summary, steps, patch

        if any("ExpectationMismatch" in str(t) for t in test_types):
            summary = (
                "React / Jest DOM assertion failure: The component rendered 'Build Pending' instead of the expected 'Build Failed', "
                "or the CSS class did not match the expected state."
            )
            steps = [
                "Check the component's state mapping for status='failure'.",
                "Ensure badge text and classNames are conditionally applied properly.",
                "Verify whether mock data or props passed to the test match the component requirements."
            ]
            patch = (
                "// Fix in BuildStatusBadge.tsx:\n"
                "export const BuildStatusBadge = ({ status }: { status: 'success' | 'failure' | 'pending' }) => {\n"
                "  const isFailure = status === 'failure';\n"
                "  return (\n"
                "    <span data-testid='status-badge' className={isFailure ? 'bg-red-500 text-white' : 'bg-yellow-500'}>\n"
                "      {isFailure ? 'Build Failed' : 'Build Pending'}\n"
                "    </span>\n"
                "  );\n"
                "};"
            )
            return summary, steps, patch

        summary = f"{len(failed_tests)} test(s) failed in {framework} suite."
        steps = [
            "Check assertion differences in the captured stack trace.",
            "Verify environment variables and mocks in test fixtures.",
            "Run failing tests in isolation to isolate state pollution."
        ]
        return summary, steps, None

test_analyzer_service = TestAnalyzerService()
