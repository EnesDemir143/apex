"""PostgreSQL checkpoint setup for LangGraph workflows."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from apex.core.config import settings


def checkpoint_database_url(database_url: str | None = None) -> str:
    """Return a psycopg-compatible PostgreSQL URL for checkpoint storage."""
    url = database_url or settings.database_url
    return url.replace("postgresql+asyncpg://", "postgresql://", 1)


@asynccontextmanager
async def create_checkpoint_saver(
    database_url: str | None = None,
    *,
    min_size: int = 1,
    max_size: int = 5,
) -> AsyncIterator[AsyncPostgresSaver]:
    """Yield a PostgreSQL checkpointer after LangGraph-managed setup.

    AsyncPostgresSaver.setup() auto-creates LangGraph's checkpoint tables
    (checkpoints, checkpoint_blobs, checkpoint_writes, checkpoint_migrations).
    Do not duplicate those tables in application-owned migrations.
    """
    async with AsyncConnectionPool(
        checkpoint_database_url(database_url),
        min_size=min_size,
        max_size=max_size,
        kwargs={"autocommit": True, "row_factory": dict_row},
    ) as pool:
        async with pool.connection() as conn:
            checkpointer = AsyncPostgresSaver(cast(Any, conn))
            await checkpointer.setup()
            yield checkpointer


async def setup_checkpoint_saver(database_url: str | None = None) -> AsyncPostgresSaver:
    """Create a checkpoint saver for callers that manage connection lifetime themselves."""
    pool = AsyncConnectionPool(
        checkpoint_database_url(database_url),
        min_size=1,
        max_size=1,
        kwargs={"autocommit": True, "row_factory": dict_row},
    )
    await pool.open()
    conn = await pool.getconn()
    checkpointer = AsyncPostgresSaver(cast(Any, conn))
    await checkpointer.setup()
    setattr(checkpointer, "_apex_pool", pool)
    setattr(checkpointer, "_apex_conn", conn)
    return checkpointer


async def close_checkpoint_saver(checkpointer: Any) -> None:
    """Close resources attached by setup_checkpoint_saver, if present."""
    pool = getattr(checkpointer, "_apex_pool", None)
    conn = getattr(checkpointer, "_apex_conn", None)
    if pool is not None and conn is not None:
        await pool.putconn(conn)
        await pool.close()
