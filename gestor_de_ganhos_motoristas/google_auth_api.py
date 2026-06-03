"""Backend HTTP route to finalize Google OAuth without depending on Reflex on_load.

This module exposes /api/auth/google/exchange that:
  1. Receives ?code=...&state=... from Google's redirect.
  2. Exchanges the code for tokens using GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET
     and the canonical redirect_uri https://markup.movinmapp.com.br/auth/google/callback.
  3. Fetches userinfo, ensures the schema, creates or finds the user/profile.
  4. Stores a short-lived one-time token (OTT) in memory.
  5. Redirects to /auth/google/finalize?ott=... where the Reflex frontend
     finalizes the session by reading the OTT.

This avoids hanging on the Reflex websocket on_load roundtrip.

IMPORTANT: This module normalizes DB connection env vars and applies the
aiomysql ping compatibility patch at import time, BEFORE any use of
rx.asession. This guarantees the OAuth callback works even when this
module is loaded directly (e.g., via the FastAPI route) without going
through the main app initialization path.
"""

# Normalize DB env vars and apply aiomysql patch BEFORE any DB access.
# This must happen at import time and before any rx.asession is used.
from gestor_de_ganhos_motoristas.db_env import normalize_db_env, normalize_db_envs

normalize_db_env(force=True)
normalize_db_envs(force=True)

from gestor_de_ganhos_motoristas.db_compat import apply_aiomysql_ping_patch

apply_aiomysql_ping_patch()

import os
import uuid
import logging
import urllib.parse
import bcrypt
import httpx
from sqlalchemy import text
from fastapi.responses import RedirectResponse

from gestor_de_ganhos_motoristas.cache import TTLCache


google_auth_tokens = TTLCache()


GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:3000/auth/google/callback",
)


async def google_start_handler() -> RedirectResponse:
    """Backend-side handler that builds the Google OAuth URL and 302s to it.

    Reads GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET from the backend environment
    so the URL is never built at frontend render time. If credentials are
    missing, redirects back to the public landing with a clear error code.
    """
    try:
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        if not client_id or not client_secret:
            return _safe_redirect("/?google_error=not_configured")

        state_val = str(uuid.uuid4())
        params = {
            "client_id": client_id,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",
            "state": state_val,
        }
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urllib.parse.urlencode(params)
        )
        return _safe_redirect(auth_url)
    except Exception:
        logging.exception("google_start_handler: unexpected failure")
        return _safe_redirect("/?google_error=start_error")


def _safe_redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=302)


_SCHEMA_ENSURED = False


