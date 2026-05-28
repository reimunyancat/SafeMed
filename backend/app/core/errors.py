"""Custom application errors."""
from __future__ import annotations


class SafeMedError(Exception):
    """Base SafeMed exception."""


class DataFetchError(SafeMedError):
    """External data source could not be reached."""


class DataParseError(SafeMedError):
    """External data could not be parsed."""


class ConfigError(SafeMedError):
    """Configuration is invalid or missing required fields."""


class LLMUnavailableError(SafeMedError):
    """LLM provider could not be reached or returned an empty response."""
