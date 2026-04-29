"""Custom exception hierarchy for Apex."""

from __future__ import annotations


class ApexError(Exception):
    """Base class for application-level errors."""


class LLMBudgetExceededError(ApexError):
    """Raised when an LLM request would exceed the configured budget."""


class DataFetchError(ApexError):
    """Raised when market data cannot be fetched or validated."""


class AgentError(ApexError):
    """Raised when an analysis agent fails."""


class ConfigError(ApexError):
    """Raised when application configuration is invalid."""
