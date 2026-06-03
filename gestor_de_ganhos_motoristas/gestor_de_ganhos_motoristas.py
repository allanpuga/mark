from gestor_de_ganhos_motoristas.db_env import normalize_db_env, normalize_db_envs

normalize_db_env()
normalize_db_envs()

from gestor_de_ganhos_motoristas.db_compat import apply_aiomysql_ping_patch

apply_aiomysql_ping_patch()

import reflex as rx
import os
import asyncio

from gestor_de_ganhos_motoristas.db_init import init_db
from gestor_de_ganhos_motoristas.states.auth_state import AuthState
from gestor_de_ganhos_motoristas.states.profile_state import ProfileState
from gestor_de_ganhos_motoristas.states.vehicle_state import VehicleState
from gestor_de_ganhos_motoristas.states.costs_state import CostsState
from gestor_de_ganhos_motoristas.states.results_state import ResultsState
from gestor_de_ganhos_motoristas.states.admin_state import AdminState
from gestor_de_ganhos_motoristas.states.legal_state import LegalState
from gestor_de_ganhos_motoristas.pages.auth import (
    login_page,
    register_page,
    recover_page,
    google_callback_page,
    google_start_page,
    google_finalize_page,
)
from gestor_de_ganhos_motoristas.google_auth_api import register_google_auth_routes
from gestor_de_ganhos_motoristas.pages.legal import privacy_policy_page, terms_of_service_page
from gestor_de_ganhos_motoristas.pages.perfil import profile_page
from gestor_de_ganhos_motoristas.pages.veiculos import vehicles_page
from gestor_de_ganhos_motoristas.pages.custos import costs_page
from gestor_de_ganhos_motoristas.pages.resultados import results_page
from gestor_de_ganhos_motoristas.pages.admin import admin_page
import logging


class InitState(rx.State):
    """State to handle global application initialization."""

    @rx.event
    async def on_load(self):
        """Non-blocking initialization check for the database."""
        from gestor_de_ganhos_motoristas.db_init import _initialized

        if _initialized:
            return
        try:
            await asyncio.wait_for(init_db(), timeout=5)
        except Exception:
            logging.exception("Unexpected error during database initialization")


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)

# Deployment-safe root page with legal navigation support
app.add_page(
    login_page,
    route="/",
    on_load=[AuthState.handle_google_callback, LegalState.check_legal_params],
)

app.add_page(register_page, route="/registrar")
app.add_page(recover_page, route="/recuperar-senha")

# Legal routes with aliasing for production propagation
app.add_page(privacy_policy_page, route="/privacidade")
app.add_page(terms_of_service_page, route="/termos")

app.add_page(
    google_start_page,
    route="/auth/google/start",
    on_load=AuthState.init_google_oauth,
)
app.add_page(
    google_callback_page,
    route="/auth/google/callback",
    on_load=AuthState.handle_google_callback,
)
app.add_page(
    google_finalize_page,
    route="/auth/google/finalize",
    on_load=AuthState.finalize_google_auth,
)

register_google_auth_routes(app)
app.add_page(
    profile_page,
    route="/app/perfil",
    on_load=[
        InitState.on_load,
        AuthState.check_auth,
        ProfileState.load_profile,
    ],
)
app.add_page(
    vehicles_page,
    route="/app/veiculos",
    on_load=[
        InitState.on_load,
        AuthState.check_auth,
        ProfileState.load_profile,
        VehicleState.load_vehicles,
    ],
)
app.add_page(
    costs_page,
    route="/app/custos",
    on_load=[
        InitState.on_load,
        AuthState.check_auth,
        ProfileState.load_profile,
        VehicleState.load_vehicles,
        CostsState.load_costs,
    ],
)
app.add_page(
    results_page,
    route="/app/resultados",
    on_load=[
        InitState.on_load,
        AuthState.check_auth,
        ProfileState.load_profile,
        VehicleState.load_vehicles,
        CostsState.load_costs,
        ResultsState.recalculate,
        ResultsState.load_saved_results,
        ResultsState.auto_save_result,
    ],
)
app.add_page(
    admin_page,
    route="/admin",
    on_load=[
        InitState.on_load,
        AuthState.check_auth,
        AuthState.check_admin,
        AdminState.load_admin_data,
    ],
)