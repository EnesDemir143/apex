# ADR-004: Redis 8 over Redis Stack

**Date:** 2026-04-28
**Deciders:** Apex engineering team

## Status

Accepted

## Context

Apex uses Redis for:
- LLM response caching (TTL-based key/value)
- Circuit breaker state (OPEN/CLOSED/HALF_OPEN counters)
- Dead letter queue (Redis list `apex:dlq`)
- Distributed locks (`redis.lock()`)
- Rate limiter token buckets

Previously, Redis Stack was the recommended distribution for projects needing RediSearch, RedisJSON, and RedisTimeSeries modules. In 2025, Redis Stack was deprecated and its modules were merged into Redis core.

Options considered:
- **Redis Stack (deprecated)**: Separate Docker image, modules as plugins — deprecated as of Redis 8
- **Redis 8**: All modules bundled in core; `redis:8-alpine` is the official image
- **Valkey**: Redis fork; compatible API but different release cadence and community

## Decision

Use **Redis 8** (`redis:8-alpine`) as the sole cache and message broker.

All previously Redis Stack-only features (JSON, Search, TimeSeries) are available in Redis 8 core. The `redis.asyncio` Python client is used throughout with `decode_responses=True`.

## Consequences

**Positive:**
- Single official image — no custom Docker builds or plugin management
- `redis:8-alpine` is ~30MB vs ~200MB for Redis Stack
- All modules available without extra configuration
- `redis.asyncio` client is fully compatible

**Negative:**
- Redis 8 is a relatively new release — some edge cases may surface before it reaches the maturity of Redis 7.x
- Valkey compatibility not tested — migration would require API audit

**Note:** The distributed lock uses `redis.lock()` (Redlock-compatible single-node implementation). For multi-node HA, upgrade to Redlock with 3+ Redis nodes.
