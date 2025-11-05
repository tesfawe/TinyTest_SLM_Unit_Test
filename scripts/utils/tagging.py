import ast
import re
from pathlib import Path
from typing import Literal, Tuple

StatusType = Literal["compiled", "ran", "passed", "failed"]
FailureType = Literal["syntax", "import", "assertion"]


def check_syntax(test_file: Path) -> Tuple[bool, str | None]:
    """Check if test file has valid Python syntax. Returns (is_valid, error_msg)."""
    try:
        code = test_file.read_text(encoding="utf-8")
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Parse error: {str(e)}"


def tag_status_and_failure(pytest_log: str, test_file: Path) -> Tuple[StatusType, FailureType | None]:
    """
    Determine status and failure type from pytest log and test file.
    Returns: (status, failure_type)
    - compiled: syntax valid (compiled successfully), but may not have run
    - ran: pytest attempted execution but failed (import error, etc.)
    - passed: all tests passed
    - failed: tests executed but some failed (assertion failures, or syntax error)
    """
    # Check syntax first
    syntax_valid, syntax_error = check_syntax(test_file)
    if not syntax_valid:
        return "failed", "syntax"  # Syntax error = failed with syntax failure type
    
    log_lower = pytest_log.lower()
    
    # Check for import errors (syntax valid but can't import)
    if "ImportError" in pytest_log or "ModuleNotFoundError" in pytest_log or "import error" in log_lower:
        return "ran", "import"
    
    # Check if tests passed (no failures, has passed count)
    if "passed" in log_lower:
        # Check if there are any failures
        if "failed" in log_lower or "FAILED" in pytest_log:
            # Has both passed and failed - some tests failed
            if "AssertionError" in pytest_log or ("assert" in log_lower and "failed" in log_lower):
                return "failed", "assertion"
            return "failed", None
        # All passed, no failures
        return "passed", None
    
    # Check for assertion failures
    if "failed" in log_lower or "FAILED" in pytest_log:
        if "AssertionError" in pytest_log or ("assert" in log_lower and "failed" in log_lower):
            return "failed", "assertion"
        return "failed", None
    
    # If pytest ran but no clear pass/fail (maybe collection error or other issue)
    if "collected" in log_lower or "test" in log_lower or "no tests ran" in log_lower:
        return "ran", None
    
    # Default: syntax valid (compiled) but unclear if pytest ran
    return "compiled", None


def parse_test_counts(pytest_log: str) -> dict:
    """
    Parse pytest output to extract test counts.
    Returns: {tests_passed, tests_failed, tests_total, tests_error}
    """
    counts = {
        "tests_passed": 0,
        "tests_failed": 0,
        "tests_error": 0,
        "tests_total": 0,
    }
    
    log_lower = pytest_log.lower()
    
    # Check for "no tests ran" or "collected 0 items"
    if "no tests ran" in log_lower or "collected 0 items" in log_lower:
        return counts
    
    # Check for collection errors (ERROR during collection)
    if "error" in log_lower and ("collecting" in log_lower or "collection" in log_lower or "error collecting" in log_lower):
        counts["tests_error"] = 1
        counts["tests_total"] = 1
        return counts
    
    # Extract numbers from patterns like "3 failed, 7 passed in 0.04s"
    # Or: "5 failed in 0.06s"
    # Or: "1 error in 0.05s"
    passed_match = re.search(r'(\d+)\s+passed', pytest_log)
    failed_match = re.search(r'(\d+)\s+failed', pytest_log)
    error_match = re.search(r'(\d+)\s+error', pytest_log)
    
    if passed_match:
        counts["tests_passed"] = int(passed_match.group(1))
    if failed_match:
        counts["tests_failed"] = int(failed_match.group(1))
    if error_match:
        counts["tests_error"] = int(error_match.group(1))
    
    counts["tests_total"] = counts["tests_passed"] + counts["tests_failed"] + counts["tests_error"]
    
    return counts


