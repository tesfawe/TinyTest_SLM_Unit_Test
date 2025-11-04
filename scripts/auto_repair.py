from pathlib import Path
from typing import Optional

from .test_generation import load_template, build_prompt, generate_with_ollama, clean_output


def build_repair_prompt(
    module_path: Path,
    failing_test_code: str,
    pytest_log: str,
    template_key: str = "auto_repair"
) -> str:
    code = module_path.read_text(encoding="utf-8")

    # Reuse function name extraction from build_prompt
    base_prompt = build_prompt(module_path, None, template="zero_shot")  # ensure function_name resolved
    # We only need module_name and function_name from that path; rebuild via template
    function_name = None
    for line in code.split("\n"):
        if line.strip().startswith("def "):
            function_name = line.strip().split("(")[0].replace("def ", "")
            break
    if not function_name:
        function_name = "target_function"

    template = load_template(template_key)
    prompt = template.format(
        code=code,
        module_name=module_path.stem,
        function_name=function_name,
        previous_test=failing_test_code,
        pytest_log=pytest_log,
    )
    return prompt


def auto_repair(
    model: str,
    module_path: Path,
    failing_test_path: Path,
    pytest_log: str,
) -> str:
    failing_test_code = failing_test_path.read_text(encoding="utf-8")
    prompt = build_repair_prompt(
        module_path=module_path,
        failing_test_code=failing_test_code,
        pytest_log=pytest_log,
    )
    output = generate_with_ollama(model, prompt)
    return clean_output(output)


