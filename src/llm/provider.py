from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import re
from pydantic import BaseModel


class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_used: Optional[int] = None
    metadata: Dict[str, Any] = {}


class BaseLLMProvider(ABC):
    """Abstract base class for LLM generation providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate response given user prompt and system prompt."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """Rule & context-aware mock LLM provider for zero-dependency local execution."""

    def __init__(self, model_name: str = "mock-llm-v1"):
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        # Extract context block if embedded in prompt
        context_match = re.search(r"Context Information:(.*?)(?:Question:|Query:|$)", prompt, re.DOTALL | re.IGNORECASE)
        context_text = context_match.group(1).strip() if context_match else ""

        query_match = re.search(r"(?:Question|Query):\s*(.*)", prompt, re.IGNORECASE)
        query = query_match.group(1).strip() if query_match else prompt

        if not context_text or "No relevant context found" in context_text:
            content = f"Based on the provided knowledge repository, I could not find relevant information to answer your question: '{query}'."
        else:
            # Extract key sentences from context
            sentences = [s.strip() for s in re.split(r"[.\n]+", context_text) if len(s.strip()) > 15]
            summary_points = sentences[:3] if sentences else [context_text[:200]]

            content = (
                f"Based on the retrieved enterprise documentation:\n\n"
                + "\n".join([f"• {point}." for point in summary_points])
                + f"\n\n(Generated locally via MockLLMProvider based on grounded context)."
            )

        return LLMResponse(
            content=content,
            model=self.model_name,
            tokens_used=len(prompt.split()) + len(content.split()),
            metadata={"provider": "mock", "is_mock": True},
        )


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI Chat Completion provider integration."""

    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        if not self.api_key:
            print("[Warning] OpenAI API Key missing. Falling back to MockLLMProvider.")
            return MockLLMProvider().generate(prompt, system_prompt)

        try:
            import httpx
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.2,
            }
            resp = httpx.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()

            answer = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", None)

            return LLMResponse(
                content=answer,
                model=self.model_name,
                tokens_used=tokens,
                metadata={"provider": "openai"},
            )
        except Exception as e:
            print(f"[Error] OpenAI API call failed ({e}). Falling back to Mock LLM Provider.")
            return MockLLMProvider().generate(prompt, system_prompt)


class OllamaLLMProvider(BaseLLMProvider):
    """Local Ollama LLM provider integration."""

    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama2"):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        try:
            import httpx
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
            }
            resp = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=60.0)
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("response", "")

            return LLMResponse(
                content=answer,
                model=self.model_name,
                metadata={"provider": "ollama"},
            )
        except Exception as e:
            print(f"[Error] Ollama connection failed ({e}). Falling back to Mock LLM Provider.")
            return MockLLMProvider().generate(prompt, system_prompt)


class LLMProviderFactory:
    """Factory for resolving LLM providers."""

    @staticmethod
    def get_provider(
        provider_type: str = "mock",
        model_name: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        ollama_url: str = "http://localhost:11434",
    ) -> BaseLLMProvider:
        provider_type = provider_type.lower()
        if provider_type == "openai":
            if not api_key:
                print("[Warning] No OpenAI API Key found. Defaulting to Mock LLM Provider.")
                return MockLLMProvider()
            return OpenAILLMProvider(api_key=api_key, model_name=model_name)
        elif provider_type == "ollama":
            return OllamaLLMProvider(base_url=ollama_url, model_name=model_name)
        elif provider_type == "mock":
            return MockLLMProvider(model_name=model_name)
        else:
            return MockLLMProvider(model_name=model_name)
