"""Gemini 2.5 Flash gateway for V5 Experimental.

The gateway is deliberately optional. If the API key is absent, the call fails,
quota is exhausted, or structured validation fails after bounded retries, the
workflow can continue through deterministic fallback.
"""
import os
from dataclasses import dataclass
from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

@dataclass
class LLMCallResult:
    value: BaseModel | None
    source: str
    attempts: int
    error: str | None = None

class GeminiGateway:
    def __init__(self, model: str | None = None, max_attempts: int = 2):
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.max_attempts = max(1, max_attempts)

    def available(self) -> bool:
        return bool(os.getenv("GEMINI_API_KEY"))

    def generate_structured(self, prompt: str, schema: Type[T]) -> LLMCallResult:
        if not self.available():
            return LLMCallResult(None, "deterministic_fallback", 0, "GEMINI_API_KEY is not configured.")

        try:
            from google import genai
            from google.genai import types
        except Exception as exc:
            return LLMCallResult(None, "deterministic_fallback", 0, f"google-genai unavailable: {exc}")

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        last_error = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema,
                        temperature=0.1,
                    ),
                )
                value = schema.model_validate_json(response.text)
                return LLMCallResult(value, "gemini", attempt)
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
        return LLMCallResult(None, "deterministic_fallback", self.max_attempts, last_error)
