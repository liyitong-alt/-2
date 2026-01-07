from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class LLMResponse:
    content: str


class BaseProvider:
    def generate(self, prompt: str, temperature: float = 0.2) -> LLMResponse:
        raise NotImplementedError


class MockProvider(BaseProvider):
    def generate(self, prompt: str, temperature: float = 0.2) -> LLMResponse:
        del temperature
        lines = ["Mock response:", prompt[:400]]
        return LLMResponse(content="\n".join(lines))


class OpenAIProvider(BaseProvider):
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.api_key = api_key
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate(self, prompt: str, temperature: float = 0.2) -> LLMResponse:
        import json
        import urllib.request

        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        return LLMResponse(content=content)


def get_provider() -> BaseProvider:
    provider_name = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider_name == "openai":
        return OpenAIProvider()
    return MockProvider()
