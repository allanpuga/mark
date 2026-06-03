"""Normalize MySQL connection env vars to strip accidental whitespace.

Parses DB_URL, REFLEX_DB_URL and REFLEX_ASYNC_DB_URL with urllib.parse,
strips whitespace from username, password, host, port and database name,
and rewrites the env vars in place. Preserves driver (pymysql/aiomysql)
and query string. Never logs credentials.
"""

import os
import logging
from urllib.parse import urlsplit, urlunsplit, quote, unquote

_NORMALIZED = False
_TARGET_VARS = ("DB_URL", "REFLEX_DB_URL", "REFLEX_ASYNC_DB_URL")


def _strip(s: str | None) -> str:
    if s is None:
        return ""
    return s.strip().strip("\t\r\n ")


def _normalize_url(url: str) -> str:
    """Normalize a single connection URL. Returns original on parse failure."""
    if not url:
        return url
    raw = url.strip()
    try:
        parts = urlsplit(raw)
        scheme = parts.scheme.strip()
        if not scheme or "@" not in parts.netloc and "/" not in raw:
            return raw

        username = unquote(parts.username) if parts.username else ""
        password = unquote(parts.password) if parts.password else ""
        host = parts.hostname or ""
        port = parts.port

        username = _strip(username)
        password = _strip(password)
        host = _strip(host)

        path = parts.path or ""
        if path.startswith("/"):
            db_name = _strip(path[1:])
            new_path = "/" + db_name if db_name else ""
        else:
            new_path = path

        userinfo = ""
        if username:
            userinfo = quote(username, safe="")
            if password:
                userinfo += ":" + quote(password, safe="")
            userinfo += "@"

        netloc = userinfo + host
        if port is not None:
            netloc += f":{port}"

        new_url = urlunsplit(
            (scheme, netloc, new_path, parts.query, parts.fragment)
        )
        return new_url
    except Exception:
        logging.exception("db_env: failed to normalize a connection URL")
        return raw


def normalize_db_env(force: bool = False) -> bool:
    """Normalize DB connection env vars. Idempotent."""
    global _NORMALIZED
    if _NORMALIZED and not force:
        return True
    changed_any = False
    for var in _TARGET_VARS:
        current = os.environ.get(var)
        if not current:
            continue
        normalized = _normalize_url(current)
        if normalized != current:
            os.environ[var] = normalized
            changed_any = True
    _NORMALIZED = True
    logging.info(
        "db_env: connection env vars normalized (changed=%s)", changed_any
    )
    return True


# Apply on import so any subsequent rx.asession() use is safe.
normalize_db_env()


# Alias for compatibility with alternate naming used by callers.
def normalize_db_envs(force: bool = False) -> bool:
    """Alias for normalize_db_env, preserved for compatibility."""
    return normalize_db_env(force=force)