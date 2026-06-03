from gestor_de_ganhos_motoristas.db_env import normalize_db_env, normalize_db_envs

normalize_db_env()
normalize_db_envs()

from gestor_de_ganhos_motoristas.db_compat import apply_aiomysql_ping_patch

apply_aiomysql_ping_patch()

import reflex as rx
import bcrypt
import re
from sqlalchemy import text
import uuid
import os
import logging
import httpx


class AuthState(rx.State):
    """Handle all authentication logic and session management."""

    logged_in: bool = False
    is_admin: bool = False
    current_user: str = ""
    user_id: str = ""
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""

    @rx.event
    def logout(self):
        """Reset session and redirect to login."""
        self.logged_in = False
        self.current_user = ""
        self.user_id = ""
        self.username = ""
        self.email = ""
        self.is_admin = False
        return rx.redirect("/")

    def _get_google_redirect_uri(self) -> str:
        """Return the canonical OAuth redirect URI.

        Priority:
          1. GOOGLE_REDIRECT_URI env var (explicit, works in all environments).
          2. Fallback: derive from the current request host (dev/sandbox only).
        """
        explicit = os.getenv("GOOGLE_REDIRECT_URI", "").strip()
        if explicit:
            return explicit

        host = getattr(self.router.page, "host", "localhost:3000")
        host_lower = (host or "").lower()
        protocol = (
            "https" if "build.reflexsandbox.com" in host_lower else "http"
        )
        return f"{protocol}://{host}/auth/google/callback"

    @rx.event
    def init_google_oauth(self):
        """Build the OAuth URL and redirect to Google."""
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        if not client_id or not client_secret:
            yield rx.redirect("/?google_error=not_configured")
            return

        import urllib.parse

        redirect_uri = self._get_google_redirect_uri()
        state_val = str(uuid.uuid4())

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",
            "state": state_val,
        }

        query = urllib.parse.urlencode(params)
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{query}"

        yield rx.redirect(auth_url, is_external=True)

    @rx.event
    async def handle_google_callback(self):
        """Process Google callback query parameters via httpx in the Reflex backend.

        Normalizes DB env vars and applies the aiomysql patch before any
        DB session, ensures the required schema exists, and on any
        failure path redirects the user back to / with a clear
        google_error code so they are never stranded on a loading screen.
        """
        query_params = self.router.page.params
        error = query_params.get("error")
        code = query_params.get("code")

        if not error and not code:
            return

        if error:
            yield rx.redirect("/?google_error=cancelled")
            return

        if not code:
            yield rx.redirect("/?google_error=missing_code")
            return

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if not client_id or not client_secret:
            yield rx.redirect("/?google_error=not_configured")
            return

        redirect_uri = self._get_google_redirect_uri()

        # Defensive: normalize DB env and apply aiomysql patch BEFORE any
        # rx.asession use, even if module-level normalization didn't run.
        try:
            normalize_db_env()
            normalize_db_envs()
            apply_aiomysql_ping_patch()
        except Exception:
            logging.exception("handle_google_callback: env normalize failed")

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                token_resp = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": code,
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                )
                if token_resp.status_code != 200:
                    logging.warning(
                        "Google token exchange failed status=%s",
                        token_resp.status_code,
                    )
                    yield rx.redirect("/?google_error=token_failed")
                    return

                tokens = token_resp.json()
                access_token = tokens.get("access_token")
                if not access_token:
                    yield rx.redirect("/?google_error=no_access_token")
                    return

                userinfo_resp = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if userinfo_resp.status_code != 200:
                    yield rx.redirect("/?google_error=userinfo_failed")
                    return

                user_info = userinfo_resp.json()
        except Exception:
            logging.exception("handle_google_callback: HTTP error")
            yield rx.redirect("/?google_error=network_error")
            return

        email = (user_info.get("email") or "").strip()
        verified_email = bool(user_info.get("verified_email", False))
        name = (user_info.get("name") or "Google User").strip()

        if not email or not verified_email:
            yield rx.redirect("/?google_error=email_not_verified")
            return

        # Ensure schema/columns exist before any SELECT/INSERT.
        try:
            from gestor_de_ganhos_motoristas.google_auth_api import _ensure_schema

            await _ensure_schema()
        except Exception:
            logging.exception("handle_google_callback: schema ensure failed")

        try:
            async with rx.asession() as session:
                result = await session.execute(
                    text(
                        "SELECT id, username, is_admin FROM users WHERE email = :email LIMIT 1"
                    ),
                    {"email": email},
                )
                user = result.first()

                if user:
                    self.logged_in = True
                    self.user_id = user[0]
                    self.current_user = user[1]
                    self.username = user[1]
                    self.email = email
                    self.is_admin = bool(user[2]) if user[2] else False
                    yield rx.redirect("/app/perfil")
                    return

                uid = str(uuid.uuid4())
                random_pass = str(uuid.uuid4())
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(
                    random_pass.encode("utf-8"), salt
                ).decode("utf-8")

                base_username = email.split("@")[0] or "user"
                username = base_username
                u_res = await session.execute(
                    text("SELECT id FROM users WHERE username = :u LIMIT 1"),
                    {"u": username},
                )
                if u_res.first():
                    username = f"{base_username}_{str(uuid.uuid4())[:6]}"

                await session.execute(
                    text(
                        "INSERT INTO users (id, username, email, password_hash, is_admin) "
                        "VALUES (:id, :username, :email, :hash, 0)"
                    ),
                    {
                        "id": uid,
                        "username": username,
                        "email": email,
                        "hash": hashed,
                    },
                )
                await session.execute(
                    text(
                        "INSERT IGNORE INTO profiles "
                        "(user_id, nome, email, dias_semana, horas_dia, km_dia) "
                        "VALUES (:id, :nome, :email, 6, 8, 150.0)"
                    ),
                    {"id": uid, "nome": name, "email": email},
                )
                await session.commit()

                self.logged_in = True
                self.user_id = uid
                self.current_user = username
                self.username = username
                self.email = email
                self.is_admin = False
                yield rx.redirect("/app/perfil")
        except Exception:
            logging.exception("handle_google_callback: DB error")
            yield rx.redirect("/?google_error=db_error")

    def _validate_email(self, email: str) -> bool:
        return re.match("[^@]+@[^@]+\\.[^@]+", email) is not None

    def _clear_session(self):
        """Clear all session-related state. Helper used before failed logins."""
        self.logged_in = False
        self.current_user = ""
        self.user_id = ""
        self.username = ""
        self.email = ""
        self.is_admin = False

    @rx.event
    async def handle_login(self, form_data: dict):
        """Verify credentials and start session."""
        username = form_data.get("username", "").strip()
        password = form_data.get("password", "").strip()
        if not username or not password:
            self._clear_session()
            return rx.toast("Por favor, preencha todos os campos.")
        try:
            async with rx.asession() as session:
                result = await session.execute(
                    text(
                        "SELECT id, password_hash, is_admin FROM users WHERE username = :username"
                    ),
                    {"username": username},
                )
                user = result.first()
                if user and bcrypt.checkpw(
                    password.encode("utf-8"), user[1].encode("utf-8")
                ):
                    self.logged_in = True
                    self.current_user = username
                    self.username = username
                    self.user_id = user[0]
                    self.is_admin = bool(user[2]) if user[2] else False
                    return rx.redirect("/app/perfil")
                else:
                    self._clear_session()
                    return rx.toast("Usuário ou senha incorretos.")
        except Exception as e:
            import logging

            logging.exception(f"Login error: {e}")
            self._clear_session()
            return rx.toast("Erro ao conectar com o servidor. Tente novamente.")

    @rx.event
    async def handle_register(self, form_data: dict):
        """Create new user with hashed password."""
        username = form_data.get("username", "").strip()
        email = form_data.get("email", "").strip()
        password = form_data.get("password", "").strip()
        confirm = form_data.get("confirm_password", "").strip()
        if not all([username, email, password, confirm]):
            yield rx.toast("Todos os campos são obrigatórios.")
            return
        if not self._validate_email(email):
            yield rx.toast("E-mail inválido.")
            return
        if len(password) < 6:
            yield rx.toast("A senha deve ter pelo menos 6 caracteres.")
            return
        if password != confirm:
            yield rx.toast("As senhas não coincidem.")
            return
        try:
            async with rx.asession() as session:
                result = await session.execute(
                    text("SELECT id FROM users WHERE username = :username"),
                    {"username": username},
                )
                if result.first():
                    yield rx.toast("Este nome de usuário já existe.")
                    return
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode("utf-8"), salt).decode(
                    "utf-8"
                )
                uid = str(uuid.uuid4())
                await session.execute(
                    text(
                        "INSERT INTO users (id, username, email, password_hash) VALUES (:id, :username, :email, :hash)"
                    ),
                    {
                        "id": uid,
                        "username": username,
                        "email": email,
                        "hash": hashed,
                    },
                )
                await session.execute(
                    text(
                        "INSERT INTO profiles (user_id, nome, email, dias_semana, horas_dia, km_dia) VALUES (:id, :nome, :email, 6, 8, 150.0)"
                    ),
                    {"id": uid, "nome": username, "email": email},
                )
                await session.commit()
            yield rx.toast("Conta criada com sucesso! Faça login.")
            yield rx.redirect("/")
        except Exception as e:
            import logging

            logging.exception(f"Registration error: {e}")
            yield rx.toast("Erro ao criar conta. Tente novamente.")

    @rx.event
    def check_auth(self):
        """Protect routes by checking session."""
        if not self.logged_in:
            return rx.redirect("/")

    @rx.event
    def check_admin(self):
        """Protect admin routes."""
        if not self.logged_in or not self.is_admin:
            return rx.redirect("/app/perfil")

    @rx.event
    def finalize_google_auth(self):
        """Read the one-time-token issued by /api/auth/google/exchange and
        finalize the user session inside Reflex state."""
        from gestor_de_ganhos_motoristas.google_auth_api import google_auth_tokens

        ott = self.router.page.params.get("ott", "")
        if not ott:
            yield rx.toast("Token de autenticação ausente.")
            yield rx.redirect("/")
            return
        data = google_auth_tokens.get(ott)
        if not data or not isinstance(data, dict):
            yield rx.toast("Sessão de login expirada. Tente novamente.")
            yield rx.redirect("/")
            return
        self.logged_in = True
        self.user_id = data.get("user_id", "")
        self.current_user = data.get("username", "")
        self.username = data.get("username", "")
        self.email = data.get("email", "")
        self.is_admin = bool(data.get("is_admin", False))
        yield rx.redirect("/app/perfil")