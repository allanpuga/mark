"""Compatibility patch for SQLAlchemy + aiomysql ping signature mismatch.

SQLAlchemy's async adapter for aiomysql may call `connection.ping()` without
the required `reconnect` positional argument expected by some aiomysql
versions, raising a TypeError at connection checkout. This module applies an
idempotent monkeypatch that wraps the adapter's `ping` method to always pass
`reconnect`, preserving normal behavior for both pymysql and aiomysql.

The patch is safe to import multiple times and logs only non-sensitive
diagnostics (class names and a status flag). Credentials and connection
strings are never read or logged.
"""

import logging

_PATCH_APPLIED = False


def apply_aiomysql_ping_patch() -> bool:
    """Apply the aiomysql ping compatibility patch. Idempotent."""
    global _PATCH_APPLIED
    if _PATCH_APPLIED:
        return True
    try:
        from sqlalchemy.dialects.mysql import aiomysql as sa_aiomysql

        adapter_cls = getattr(
            sa_aiomysql, "AsyncAdapt_aiomysql_connection", None
        )
        if adapter_cls is None:
            logging.info(
                "aiomysql_ping_patch: adapter class not found, skipping"
            )
            _PATCH_APPLIED = True
            return False

        original_ping = adapter_cls.ping

        if getattr(original_ping, "_reconnect_patch_applied", False):
            _PATCH_APPLIED = True
            return True

        def patched_ping(self, reconnect=False):
            return original_ping(self, reconnect)

        patched_ping._reconnect_patch_applied = True
        adapter_cls.ping = patched_ping

        _PATCH_APPLIED = True
        logging.info("aiomysql_ping_patch: applied to %s", adapter_cls.__name__)
        return True
    except ImportError:
        logging.info(
            "aiomysql_ping_patch: SQLAlchemy aiomysql dialect not available"
        )
        _PATCH_APPLIED = True
        return False
    except Exception as e:
        logging.exception(
            "aiomysql_ping_patch: unexpected error applying patch: %s",
            type(e).__name__,
        )
        return False


# Apply immediately on import so any subsequent rx.asession() use is safe.
apply_aiomysql_ping_patch()