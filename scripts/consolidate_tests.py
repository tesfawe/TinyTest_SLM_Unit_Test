#!/usr/bin/env python3
"""
consolidate_tests.py

This script consolidates test files from modules into a single test file per module.
It collects passed tests from all attempts (raw + repaired), even if the module ultimately failed.
For modules with multiple test files, it merges them by:
- Keeping the latest version of common test functions (if passed)
- Keeping all unique test functions (if passed)
- Combining imports

Usage:
    python -m scripts.consolidate_tests --summary-file results_summary.json --run-id run_id_3
"""

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


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


def parse_pytest_log(log_path: Path) -> Set[str]:
    """
    Parse pytest log to identify failed tests.
    Returns a set of failed test function names.
    """
    failed_tests = set()
    if not log_path.exists():
        return failed_tests

    try:
        content = log_path.read_text(encoding="utf-8")
        # Look for lines like "FAILED path/to/test.py::test_function_name"
        # or "FAILED path/to/test.py::test_function_name - AssertionError..."
        # Regex to capture the function name after ::
        matches = re.findall(r"::(test_\w+)", content)
        failed_tests.update(matches)
        
        # Also check for "FAILED" lines in the short summary info at the bottom
        # FAILED runs/.../test.py::test_function_name
        summary_matches = re.findall(r"FAILED .+?::(test_\w+)", content)
        failed_tests.update(summary_matches)
        
    except Exception as e:
        print(f"Warning: Failed to parse log {log_path}: {e}")
    
    return failed_tests


def process_module(module_dir: Path, output_dir: Path, module_id: str = None) -> bool:
    """
    Process a single module directory.
    Returns True if a consolidated test file was created, False otherwise.
    """
    if module_id is None:
        module_id = module_dir.name
    
    # Collect all test files and their corresponding logs
    test_files_info = [] # List of (test_file_path, log_file_path)
    
    # Check raw test
    test_raw = module_dir / f"{module_id}_test_raw.py"
    log_raw = module_dir / "pytest_log.txt"
    if test_raw.exists():
        test_files_info.append((test_raw, log_raw))
    
    # Check repaired tests
    repair_num = 1
    while True:
        test_repaired = module_dir / f"{module_id}_test_repaired_{repair_num}.py"
        log_repaired = module_dir / f"pytest_log_retry_{repair_num}.txt"
        if test_repaired.exists():
            test_files_info.append((test_repaired, log_repaired))
            repair_num += 1
        else:
            break
    
    if not test_files_info:
        # print(f"Warning: No test files found in {module_dir}")
        return False

    all_imports: List[Tuple[ast.Import | ast.ImportFrom, List[str]]] = []
    all_test_functions: Dict[str, Tuple[ast.FunctionDef, List[str]]] = {}
    
    has_passed_tests = False

    for test_file, log_file in test_files_info:
        imports, test_functions, source_lines = extract_test_functions(test_file)
        failed_tests = parse_pytest_log(log_file)
        
        # Collect imports
        for imp in imports:
            imp_str = unparse_import(imp, source_lines)
            if not any(unparse_import(existing_imp, existing_lines) == imp_str 
                      for existing_imp, existing_lines in all_imports):
                all_imports.append((imp, source_lines))
        
        # Collect passed test functions
        for func_name, func_node in test_functions.items():
            if func_name not in failed_tests:
                all_test_functions[func_name] = (func_node, source_lines)
                has_passed_tests = True
    
    if not has_passed_tests:
        return False

    # Generate consolidated content
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
    
    consolidated_content = "\n".join(lines).strip() + "\n"
    
    output_file = output_dir / f"{module_id}_test.py"
    output_file.write_text(consolidated_content, encoding="utf-8")
    
    # print(f"Created consolidated test file: {output_file} (from {len(test_files_info)} attempt(s))")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate test files from modules into a single test file per module"
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
        default="all_runs",
        help="Base directory containing run directories (default: all_runs)"
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
    
    # Process ALL modules that have a path, regardless of status
    target_modules = [m for m in modules if m.get("path")]
    
    if not target_modules:
        print("Warning: No modules with paths found in summary file")
        return 1
    
    output_dir = output_base / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    init_file = output_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("", encoding="utf-8")
    
    print(f"Processing {len(target_modules)} modules for run_id: {run_id}")
    print(f"Output directory: {output_dir}")
    print()
    
    total_consolidated = 0
    processed_modules = set()
    
    for module in target_modules:
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
            # print(f"Warning: Module directory not found: {module_dir}")
            continue

        metadata_file = module_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                if metadata.get("final_status") == "ran":
                    # Skip modules with final_status="ran"
                    continue
            except Exception as e:
                # If we can't read metadata, continue processing (don't skip)
                pass
        
        if process_module(module_dir, output_dir, module_id):
            total_consolidated += 1
            processed_modules.add(module_id)
            # print(f"Consolidated {module_id}")
    
    print()
    print(f"Total consolidated: {total_consolidated} test file(s)")
    print(f"Output saved to: {output_dir}")
    
    return 0


if __name__ == "__main__":
    exit(main())

