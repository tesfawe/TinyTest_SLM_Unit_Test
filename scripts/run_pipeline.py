#!/usr/bin/env python3
import argparse
import time
from pathlib import Path
from typing import Iterable, List

from .test_generation import build_prompt, generate_with_ollama
from .auto_repair import auto_repair
from .utils.file_ops import make_run_root, module_run_dir, write_text
from .utils.logger import write_json
from .utils.runner import run_pytest
from .utils.tagging import tag_status_and_failure, parse_test_counts


# python -m scripts.run_pipeline --model llama3.2 --template few_shot --range 1-5 --max_retries 1



def iter_modules(modules_dir: Path, start: int | None, end: int | None) -> Iterable[Path]:
    files = sorted(modules_dir.glob("module_*.py"))
    if start is None and end is None:
        return files
    selected: List[Path] = []
    for f in files:
        try:
            idx = int(f.stem.split("_")[-1])
        except ValueError:
            continue
        if (start is None or idx >= start) and (end is None or idx <= end):
            selected.append(f)
    return selected


def main():
    parser = argparse.ArgumentParser(description="End-to-end TinyTest pipeline: gen → run → auto-repair")
    parser.add_argument("--model", required=True, help="Ollama model name (e.g., phi3, mistral, gemma)")
    parser.add_argument("--template", default="few_shot", choices=["few_shot", "structured", "zero_shot"], help="Prompt template for initial generation")
    parser.add_argument("--modules_dir", default="data/modules", help="Directory containing source modules")
    parser.add_argument("--max_retries", type=int, default=2, help="Max auto-repair attempts after initial failure")
    parser.add_argument("--range", dest="range_", default=None, help="Module index range like 1-20 (optional)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for model generation")
    parser.add_argument("--temperature", type=float, default=None, help="Temperature for model generation")
    args = parser.parse_args()

    modules_dir = Path(args.modules_dir)
    if not modules_dir.exists():
        raise FileNotFoundError(modules_dir)

    start = end = None
    if args.range_:
        try:
            parts = args.range_.split("-")
            if parts[0]:
                start = int(parts[0])
            if len(parts) > 1 and parts[1]:
                end = int(parts[1])
        except Exception:
            raise ValueError("--range must be like '1-20' (start-end)")

    run_root = make_run_root(args.model, args.template)

    for module_path in iter_modules(modules_dir, start, end):
        mod_dir = module_run_dir(run_root, module_path.stem)
        module_id = module_path.stem  # e.g., "module_001"

        # Build base metadata structure
        metadata = {
            "module_id": module_id,
            "model": args.model,
            "prompt_id": args.template,  # few_shot/zero_shot/structured
            "seed": args.seed,
            "temp": args.temperature,
            "iterations": [],
        }

        total_start_time = time.time()

        # 1) Generate tests (initial iteration)
        prompt = build_prompt(module_path, Path("data/metadata") / f"{module_path.stem}.json", template=args.template)
        generated_text, gen_metadata = generate_with_ollama(args.model, prompt, seed=args.seed, temperature=args.temperature)

        test_file_raw = mod_dir / f"{module_path.stem}_test_raw.py"
        write_text(test_file_raw, generated_text)

        # 2) Run pytest on initial test
        passed, log_raw = run_pytest(test_file_raw)
        write_text(mod_dir / "pytest_log.txt", log_raw)

        # Determine status and failure type
        status, failure_type = tag_status_and_failure(log_raw, test_file_raw)
        test_counts = parse_test_counts(log_raw)

        # Add initial iteration with tokens and time
        iteration = {
            "iteration": 0,
            "kind": "initial",
            "test_code": generated_text,
            "run_log": log_raw,
            "status": status,
            "failure_type": failure_type,
            "tests_passed": test_counts["tests_passed"],
            "tests_failed": test_counts["tests_failed"],
            "tests_error": test_counts["tests_error"],
            "tests_total": test_counts["tests_total"],
            "time": gen_metadata.get("time"),
            "tokens": gen_metadata.get("total_tokens"),
        }
        metadata["iterations"].append(iteration)

        # Track final status from last iteration
        final_status = status
        final_failure_type = failure_type

        # 3) Auto-repair attempts
        if status not in ("compiled", "passed") and failure_type != "syntax":  # Only repair if it ran but failed (not syntax errors)
            retries = 0
            cur_test_path = test_file_raw
            cur_log = log_raw
            
            while retries < args.max_retries:
                retries += 1
                repaired_text, repair_metadata = auto_repair(
                    model=args.model,
                    module_path=module_path,
                    failing_test_path=cur_test_path,
                    pytest_log=cur_log,
                    seed=args.seed,
                    temperature=args.temperature,
                )
                repaired_path = mod_dir / f"{module_path.stem}_test_repaired_{retries}.py"
                write_text(repaired_path, repaired_text)

                passed, log = run_pytest(repaired_path)
                write_text(mod_dir / f"pytest_log_retry_{retries}.txt", log)

                # Update status after repair
                status, failure_type = tag_status_and_failure(log, repaired_path)
                test_counts = parse_test_counts(log)

                # Add repair iteration with tokens and time
                iteration = {
                    "iteration": retries,
                    "kind": "repair",
                    "test_code": repaired_text,
                    "run_log": log,
                    "status": status,
                    "failure_type": failure_type,
                    "tests_passed": test_counts["tests_passed"],
                    "tests_failed": test_counts["tests_failed"],
                    "tests_error": test_counts["tests_error"],
                    "tests_total": test_counts["tests_total"],
                    "time": repair_metadata.get("time"),
                    "tokens": repair_metadata.get("total_tokens"),
                }
                metadata["iterations"].append(iteration)

                # Update final status
                final_status = status
                final_failure_type = failure_type

                if status == "passed":
                    break
                
                cur_test_path = repaired_path
                cur_log = log

        # Calculate total time
        total_time = time.time() - total_start_time

        # Add final status and totals
        metadata["final_status"] = final_status
        metadata["final_failure_type"] = final_failure_type
        metadata["total_time"] = total_time
        metadata["cost"] = None  # Ollama doesn't provide cost

        write_json(mod_dir / "metadata.json", metadata)

    print(f"Run complete. Outputs saved under: {run_root}")


if __name__ == "__main__":
    main()


