#!/usr/bin/env python3
"""
consolidate_tests.py

This script consolidates test files from passed modules into a single test file per module.
For modules with multiple test files (raw + repaired), it merges them by:
- Keeping the latest version of common test functions
- Keeping all unique test functions
- Combining imports

Usage:
    python -m scripts.consolidate_tests --summary-file results_summary.json --run-id run_id_3
"""

import argparse
import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple


def extract_test_functions(file_path: Path) -> Tuple[List[ast.Import | ast.ImportFrom], Dict[str, ast.FunctionDef], List[str]]:
    """
    Extract imports and test functions from a test file.
    Returns (imports, dict of function_name -> FunctionDef node, source_lines).
    """
    try:
        source = file_path.read_text(encoding="utf-8")
        source_lines = source.split("\n")
        tree = ast.parse(source)
        
        imports = []
        test_functions = {}
        
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
            elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                test_functions[node.name] = node
        
        return imports, test_functions, source_lines
    except Exception as e:
        print(f"Warning: Failed to parse {file_path}: {e}")
        return [], {}, []


def get_function_source_code(node: ast.FunctionDef, source_lines: List[str]) -> str:
    """Extract source code for a function from the original source."""
    source = "\n".join(source_lines)
    
    try:
        if hasattr(ast, "get_source_segment"):
            func_code = ast.get_source_segment(source, node)
            if func_code:
                return func_code
    except Exception:
        pass
    
    start_line_0based = node.lineno - 1
    
    if hasattr(node, "end_lineno") and node.end_lineno:
        end_line_0based_exclusive = node.end_lineno
    else:
        end_line_0based_exclusive = len(source_lines)
        if start_line_0based < len(source_lines):
            func_indent = len(source_lines[start_line_0based]) - len(source_lines[start_line_0based].lstrip())
            
            for i in range(start_line_0based + 1, len(source_lines)):
                line = source_lines[i]
                if not line.strip():
                    continue
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= func_indent:
                    end_line_0based_exclusive = i
                    break
    
    func_lines = source_lines[start_line_0based:end_line_0based_exclusive]
    return "\n".join(func_lines)


def unparse_import(import_node: ast.Import | ast.ImportFrom, source_lines: List[str] = None) -> str:
    """Convert an import node back to source code."""
    try:
        if hasattr(ast, "unparse"):
            return ast.unparse(import_node)
    except Exception:
        pass
    
    if isinstance(import_node, ast.Import):
        names = ", ".join([alias.name if alias.asname is None else f"{alias.name} as {alias.asname}" 
                          for alias in import_node.names])
        return f"import {names}"
    elif isinstance(import_node, ast.ImportFrom):
        module = import_node.module or ""
        names = ", ".join([alias.name if alias.asname is None else f"{alias.name} as {alias.asname}" 
                          for alias in import_node.names])
        level = "." * import_node.level if import_node.level > 0 else ""
        if module:
            return f"from {level}{module} import {names}"
        else:
            return f"from {level} import {names}"
    return ""


def consolidate_test_files(test_files: List[Path]) -> str:
    """
    Consolidate multiple test files into a single test file.
    For common test functions, keeps the version from the latest file.
    For unique test functions, keeps them all.
    """
    all_imports: List[Tuple[ast.Import | ast.ImportFrom, List[str]]] = []
    all_test_functions: Dict[str, Tuple[ast.FunctionDef, List[str]]] = {}
    
    for test_file in test_files:
        imports, test_functions, source_lines = extract_test_functions(test_file)
        
        for imp in imports:
            imp_str = unparse_import(imp, source_lines)
            if not any(unparse_import(existing_imp, existing_lines) == imp_str 
                      for existing_imp, existing_lines in all_imports):
                all_imports.append((imp, source_lines))
        
        for func_name, func_node in test_functions.items():
            all_test_functions[func_name] = (func_node, source_lines)
    
    lines = []
    
    import_strs = []
    for imp, source_lines in all_imports:
        imp_str = unparse_import(imp, source_lines)
        if imp_str and imp_str not in import_strs:
            import_strs.append(imp_str)
    
    for imp_str in import_strs:
        lines.append(imp_str)
    
    if lines:
        lines.append("")
    
    for func_name in sorted(all_test_functions.keys()):
        func_node, source_lines = all_test_functions[func_name]
        func_code = get_function_source_code(func_node, source_lines)
        lines.append(func_code)
        lines.append("")
    
    return "\n".join(lines).strip() + "\n"


