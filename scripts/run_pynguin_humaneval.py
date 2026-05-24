#!/usr/bin/env python3
"""
Pynguin Batch Runner for HumanEval Dataset (164 modules)
=========================================================
Usage:
    python run_pynguin_humaneval.py --modules-dir ./modules --output-dir ./results [OPTIONS]

Requirements:
    pip install pynguin pytest pytest-cov
    export PYNGUIN_DANGER_AWARE=1
"""

import argparse
import csv
import json
import logging
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


@dataclass
class ModuleResult:
    module_name: str
    status: str                        # "success" | "no_tests" | "pynguin_error" | "coverage_error" | "timeout"
    pynguin_return_code: Optional[int] = None
    tests_generated: int = 0
    line_coverage: Optional[float] = None   # 0.0 – 100.0
    lines_total: Optional[int] = None
    lines_missed: Optional[int] = None
    missing_lines: str = ""
    duration_seconds: float = 0.0
    error_message: str = ""
    test_file_path: str = ""


def check_environment() -> None:
    """Abort early if required env var is missing."""
    if not os.environ.get("PYNGUIN_DANGER_AWARE"):
        log.error(
            "Environment variable PYNGUIN_DANGER_AWARE is not set.\n"
            "Pynguin executes code under test during generation.\n"
            "If you accept this risk, run:\n\n"
            "    export PYNGUIN_DANGER_AWARE=1\n"
        )
        sys.exit(1)


def count_test_cases(test_file: Path) -> int:
    """Count 'def test_' occurrences in a generated test file."""
    if not test_file.exists():
        return 0
    text = test_file.read_text(errors="replace")
    return text.count("def test_")


def run_pynguin(
    module_path: Path,
    output_dir: Path,
    budget: int,
    seed: int,
    algorithm: str,
    assertion_gen: str,
) -> tuple[int, str, str]:
    """Invoke Pynguin as a subprocess and return (returncode, stdout, stderr)."""
    cmd = [
        sys.executable, "-m", "pynguin",
        "--project-path", str(module_path.parent),
        "--module-name", module_path.stem,
        "--output-path", str(output_dir),
        "--maximum-search-time", str(budget),
        "--seed", str(seed),
        "--algorithm", algorithm,
        "--assertion-generation", assertion_gen,
        "-v",
    ]
    env = {**os.environ, "PYNGUIN_DANGER_AWARE": "1"}
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=budget + 60,   # hard kill: budget + grace period
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_coverage(
    module_path: Path,
    test_file: Path,
    output_dir: Path,
) -> tuple[Optional[float], Optional[int], Optional[int], str, str]:
    """
    Run pytest --cov on the generated test file.
    Returns (coverage_pct, total_lines, missed_lines, missing_str, raw_output).
    """
    json_report = output_dir / f"{module_path.stem}_cov.json"
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        f"--cov={module_path}",
        "--cov-report=json:" + str(json_report),
        "--cov-report=term-missing",
        "--tb=no",
        "-q",
    ]
    env = {**os.environ, "PYTHONPATH": str(module_path.parent)}
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    raw = proc.stdout + proc.stderr

    # Parse JSON coverage report
    if json_report.exists():
        try:
            data = json.loads(json_report.read_text())
            # Find our module in the report
            for fpath, fdata in data.get("files", {}).items():
                if Path(fpath).stem == module_path.stem:
                    summary = fdata["summary"]
                    pct = summary.get("percent_covered", 0.0)
                    total = summary.get("num_statements", 0)
                    missed = summary.get("missing_lines", 0)
                    missing_str = ",".join(str(l) for l in fdata.get("missing_lines", []))
                    return round(pct, 2), total, missed, missing_str, raw
        except (json.JSONDecodeError, KeyError):
            pass

    return None, None, None, "", raw


