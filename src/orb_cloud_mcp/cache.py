"""Shared TTL cache for stable Orb Cloud API responses."""

import os

from cachetools import TTLCache

_DEFAULT_TTL = 300  # seconds


def _ttl() -> int:
    return int(os.environ.get("ORB_CLOUD_CACHE_TTL", _DEFAULT_TTL))


# Module-level cache shared across tools. Sized generously; in practice only a
# handful of organizations and their device lists will ever be stored.
cache: TTLCache = TTLCache(maxsize=256, ttl=_ttl())


def cache_key(*args: object) -> tuple:
    """Build a cache key scoped to the current API token.

    The token is hashed so it is never stored in plaintext as a dict key,
    preventing accidental exposure in logs or debug output.
    """
    return (hash(os.environ.get("ORB_CLOUD_API_KEY")), *args)
