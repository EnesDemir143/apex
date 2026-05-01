"""RAG pipeline using Nomic embeddings and pgvector cosine search."""

from __future__ import annotations

from typing import Any

import structlog
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from apex.core.config import settings
from apex.infrastructure_layer.models.embedding import Embedding

logger = structlog.get_logger(__name__)


class RAGPipeline:
    """Retrieve top-K documents for a query using pgvector cosine similarity.

    Embedding is model-agnostic: the model name and dimension are read from
    Settings (default: nomic-embed-text-v2, 768-dim).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def embed_text(self, text_input: str) -> list[float]:
        """Return a vector embedding for *text_input*.

        In production this calls the configured embedding model.  For the
        current stub it returns a zero-vector of the configured dimension so
        the pipeline is exercisable without a live model endpoint.
        """
        logger.debug("rag.embed", model=settings.embedding_model, dim=settings.embedding_dim)
        # Stub: zero-vector — replace with real model call (e.g. ollama / OpenAI)
        return [0.0] * settings.embedding_dim

    async def search_similar(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """Return the top-K most similar documents to *query* using cosine distance (<=>)."""
        query_vec = await self.embed_text(query)
        vec_literal = "[" + ",".join(str(v) for v in query_vec) + "]"

        stmt = (
            select(
                Embedding.id,
                Embedding.content,
                Embedding.content_type,
                Embedding.metadata_,
                text(f"embedding <=> '{vec_literal}'::vector AS distance"),
            )
            .where(Embedding.embedding.is_not(None))
            .order_by(text("distance"))
            .limit(k)
        )

        result = await self._session.execute(stmt)
        rows = result.mappings().all()
        logger.info("rag.search", query_len=len(query), k=k, hits=len(rows))
        return [dict(r) for r in rows]
