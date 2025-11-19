#!/usr/bin/env python3
"""
generate_tests_ollama.py

Generate pytest-style unit tests for TinyTest modules using Small Language Models
(Phi-3, Gemma-2B, or Mistral-7B) through Ollama.

Usage:
    python scripts/test_generation.py --model llama3.2 --module data/modules/module_001.py --template few_shot
"""

import argparse
import requests
from pathlib import Path
import json
import time
from typing import Tuple

def load_template(template_key: str) -> str:
    """Load a prompt template from the prompts/*.md files.
    
    This function execs the file content in an isolated namespace and
    returns the string bound to the expected variable name.
    """
    specs = {
        "few_shot": ("few_shot.md", "FEW_SHOT_TEMPLATE_v1"),
        "structured": ("structured.md", "STRUCTURED_TEMPLATE_v1"),
        "zero_shot": ("zero_shot.md", "ZERO_SHOT_TEMPLATE_v1"),
        "auto_repair": ("auto_repair.md", "AUTO_REPAIR_TEMPLATE_v1"),
    }

    if template_key not in specs:
        raise ValueError(f"Unknown template '{template_key}'. Choose one of: {', '.join(specs)}")

    prompts_dir = Path(__file__).resolve().parents[1] / "prompts"
    filename, var_name = specs[template_key]
    file_path = prompts_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    namespace: dict = {}
    exec(content, {}, namespace)
    value = namespace.get(var_name)
    if not isinstance(value, str):
        raise ValueError(f"Expected string variable '{var_name}' in {file_path}")
    return value

def build_prompt(module_path: Path, metadata_path: Path | None = None, template: str = "few_shot") -> str:
    """Construct the test-generation prompt from code and optional metadata."""
    code = module_path.read_text(encoding="utf-8")
    
    # Extract function name from code (simple heuristic)
    function_name = None
    for line in code.split('\n'):
        if line.strip().startswith('def '):
            function_name = line.strip().split('(')[0].replace('def ', '')
            break
    
    if not function_name:
        function_name = "target_function"
    
    # Select template
    template_str = load_template(template)
    prompt = template_str.format(
        code=code,
        module_name=module_path.stem,
        function_name=function_name
    )

    # Optionally include metadata info
    if metadata_path and metadata_path.exists():
        meta = json.loads(metadata_path.read_text())
        func = meta["functions"][0]
        prompt += (
            f"\n\nHINT - Function: {func['name']}, "
            f"Args: {', '.join(a['name'] for a in func['args'])}, "
            f"Returns: {func['returns']}\n"
        )

    return prompt


def generate_with_ollama(model: str, prompt: str, seed: int | None = None, temperature: float | None = None) -> Tuple[str, dict]:
    """
    Run a local Ollama model via API and return the generated text with metadata.
    Returns: (generated_text, metadata_dict) where metadata includes tokens, time, etc.
    """
    
    url = "http://127.0.0.1:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        # "format": "json",
        "stream": False,
        "options": {}
    }
    
    # if seed is not None:
    #     payload["options"]["seed"] = seed
    if temperature is not None:
        payload["options"]["temperature"] = temperature
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, timeout=300, stream=False)
        response.raise_for_status()
        data = response.json()
        
        elapsed_time = time.time() - start_time
        
        # Extract response text
        output = data.get("response", "").strip()
        
        # If response is JSON-encoded, parse it
        if output.startswith('{') or output.startswith('['):
            try:
                parsed = json.loads(output)
                # If it's a dict, try to extract the actual code
                if isinstance(parsed, dict):
                    # Look for common keys that might contain the code
                    output = parsed.get("code") or parsed.get("test") or str(parsed)
                else:
                    output = str(parsed)
            except json.JSONDecodeError:
                pass  # Not valid JSON, use as-is
        
        output = clean_output(output)
        
        # Extract token counts and timing information
        prompt_eval_count = data.get("prompt_eval_count")
        eval_count = data.get("eval_count")
        eval_duration = data.get("eval_duration")
        total_duration = data.get("total_duration")
        load_duration = data.get("load_duration")
        prompt_eval_duration = data.get("prompt_eval_duration")
        
        # Calculate tokens per second: eval_count / eval_duration * 10^9
        tokens_per_second = None
        if eval_count is not None and eval_duration is not None and eval_duration > 0:
            tokens_per_second = (eval_count / eval_duration) * 1_000_000_000
        
        # Calculate total tokens for convenience
        total_tokens = None
        if prompt_eval_count is not None and eval_count is not None:
            total_tokens = prompt_eval_count + eval_count
        
        metadata = {
            "time": elapsed_time,
            "total_tokens": total_tokens,
            "prompt_eval_count": prompt_eval_count,
            "prompt_eval_duration": prompt_eval_duration,
            "eval_count": eval_count,
            "eval_duration": eval_duration,
            "total_duration": total_duration,
            "load_duration": load_duration,
            "tokens_per_second": tokens_per_second,
            "done_reason": data.get("done_reason"),
        }
        
        return output, metadata
        
    except requests.exceptions.RequestException as e:
        # Re-raise with more context - API is required for token counts
        raise RuntimeError(f"Failed to connect to Ollama API at {url}: {e}") from e


def clean_output(text: str) -> str:
    """Remove markdown code fences and other artifacts from SLM output."""
    lines = text.split('\n')
    cleaned = []
    in_code_block = False
    
    for line in lines:
        # Skip markdown code fence markers
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        # Skip explanatory text before first import/def
        if not cleaned and not (line.strip().startswith('from ') or line.strip().startswith('import ') or line.strip().startswith('def ')):
            continue    # skip explanatory text before first import/def             
            
        cleaned.append(line)
    
    result = '\n'.join(cleaned)
    
    # Remove trailing explanations after last test
    lines = result.split('\n')
    last_code_line = len(lines) - 1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith('assert ') or lines[i].strip().startswith('def test_'):
            last_code_line = i
            break
    
    return '\n'.join(lines[:last_code_line + 1]) + '\n'


def save_generated_test(module_path: Path, output_text: str, output_dir: Path = Path("data/generated_tests")) -> Path:
    """Save generated test code to file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{module_path.stem}_test.py"
    output_file.write_text(output_text, encoding="utf-8")
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Generate unit tests using Ollama SLMs.")
    parser.add_argument("--model", type=str, default="phi3", help="Model name (phi3, mistral, gemma, etc.)")
    parser.add_argument("--module", type=str, required=True, help="Path to Python module to analyze")
    parser.add_argument("--template", type=str, default="few_shot", 
                       choices=["few_shot", "structured", "zero_shot"],
                       help="Prompt template style")
    
    args = parser.parse_args()

    module_path = Path(args.module)
    metadata_path = Path("data/metadata") / (module_path.stem + ".json")

    if not module_path.exists():
        raise FileNotFoundError(f"Module not found: {module_path}")

    prompt = build_prompt(
        module_path, 
        metadata_path if metadata_path.exists() else None,
        template=args.template
    )
    
    print(f"Generating tests for {module_path.name} using {args.model}...")

    try:
        output, metadata = generate_with_ollama(args.model, prompt)
        test_file = save_generated_test(module_path, output)
        print(f"\n Test file saved: {test_file}")
        print(f"Run with: pytest {test_file}")
        if metadata.get("total_tokens"):
            print(f"Tokens used: {metadata['total_tokens']}")
    except Exception as e:
        print(f"Generation failed: {e}")


if __name__ == "__main__":
    main()