def process_module(
    module_path: Path,
    results_dir: Path,
    budget: int,
    seed: int,
    algorithm: str,
    assertion_gen: str,
    idx: int,
    total: int,
) -> ModuleResult:
    name = module_path.stem
    log.info(f"[{idx}/{total}] Processing: {name}")

    module_out = results_dir / "tests" / name
    module_out.mkdir(parents=True, exist_ok=True)

    result = ModuleResult(module_name=name, status="pynguin_error")
    t0 = time.time()

    try:
        rc, stdout, stderr = run_pynguin(
            module_path, module_out, budget, seed, algorithm, assertion_gen
        )
    except subprocess.TimeoutExpired:
        result.status = "timeout"
        result.duration_seconds = round(time.time() - t0, 2)
        result.error_message = f"Pynguin killed after {budget + 60}s"
        log.warning(f"  [{name}] TIMEOUT")
        return result
    except Exception as exc:
        result.status = "pynguin_error"
        result.duration_seconds = round(time.time() - t0, 2)
        result.error_message = str(exc)
        log.warning(f"  [{name}] ERROR: {exc}")
        return result

    result.pynguin_return_code = rc

    test_file = module_out / f"test_{name}.py"
    if not test_file.exists():
        # Fallback: look for any test_*.py file Pynguin may have generated
        candidates = list(module_out.glob("test_*.py"))
        if candidates:
            test_file = candidates[0]
    result.test_file_path = str(test_file)
    result.tests_generated = count_test_cases(test_file)

    if rc != 0 or not test_file.exists():
        result.status = "pynguin_error"
        # Capture first meaningful error line
        for line in (stdout + stderr).splitlines():
            if "error" in line.lower() or "exception" in line.lower():
                result.error_message = line.strip()
                break
        result.duration_seconds = round(time.time() - t0, 2)
        log.warning(f"  [{name}] Pynguin failed (rc={rc})")
        return result

    if result.tests_generated == 0:
        result.status = "no_tests"
        result.duration_seconds = round(time.time() - t0, 2)
        log.warning(f"  [{name}] No tests generated")
        return result

    cov_out = results_dir / "coverage_json"
    cov_out.mkdir(parents=True, exist_ok=True)

    try:
        pct, total_lines, missed, missing_str, cov_raw = run_coverage(
            module_path, test_file, cov_out
        )
    except subprocess.TimeoutExpired:
        result.status = "coverage_error"
        result.error_message = "Coverage measurement timed out"
        result.duration_seconds = round(time.time() - t0, 2)
        log.warning(f"  [{name}] Coverage timeout")
        return result
    except Exception as exc:
        result.status = "coverage_error"
        result.error_message = str(exc)
        result.duration_seconds = round(time.time() - t0, 2)
        log.warning(f"  [{name}] Coverage error: {exc}")
        return result

    result.line_coverage = pct
    result.lines_total = total_lines
    result.lines_missed = missed
    result.missing_lines = missing_str or ""
    result.status = "success"
    result.duration_seconds = round(time.time() - t0, 2)

    log.info(
        f"  [{name}] ✓ tests={result.tests_generated}, "
        f"coverage={pct}%, time={result.duration_seconds}s"
    )
    return result


def write_csv(results: list[ModuleResult], path: Path) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(r) for r in results)


def write_json(results: list[ModuleResult], path: Path) -> None:
    path.write_text(
        json.dumps([asdict(r) for r in results], indent=2)
    )


