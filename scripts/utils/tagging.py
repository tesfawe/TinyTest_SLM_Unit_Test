from typing import Literal

FailureType = Literal[
    "import_error",
    "assertion_failure",
    "exception",
    "timeout",
    "collection_error",
    "unknown",
]


def tag_failure(pytest_log: str) -> FailureType:
    log_lower = pytest_log.lower()
    if "ImportError" in pytest_log or "ModuleNotFoundError" in pytest_log or "import error" in log_lower:
        return "import_error"
    if "assert" in log_lower and ("failed" in log_lower or "assertion" in log_lower):
        return "assertion_failure"
    if "E   " in pytest_log or "Traceback (most recent call last)" in pytest_log:
        return "exception"
    if "timeout" in log_lower:
        return "timeout"
    if "errors during collection" in log_lower or "collected 0 items" in log_lower:
        return "collection_error"
    return "unknown"


