#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Iterable, List

from .test_generation import build_prompt, generate_with_ollama, save_generated_test
from .auto_repair import auto_repair
from .utils.file_ops import make_run_root, module_run_dir, write_text
from .utils.logger import write_json
from .utils.runner import run_pytest
from .utils.tagging import tag_failure


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

        # 1) Generate tests
        prompt = build_prompt(module_path, Path("data/metadata") / f"{module_path.stem}.json", template=args.template)
        generated_text = generate_with_ollama(args.model, prompt)

        test_file = mod_dir / f"{module_path.stem}_test_raw.py"
        write_text(test_file, generated_text)

        # 2) Run pytest on initial test
        passed, log = run_pytest(test_file)
        write_text(mod_dir / "pytest_log.txt", log)

        metadata = {
            "module": module_path.name,
            "model": args.model,
            "template": args.template,
            "attempts": []
        }

        metadata["attempts"].append({
            "kind": "initial",
            "test_file": str(test_file),
            "passed": passed,
            "failure_type": None if passed else tag_failure(log),
        })

        if not passed:
            retries = 0
            cur_test_path = test_file
            while retries < args.max_retries:
                retries += 1
                repaired_text = auto_repair(
                    model=args.model,
                    module_path=module_path,
                    failing_test_path=cur_test_path,
                    pytest_log=log,
                )
                repaired_path = mod_dir / f"{module_path.stem}_test_repaired_{retries}.py"
                write_text(repaired_path, repaired_text)

                passed, log = run_pytest(repaired_path)
                write_text(mod_dir / f"pytest_log_retry_{retries}.txt", log)

                metadata["attempts"].append({
                    "kind": "repair",
                    "iteration": retries,
                    "test_file": str(repaired_path),
                    "passed": passed,
                    "failure_type": None if passed else tag_failure(log),
                })

                if passed:
                    break
                cur_test_path = repaired_path

        # 3) Final status per module
        metadata["final_status"] = "passed" if any(a.get("passed") for a in metadata["attempts"]) else "failed"
        write_json(mod_dir / "metadata.json", metadata)

    print(f"Run complete. Outputs saved under: {run_root}")


if __name__ == "__main__":
    main()