def print_summary(results: list[ModuleResult]) -> None:
    total = len(results)
    success = [r for r in results if r.status == "success"]
    no_tests = [r for r in results if r.status == "no_tests"]
    errors = [r for r in results if r.status in ("pynguin_error", "coverage_error")]
    timeouts = [r for r in results if r.status == "timeout"]

    coverages = [r.line_coverage for r in success if r.line_coverage is not None]
    avg_cov = sum(coverages) / len(coverages) if coverages else 0.0
    full_cov = sum(1 for c in coverages if c == 100.0)

    print("\n" + "=" * 60)
    print("  PYNGUIN BATCH RUN — SUMMARY")
    print("=" * 60)
    print(f"  Total modules       : {total}")
    print(f"  Successful          : {len(success)}")
    print(f"  No tests generated  : {len(no_tests)}")
    print(f"  Pynguin/cov errors  : {len(errors)}")
    print(f"  Timeouts            : {len(timeouts)}")
    print(f"  Avg line coverage   : {avg_cov:.1f}%")
    print(f"  100% coverage       : {full_cov} modules")
    print("=" * 60)

    if errors:
        print("\n  Failed modules:")
        for r in errors:
            print(f"    {r.module_name}: {r.error_message[:80]}")

    if no_tests:
        print("\n  No-tests modules:")
        for r in no_tests:
            print(f"    {r.module_name}")
    print()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run Pynguin on all HumanEval modules and collect coverage."
    )
    p.add_argument(
        "--modules-dir",
        default=Path("data/modules"), type=Path,
        help="Directory containing the 164 HumanEval .py module files."
    )
    p.add_argument(
        "--output-dir", default=Path("pynguin_results"), type=Path,
        help="Root directory for all outputs (default: ./pynguin_results)."
    )
    p.add_argument(
        "--budget", type=int, default=60,
        help="Pynguin search budget in seconds per module (default: 60)."
    )
    p.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducibility (default: 42)."
    )
    p.add_argument(
        "--algorithm", default="DYNAMOSA",
        choices=["DYNAMOSA", "MOSA", "RANDOM", "RANDOM_TEST_SUITE",
                 "WHOLE_SUITE", "MIO", "RANDOM_TEST_CASE"],
        help="Pynguin search algorithm (default: DYNAMOSA)."
    )
    p.add_argument(
        "--assertion-generation", default="SIMPLE",
        choices=["SIMPLE", "MUTATION", "NONE"],
        dest="assertion_gen",
        help="Assertion generation strategy (default: SIMPLE)."
    )
    p.add_argument(
        "--workers", type=int, default=1,
        help=(
            "Number of parallel workers (default: 1). "
            "WARNING: Pynguin executes code — use >1 only in an isolated environment."
        )
    )
    p.add_argument(
        "--module-pattern", default="*.py",
        help="Glob pattern to match module files (default: '*.py')."
    )
    p.add_argument(
        "--skip-existing", action="store_true",
        help="Skip modules that already have a generated test file."
    )
    p.add_argument(
        "--modules", nargs="*",
        help="Process only these specific module names (without .py)."
    )
    return p.parse_args()

def main() -> None:
    args = parse_args()
    check_environment()

    modules_dir: Path = args.modules_dir.resolve()
    output_dir: Path = args.output_dir.resolve()

    if not modules_dir.exists():
        log.error(f"Modules directory not found: {modules_dir}")
        sys.exit(1)

    # Gather modules
    all_modules = sorted(modules_dir.glob(args.module_pattern))
    all_modules = [m for m in all_modules if not m.name.startswith("_")]

    if args.modules:
        all_modules = [m for m in all_modules if m.stem in args.modules]

    if not all_modules:
        log.error(f"No modules found in {modules_dir} matching '{args.module_pattern}'")
        sys.exit(1)

    if args.skip_existing:
        def _has_tests(m: Path) -> bool:
            return (output_dir / "tests" / m.stem / f"test_{m.stem}.py").exists()
        before = len(all_modules)
        all_modules = [m for m in all_modules if not _has_tests(m)]
        log.info(f"Skipping {before - len(all_modules)} already-processed modules.")

    total = len(all_modules)
    log.info(f"Found {total} modules to process in {modules_dir}")
    log.info(
        f"Settings: budget={args.budget}s, seed={args.seed}, "
        f"algorithm={args.algorithm}, assertion={args.assertion_gen}, "
        f"workers={args.workers}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    results: list[ModuleResult] = []

    if args.workers == 1:
        for idx, module_path in enumerate(all_modules, 1):
            r = process_module(
                module_path, output_dir,
                args.budget, args.seed, args.algorithm, args.assertion_gen,
                idx, total,
            )
            results.append(r)
    else:
        log.warning(
            f"Running with {args.workers} parallel workers. "
            "Ensure you are in a sandboxed/containerised environment!"
        )
        worker_args = [
            (m, output_dir, args.budget, args.seed,
             args.algorithm, args.assertion_gen, i + 1, total)
            for i, m in enumerate(all_modules)
        ]
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(process_module, *a): a[0].stem for a in worker_args}
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as exc:
                    name = futures[future]
                    log.error(f"Worker for {name} raised: {exc}")
                    results.append(ModuleResult(
                        module_name=name,
                        status="pynguin_error",
                        error_message=str(exc),
                    ))

    order = {m.stem: i for i, m in enumerate(all_modules)}
    results.sort(key=lambda r: order.get(r.module_name, 9999))

    csv_path = output_dir / f"results_{run_ts}.csv"
    json_path = output_dir / f"results_{run_ts}.json"
    write_csv(results, csv_path)
    write_json(results, json_path)

    log.info(f"CSV report  → {csv_path}")
    log.info(f"JSON report → {json_path}")

    print_summary(results)


if __name__ == "__main__":
    main()