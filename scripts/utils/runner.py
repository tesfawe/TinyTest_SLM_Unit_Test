import os
import subprocess
from pathlib import Path
from typing import Tuple


def run_pytest(test_file: Path, extra_args: list[str] | None = None) -> Tuple[bool, str]:
    args = ["pytest", "-q", str(test_file)]
    if extra_args:
        args.extend(extra_args)

    # Ensure imports like `from data.modules...` resolve by running from repo root and setting PYTHONPATH
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{repo_root}:{existing}" if existing else str(repo_root)

    result = subprocess.run(args, capture_output=True, text=True, cwd=str(repo_root), env=env)

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    full_log = stdout + ("\n" + stderr if stderr else "")

    passed = result.returncode == 0
    return passed, full_log


