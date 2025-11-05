import ast
import re
from pathlib import Path
from typing import Optional, Tuple

from .test_generation import load_template, build_prompt, generate_with_ollama, clean_output


def extract_failing_tests(test_code: str, pytest_log: str) -> str:
    """
    Extract only the failing test functions from the test code based on pytest log.
    Returns test code containing only the failing test functions + imports.
    """
    # Extract failing test names from pytest log
    failing_test_names = set()
    
    # Look for FAILED lines: "FAILED runs/.../module.py::test_name"
    for line in pytest_log.split('\n'):
        if 'FAILED' in line:
            # Pattern: FAILED path/to/file.py::test_function_name
            match = re.search(r'::(test_[a-zA-Z0-9_]+)', line)
            if match:
                failing_test_names.add(match.group(1))
    
    # Also check for test names in error tracebacks
    # Pattern: "def test_name():" in traceback
    in_traceback = False
    for line in pytest_log.split('\n'):
        if 'Traceback' in line or 'AssertionError' in line:
            in_traceback = True
        if in_traceback and 'def test_' in line:
            match = re.search(r'def\s+(test_[a-zA-Z0-9_]+)', line)
            if match:
                failing_test_names.add(match.group(1))
    
    if not failing_test_names:
        # If we can't extract, return all test code (fallback)
        return test_code
    
    # Parse test code to extract only failing tests
    try:
        tree = ast.parse(test_code)
        lines = test_code.split('\n')
        result_lines = []
        
        # Walk through module body in order (preserves order)
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
                result_lines.extend(lines[start_line:end_line])
                if result_lines and result_lines[-1] != '':
                    result_lines.append('')
            elif isinstance(node, ast.FunctionDef) and node.name in failing_test_names:
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
                result_lines.extend(lines[start_line:end_line])
                result_lines.append('')
        
        result = '\n'.join(result_lines).strip()
        return result + '\n' if result else test_code
    except Exception:
        # Fallback: return original if parsing fails
        return test_code


def build_repair_prompt(
    module_path: Path,
    full_test_code: str,
    pytest_log: str,
    template_key: str = "auto_repair"
) -> str:
    code = module_path.read_text(encoding="utf-8")

    # Extract function name
    function_name = None
    for line in code.split("\n"):
        if line.strip().startswith("def "):
            function_name = line.strip().split("(")[0].replace("def ", "")
            break
    if not function_name:
        function_name = "target_function"

    # Extract only failing tests
    failing_tests = extract_failing_tests(full_test_code, pytest_log)

    template = load_template(template_key)
    prompt = template.format(
        code=code,
        module_name=module_path.stem,
        function_name=function_name,
        failing_tests=failing_tests,
        pytest_log=pytest_log,
    )
    return prompt


def auto_repair(
    model: str,
    module_path: Path,
    failing_test_path: Path,
    pytest_log: str,
    seed: int | None = None,
    temperature: float | None = None,
) -> Tuple[str, dict]:
    """
    Repair failing tests. Returns (repaired_code, metadata).
    Only the failing tests are passed to the model for repair.
    """
    full_test_code = failing_test_path.read_text(encoding="utf-8")
    prompt = build_repair_prompt(
        module_path=module_path,
        full_test_code=full_test_code,
        pytest_log=pytest_log,
    )
    output, metadata = generate_with_ollama(model, prompt, seed=seed, temperature=temperature)
    return output, metadata


