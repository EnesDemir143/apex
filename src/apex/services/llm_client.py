"""LLM client abstractions for agent workflows."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from apex.core.config import Settings, get_settings


class LLMResponse(BaseModel):
    """Normalized LLM response with usage metadata."""

    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = Field(default=0.0, ge=0.0)


class LLMClient(ABC):
    """Abstract interface for async LLM generation."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        config: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Generate a response for the prompt."""


class OpenAIClient(LLMClient):
    """LangChain OpenAI-backed LLM client."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        config: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Generate a response using ChatOpenAI."""
        llm = ChatOpenAI(  # type: ignore[call-arg]
            model=self.settings.llm_model,
            temperature=temperature if temperature is not None else self.settings.llm_temperature,
            max_completion_tokens=max_tokens if max_tokens is not None else self.settings.llm_max_tokens,
            api_key=self.settings.openai_api_key if self.settings.openai_api_key.get_secret_value() else None,
        )
        messages: list[BaseMessage] = []
        if system:
            messages.append(SystemMessage(content=system))
        messages.append(HumanMessage(content=prompt))

        response = await llm.ainvoke(messages, config=config)
        usage = getattr(response, "usage_metadata", None) or {}
        input_tokens = int(usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("output_tokens") or 0)
        return LLMResponse(
            content=str(response.content),
            model=self.settings.llm_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=_estimate_cost_usd(input_tokens=input_tokens, output_tokens=output_tokens),
        )


class FakeLLMClient(LLMClient):
    """Deterministic LLM client for tests and local development."""

    def __init__(self, response: str = "HOLD: deterministic fake response") -> None:
        self.response = response

    async def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        config: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Return a deterministic response without external calls."""
        del prompt, system, temperature, max_tokens, config
        return LLMResponse(content=self.response, model="fake", input_tokens=0, output_tokens=0)


def _estimate_cost_usd(*, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost using conservative gpt-4o-mini-style token pricing."""
    input_cost_per_million = 0.15
    output_cost_per_million = 0.60
    return (input_tokens / 1_000_000 * input_cost_per_million) + (output_tokens / 1_000_000 * output_cost_per_million)


def parse_response_content(response: Any) -> str:
    """Convert provider response content to a plain string."""
    content = getattr(response, "content", response)
    return content if isinstance(content, str) else str(content)
