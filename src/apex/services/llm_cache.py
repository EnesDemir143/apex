"""Redis-backed LLM response cache."""

from __future__ import annotations

import hashlib
from datetime import date

from apex.services.cache_service import CacheService
from apex.services.llm_client import LLMClient, LLMResponse


class LLMCacheService:
    """Wrap an LLMClient with deterministic Redis response caching."""

    def __init__(self, client: LLMClient, cache: CacheService, *, ttl_seconds: int = 86_400) -> None:
        self.client = client
        self.cache = cache
        self.ttl_seconds = ttl_seconds

    async def generate(
        self,
        *,
        ticker: str,
        agent_name: str,
        prompt_version: str,
        prompt: str,
        system: str = "",
        trading_date: date | None = None,
        skip_cache: bool = False,
    ) -> LLMResponse:
        """Return a cached LLM response or generate and store it for 24h."""
        key = self.cache_key(
            ticker=ticker,
            trading_date=trading_date or date.today(),
            agent_name=agent_name,
            prompt_version=prompt_version,
        )
        if not skip_cache:
            cached = await self.cache.get(key)
            if cached is not None:
                return LLMResponse(content=cached, model="cache")

        response = await self.client.generate(prompt, system=system)
        await self.cache.set(key, response.content, ttl=self.ttl_seconds)
        return response

    @staticmethod
    def cache_key(*, ticker: str, trading_date: date, agent_name: str, prompt_version: str) -> str:
        """Build cache key = hash(ticker + date + agent_name + prompt_version)."""
        raw = f"{ticker.upper()}:{trading_date.isoformat()}:{agent_name}:{prompt_version}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"llm:{digest}"
