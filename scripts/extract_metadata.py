# scripts/extract_metadata.py

"""
extract_metadat.py

This script extracts metadata of generated modules from the HumanEval dataset (HumanEval.jsonl).
It reads each Python module file, analyzes its structure using the ast module,
and writes the metadata (function signatures, docstrings, imports, etc.) to a JSON file.

Output:
    data/metadata/module_001.json
    data/metadata/module_002.json
    ...
"""

import ast
import json
from pathlib import Path


def analyze_module(file_path: Path) -> dict:
    """Extract function signatures, docstrings, and metadata from a Python module."""
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    module_info = {
        "module_name": file_path.name,
        "path": str(file_path),
        "num_functions": 0,
        "num_classes": 0,
        "imports": [],
        "functions": [],
    }

    # Walk the AST
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            module_info["imports"].extend([alias.name for alias in node.names])

        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            module_info["imports"].extend([f"{mod}.{alias.name}" for alias in node.names])

        elif isinstance(node, ast.ClassDef):
            module_info["num_classes"] += 1

        elif isinstance(node, ast.FunctionDef):
            module_info["num_functions"] += 1

            args = []
            for arg in node.args.args:
                arg_type = None
                if arg.annotation:
                    arg_type = ast.unparse(arg.annotation)
                args.append({"name": arg.arg, "type": arg_type})

            return_type = ast.unparse(node.returns) if node.returns else None
            docstring = ast.get_docstring(node) or ""

            module_info["functions"].append({
                "name": node.name,
                "args": args,
                "returns": return_type,
                "docstring": docstring.strip(),
                "start_line": getattr(node, "lineno", None),
                "end_line": getattr(node, "end_lineno", None)
            })

    return module_info


def main():
    modules_path = Path("data/modules")
    output_path = Path("data/metadata")
    output_path.mkdir(parents=True, exist_ok=True)

    for file_path in modules_path.glob("*.py"):
        try:
            result = analyze_module(file_path)
            output_file = output_path / f"{file_path.stem}.json"
            output_file.write_text(json.dumps(result, indent=2))
            print(f"Extracted metadata for {file_path.name}")
        except Exception as e:
            print(f"Failed to analyze {file_path.name}: {e}")


if __name__ == "__main__":
    main()