async def _ensure_schema() -> None:
    """Idempotent schema guard for legacy databases.

    For each table, fetches SHOW COLUMNS once, then only runs ALTER TABLE
    statements for columns that are actually missing. This avoids
    triggering MySQL "Duplicate column" errors and the noisy stack traces
    they used to produce.

    Never raises to the caller; any unexpected error is logged at INFO
    level (no credentials) and ignored so the OAuth flow can proceed.
    """
    global _SCHEMA_ENSURED
    if _SCHEMA_ENSURED:
        return

    # Re-assert env normalization and aiomysql patch at call time as a
    # defensive guard. Both helpers are idempotent.
    normalize_db_env()
    normalize_db_envs()
    apply_aiomysql_ping_patch()

    import reflex as rx

    required_columns: dict[str, list[tuple[str, str]]] = {
        "users": [
            ("is_admin", "TINYINT(1) DEFAULT 0"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ],
        "profiles": [
            ("nome", "VARCHAR(255) DEFAULT ''"),
            ("email", "VARCHAR(255) DEFAULT ''"),
            ("whatsapp", "VARCHAR(50) DEFAULT ''"),
            ("estado", "VARCHAR(2) DEFAULT ''"),
            ("cidade", "VARCHAR(255) DEFAULT ''"),
            ("dias_semana", "INT DEFAULT 6"),
            ("horas_dia", "INT DEFAULT 8"),
            ("km_dia", "FLOAT DEFAULT 150.0"),
            ("veiculo_ativo_id", "VARCHAR(36) DEFAULT ''"),
        ],
        "vehicles": [
            ("categorias", "TEXT"),
            ("valor_aluguel_semana", "FLOAT DEFAULT 0"),
            ("valor_parcela", "FLOAT DEFAULT 0"),
            ("parcelas_restantes", "INT DEFAULT 0"),
            ("tipo_posse", "VARCHAR(50) DEFAULT 'Próprio'"),
        ],
        "costs": [
            ("cf_depreciacao", "FLOAT DEFAULT 0"),
            ("cp_irpf", "FLOAT DEFAULT 0"),
            ("cp_ipca", "FLOAT DEFAULT 4.62"),
            ("margem_icms", "FLOAT DEFAULT 20.0"),
            ("remuneracao_semanal", "FLOAT DEFAULT 1551.0"),
        ],
        "saved_results": [
            ("faturamento_bruto", "FLOAT DEFAULT 0"),
            ("total_cf", "FLOAT DEFAULT 0"),
            ("total_cv", "FLOAT DEFAULT 0"),
            ("custo_diario", "FLOAT DEFAULT 0"),
            ("custo_semanal", "FLOAT DEFAULT 0"),
            ("markup_sugerido", "FLOAT DEFAULT 0"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ],
    }

    for table, cols in required_columns.items():
        existing: set[str] = set()
        try:
            async with rx.asession() as session:
                result = await session.execute(
                    text(f"SHOW COLUMNS FROM {table}")
                )
                for row in result.all():
                    if row and row[0]:
                        existing.add(row[0])
        except Exception:
            # Table may not exist on this database; skip silently.
            logging.exception("Unexpected error")
            logging.info("ensure_schema: table %s not introspectable", table)
            continue

        missing = [(name, ddl) for name, ddl in cols if name not in existing]
        if not missing:
            continue

        for col_name, col_ddl in missing:
            stmt = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_ddl}"
            try:
                async with rx.asession() as session:
                    await session.execute(text(stmt))
                    await session.commit()
                logging.info("ensure_schema: added %s.%s", table, col_name)
            except Exception as e:
                # Race condition or unsupported driver default; log and move on.
                logging.exception("Unexpected error")
                logging.info(
                    "ensure_schema: skipped %s.%s (%s)",
                    table,
                    col_name,
                    type(e).__name__,
                )

    _SCHEMA_ENSURED = True


async def google_exchange_handler(
    code: str = "", state: str = "", error: str = ""
) -> RedirectResponse:
    """Server-side handler that completes the Google OAuth exchange.

    On any failure path this function ALWAYS returns a 302 redirect to
    "/" with a `google_error=...` query string so the user is never
    stranded on the loading screen.
    """
    try:
        if error:
            return _safe_redirect("/?google_error=cancelled")
        if not code:
            return _safe_redirect("/?google_error=missing_code")

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        if not client_id or not client_secret:
            return _safe_redirect("/?google_error=not_configured")
    except Exception:
        logging.exception("google_exchange_handler: pre-flight failure")
        return _safe_redirect("/?google_error=preflight_error")

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code != 200:
                logging.warning(
                    "Google token exchange failed status=%s",
                    token_resp.status_code,
                )
                return _safe_redirect("/?google_error=token_failed")
            tokens = token_resp.json()
            access_token = tokens.get("access_token")
            if not access_token:
                return _safe_redirect("/?google_error=no_access_token")

            ui_resp = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if ui_resp.status_code != 200:
                logging.warning(
                    "Google userinfo failed status=%s", ui_resp.status_code
                )
                return _safe_redirect("/?google_error=userinfo_failed")
            info = ui_resp.json()
    except Exception:
        logging.exception("google_exchange_handler: HTTP error")
        return _safe_redirect("/?google_error=network_error")

    email = (info.get("email") or "").strip()
    verified = bool(info.get("verified_email", False))
    name = (info.get("name") or "Google User").strip()
    if not email or not verified:
        return _safe_redirect("/?google_error=email_not_verified")

    # Defensive: ensure env vars are normalized and aiomysql patch applied
    # before any rx.asession() use, even if the module was imported via an
    # alternate path that bypassed the main app initialization.
    normalize_db_env()
    normalize_db_envs()
    apply_aiomysql_ping_patch()

    await _ensure_schema()

    try:
        import reflex as rx

        async with rx.asession() as session:
            r = await session.execute(
                text(
                    "SELECT id, username, is_admin FROM users WHERE email = :e LIMIT 1"
                ),
                {"e": email},
            )
            user = r.first()
            if user:
                uid = user[0]
                username = user[1]
                is_admin = bool(user[2]) if user[2] else False
            else:
                uid = str(uuid.uuid4())
                base_username = email.split("@")[0] or "user"
                username = base_username
                u_res = await session.execute(
                    text("SELECT id FROM users WHERE username = :u LIMIT 1"),
                    {"u": username},
                )
                if u_res.first():
                    username = f"{base_username}_{str(uuid.uuid4())[:6]}"
                random_pass = str(uuid.uuid4())
                hashed = bcrypt.hashpw(
                    random_pass.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
                await session.execute(
                    text(
                        "INSERT INTO users (id, username, email, password_hash, is_admin) "
                        "VALUES (:id, :u, :e, :h, 0)"
                    ),
                    {"id": uid, "u": username, "e": email, "h": hashed},
                )
                # Profile insert is idempotent
                await session.execute(
                    text(
                        "INSERT IGNORE INTO profiles "
                        "(user_id, nome, email, dias_semana, horas_dia, km_dia) "
                        "VALUES (:id, :n, :e, 6, 8, 150.0)"
                    ),
                    {"id": uid, "n": name, "e": email},
                )
                await session.commit()
                is_admin = False
    except Exception:
        logging.exception("google_exchange_handler: DB error")
        return _safe_redirect("/?google_error=db_error")

    try:
        ott = str(uuid.uuid4())
        google_auth_tokens.set(
            ott,
            {
                "user_id": uid,
                "username": username,
                "email": email,
                "is_admin": is_admin,
            },
            120,
        )
        return _safe_redirect(f"/auth/google/finalize?ott={ott}")
    except Exception:
        logging.exception("google_exchange_handler: ott persistence failed")
        return _safe_redirect("/?google_error=session_error")


def register_google_auth_routes(app) -> None:
    """Attach the Google OAuth backend routes to the Reflex FastAPI app.

    In Reflex 0.8.x the internal FastAPI instance is exposed as ``app.api``.
    We register two GET routes:
      - /api/auth/google/start   → builds the Google OAuth URL and redirects.
      - /api/auth/google/exchange → exchanges the code, creates/finds the user,
                                    issues a one-time-token and redirects to
                                    /auth/google/finalize?ott=<token>.
    """
    try:
        # Reflex 0.8.x exposes the FastAPI instance as app.api.
        backend_app = getattr(app, "api", None)
        if backend_app is None:
            # Fallback probe for renamed attributes in future Reflex releases.
            for attr in ("_api", "backend_app", "_backend_app"):
                backend_app = getattr(app, attr, None)
                if backend_app is not None:
                    break
        if backend_app is None:
            logging.error(
                "register_google_auth_routes: could not locate the FastAPI "
                "instance on the Reflex app object. "
                "Available attrs: %s",
                [a for a in dir(app) if not a.startswith("__")],
            )
            return

        backend_app.add_route(
            "/api/auth/google/start",
            google_start_handler,
            methods=["GET"],
            name="google_oauth_start",
        )
        backend_app.add_route(
            "/api/auth/google/exchange",
            google_exchange_handler,
            methods=["GET"],
            name="google_oauth_exchange",
        )
        logging.info(
            "register_google_auth_routes: routes registered on %s",
            type(backend_app).__name__,
        )
    except Exception:
        logging.exception("register_google_auth_routes: failed to register")