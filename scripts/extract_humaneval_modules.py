# scripts/extract_humaneval_modules.py

"""
extract_humaneval_modules.py

This script extracts Python code modules from the HumanEval dataset (HumanEval.jsonl).
It reads each JSON line, combines the 'prompt' (function header and docstring)
with the 'canonical_solution' (function body), and writes the result as a .py file.

Output:
    data/modules/module_001.py
    data/modules/module_002.py
    ...
"""

import json
from pathlib import Path


def extract_humaneval_modules(jsonl_path: str, output_dir: str = "data/modules") -> None:
    """
    Extract Python modules from a HumanEval-style JSONL file.

    Args:
        jsonl_path (str): Path to the HumanEval.jsonl dataset file.
        output_dir (str): Directory to save extracted Python modules.
    """
    data_path = Path(output_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    jsonl_file = Path(jsonl_path)
    if not jsonl_file.exists():
        raise FileNotFoundError(f"Dataset file not found: {jsonl_file}")

    with jsonl_file.open("r", encoding="utf-8") as infile:
        for i, line in enumerate(infile, start=1):
            try:
                task = json.loads(line)
                prompt = task.get("prompt", "")
                solution = task.get("canonical_solution", "")
                code = f"{prompt}{solution}"

                output_file = data_path / f"module_{i:03}.py"
                output_file.write_text(code, encoding="utf-8")

                print(f"Created {output_file}")
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line {i}: {e}")
            except Exception as e:
                print(f"Error processing line {i}: {e}")


if __name__ == "__main__":
    extract_humaneval_modules("data/HumanEval.jsonl")