def process_module(module_dir: Path, output_dir: Path, module_id: str = None) -> bool:
    """
    Process a single module directory.
    Returns True if a consolidated test file was created, False otherwise.
    """
    if module_id is None:
        module_id = module_dir.name
    
    metadata_file = module_dir / "metadata.json"
    
    if not metadata_file.exists():
        print(f"Warning: metadata.json not found in {module_dir}")
        return False
    
    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load metadata from {metadata_file}: {e}")
        return False
    
    if metadata.get("final_status") != "passed":
        return False
    
    if "module_id" in metadata:
        module_id = metadata["module_id"]
    
    test_files = []
    
    test_raw = module_dir / f"{module_id}_test_raw.py"
    if test_raw.exists():
        test_files.append(test_raw)
    
    repair_num = 1
    while True:
        test_repaired = module_dir / f"{module_id}_test_repaired_{repair_num}.py"
        if test_repaired.exists():
            test_files.append(test_repaired)
            repair_num += 1
        else:
            break
    
    if not test_files:
        print(f"Warning: No test files found in {module_dir}")
        return False
    
    if len(test_files) == 1:
        consolidated_content = test_files[0].read_text(encoding="utf-8")
    else:
        consolidated_content = consolidate_test_files(test_files)
    
    output_file = output_dir / f"{module_id}_test.py"
    output_file.write_text(consolidated_content, encoding="utf-8")
    
    print(f"Created consolidated test file: {output_file} ({len(test_files)} file(s))")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate test files from passed modules into a single test file per module"
    )
    parser.add_argument(
        "--summary-file",
        required=True,
        help="Path to results_summary.json file"
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Run ID (e.g., run_id_1, run_id_2, run_id_3)"
    )
    parser.add_argument(
        "--base-dir",
        default="old_runs",
        help="Base directory containing run directories (default: old_runs)"
    )
    parser.add_argument(
        "--output-dir",
        default="consolidated_tests",
        help="Output directory for consolidated tests (default: consolidated_tests)"
    )
    args = parser.parse_args()
    
    summary_file = Path(args.summary_file)
    if not summary_file.exists():
        print(f"Error: Summary file not found: {summary_file}")
        return 1
    
    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            summary_data = json.load(f)
    except Exception as e:
        print(f"Error: Failed to load summary file: {e}")
        return 1
    
    modules = summary_data.get("modules", [])
    if not modules:
        print("Warning: No modules found in summary file")
        return 1
    
    base_dir = Path(args.base_dir)
    run_id = args.run_id
    output_base = Path(args.output_dir)
    
    passed_modules = [m for m in modules if m.get("final_status") == "passed" and m.get("path")]
    
    if not passed_modules:
        print("Warning: No passed modules found in summary file")
        return 1
    
    output_dir = output_base / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    init_file = output_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("", encoding="utf-8")
    
    print(f"Processing {len(passed_modules)} passed module(s) for run_id: {run_id}")
    print(f"Output directory: {output_dir}")
    print()
    
    total_consolidated = 0
    processed_modules = set()
    
    for module in passed_modules:
        module_id = module.get("module_id")
        path = module.get("path", "")
        
        if not module_id or not path:
            continue
        
        if module_id in processed_modules:
            continue
        
        path_parts = path.split("/")
        if len(path_parts) >= 2:
            timestamp = path_parts[0]
            module_dir_name = path_parts[-2]
            module_dir = base_dir / run_id / timestamp / module_dir_name
        else:
            continue
        
        if not module_dir.exists():
            print(f"Warning: Module directory not found: {module_dir}")
            continue
        
        if process_module(module_dir, output_dir, module_id):
            total_consolidated += 1
            processed_modules.add(module_id)
    
    print()
    print(f"Total consolidated: {total_consolidated} test file(s)")
    print(f"Output saved to: {output_dir}")
    
    return 0


if __name__ == "__main__":
    exit(main())

