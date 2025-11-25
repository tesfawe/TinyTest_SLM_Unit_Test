import os
import time
import json
import requests
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, model: str, seed: Optional[int] = None, temperature: Optional[float] = None) -> Tuple[str, dict]:
        pass

class OllamaProvider(LLMProvider):
    def generate(self, prompt: str, model: str, seed: Optional[int] = None, temperature: Optional[float] = None) -> Tuple[str, dict]:
        url = "http://127.0.0.1:11434/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {}
        }
        
        if temperature is not None:
            payload["options"]["temperature"] = temperature
        
        start_time = time.time()
        
        try:
            response = requests.post(url, json=payload, timeout=300, stream=False)
            response.raise_for_status()
            data = response.json()
            
            elapsed_time = time.time() - start_time
            
            output = data.get("response", "").strip()
            
            # If response is JSON-encoded, parse it
            if output.startswith('{') or output.startswith('['):
                try:
                    parsed = json.loads(output)
                    if isinstance(parsed, dict):
                        output = parsed.get("code") or parsed.get("test") or str(parsed)
                    else:
                        output = str(parsed)
                except json.JSONDecodeError:
                    pass
            
            output = self._clean_output(output)
            
            metadata = {
                "time": elapsed_time,
                "total_tokens": (data.get("prompt_eval_count") or 0) + (data.get("eval_count") or 0),
                "prompt_eval_count": data.get("prompt_eval_count"),
                "eval_count": data.get("eval_count"),
                "eval_duration": data.get("eval_duration"),
                "total_duration": data.get("total_duration"),
                "load_duration": data.get("load_duration"),
                "done_reason": data.get("done_reason"),
            }
            
            return output, metadata
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to connect to Ollama API at {url}: {e}") from e

    def _clean_output(self, text: str) -> str:
        """Remove markdown code fences and other artifacts."""
        lines = text.split('\n')
        cleaned = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if not cleaned and not (line.strip().startswith('from ') or line.strip().startswith('import ') or line.strip().startswith('def ')):
                continue
                
            cleaned.append(line)
        
        result = '\n'.join(cleaned)
        
        lines = result.split('\n')
        last_code_line = len(lines) - 1
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().startswith('assert ') or lines[i].strip().startswith('def test_'):
                last_code_line = i
                break
        
        return '\n'.join(lines[:last_code_line + 1]) + '\n'

class GeminiProvider(LLMProvider):
    def generate(self, prompt: str, model: str, seed: Optional[int] = None, temperature: Optional[float] = None) -> Tuple[str, dict]:
        from google import genai
        from google.genai import types
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
            
        client = genai.Client(api_key=api_key)
        
        config = types.GenerateContentConfig(
            temperature=temperature if temperature is not None else 0.7,
        )
        if seed is not None:
            config.seed = seed

        start_time = time.time()
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        elapsed_time = time.time() - start_time
        
        output = response.text
        output = self._clean_output(output)
        
        metadata = {
            "time": elapsed_time,
            "total_tokens": response.usage_metadata.total_token_count if response.usage_metadata else None,
            "prompt_eval_count": response.usage_metadata.prompt_token_count if response.usage_metadata else None,
            "eval_count": response.usage_metadata.candidates_token_count if response.usage_metadata else None,
        }
        
        return output, metadata

    def _clean_output(self, text: str) -> str:
        # Reuse similar cleaning logic or adapt as needed
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            if line.strip().startswith('```'):
                continue
            cleaned.append(line)
        return '\n'.join(cleaned)

class OpenAIProvider(LLMProvider):
    def generate(self, prompt: str, model: str, seed: Optional[int] = None, temperature: Optional[float] = None) -> Tuple[str, dict]:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        client = OpenAI(api_key=api_key)
        
        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature if temperature is not None else 0.7,
            seed=seed
        )
        elapsed_time = time.time() - start_time
        
        output = response.choices[0].message.content
        output = self._clean_output(output)
        
        metadata = {
            "time": elapsed_time,
            "total_tokens": response.usage.total_tokens,
            "prompt_eval_count": response.usage.prompt_tokens,
            "eval_count": response.usage.completion_tokens,
        }
        
        return output, metadata

    def _clean_output(self, text: str) -> str:
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            if line.strip().startswith('```'):
                continue
            cleaned.append(line)
        return '\n'.join(cleaned)

def get_provider(provider_name: str) -> LLMProvider:
    if provider_name.lower() == "ollama":
        return OllamaProvider()
    elif provider_name.lower() == "gemini":
        return GeminiProvider()
    elif provider_name.lower() == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
