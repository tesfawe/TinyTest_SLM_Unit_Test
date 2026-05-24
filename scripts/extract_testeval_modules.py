# scripts/extract_testeval_modules.py

"""
extract_testeval_modules.py

Extract Python modules from the TestEval dataset (TestEval.jsonl).

Selection rules (50 tasks total):
  - Include entries with difficulty == 1
  - Otherwise include entries with task_num < 770

Output:
    data/modules_testeval/module_001.py
    data/modules_testeval/module_002.py
    ...
"""

import json
from pathlib import Path


def should_include_task(task: dict) -> bool:
    """Return True if the task matches the TestEval extraction criteria."""
    difficulty = task.get("difficulty")
    task_num = task.get("task_num")
    if difficulty == 1:
        return True
    if difficulty != 1 and task_num is not None and task_num < 770:
        return True
    return False


def extract_testeval_modules(
    jsonl_path: str, output_dir: str = "data/modules_testeval"
) -> int:
    """
    Extract Python modules from a TestEval JSONL file.

    Args:
        jsonl_path: Path to the TestEval.jsonl dataset file.
        output_dir: Directory to save extracted Python modules.

    Returns:
        Number of modules written.
    """
    data_path = Path(output_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    jsonl_file = Path(jsonl_path)
    if not jsonl_file.exists():
        raise FileNotFoundError(f"Dataset file not found: {jsonl_file}")

    module_index = 0
    with jsonl_file.open("r", encoding="utf-8") as infile:
        for line_num, line in enumerate(infile, start=1):
            try:
                task = json.loads(line)
                if not should_include_task(task):
                    continue

                code = task.get("python_solution", "")
                if not code:
                    print(
                        f"Skipping line {line_num} (task_num={task.get('task_num')}): "
                        "missing python_solution"
                    )
                    continue

                module_index += 1
                output_file = data_path / f"module_{module_index:03}.py"
                output_file.write_text(code, encoding="utf-8")
                print(
                    f"Created {output_file} "
                    f"(task_num={task.get('task_num')}, difficulty={task.get('difficulty')})"
                )
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line {line_num}: {e}")
            except Exception as e:
                print(f"Error processing line {line_num}: {e}")

    if module_index != 50:
        print(
            f"Warning: expected 50 modules, wrote {module_index}. "
            "Check dataset or selection criteria."
        )

    return module_index


if __name__ == "__main__":
    extract_testeval_modules("data/TestEval.jsonl")
