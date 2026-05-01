"""Redis-backed dead letter queue for failed analysis messages."""

from __future__ import annotations

import json
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

DLQ_KEY = "apex:dlq"


class DeadLetterQueue:
    """Push failed messages to Redis and retry them later.

    Messages are stored as JSON strings in a Redis list (RPUSH / LPOP).
    """

    def __init__(self, redis: Any) -> None:
        self._redis = redis

    async def push(self, message: dict[str, Any]) -> None:
        """Append *message* to the dead letter queue."""
        payload = json.dumps(message)
        await self._redis.rpush(DLQ_KEY, payload)
        logger.warning("dlq.push", key=DLQ_KEY, message_keys=list(message.keys()))

    async def pop(self) -> dict[str, Any] | None:
        """Remove and return the oldest message, or None if the queue is empty."""
        raw = await self._redis.lpop(DLQ_KEY)
        if raw is None:
            return None
        return json.loads(raw)  # type: ignore[no-any-return]

    async def retry_all(self) -> list[dict[str, Any]]:
        """Drain the queue and return all messages for re-processing.

        Callers are responsible for re-submitting each message to the workflow.
        """
        messages: list[dict[str, Any]] = []
        while True:
            msg = await self.pop()
            if msg is None:
                break
            messages.append(msg)
        logger.info("dlq.retry_all", count=len(messages))
        return messages

    async def length(self) -> int:
        """Return the current queue depth."""
        return int(await self._redis.llen(DLQ_KEY))
