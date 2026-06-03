import reflex as rx
from gestor_de_ganhos_motoristas.components.sidebar import sidebar
from gestor_de_ganhos_motoristas.states.auth_state import AuthState
from gestor_de_ganhos_motoristas.states.sidebar_state import SidebarState
# ... outros imports de states ...

from gestor_de_ganhos_motoristas.pages.auth import (
    login_page,
    register_page,
    recover_page,
    google_callback_page,
)
from gestor_de_ganhos_motoristas.pages.legal import privacy_policy_page, terms_of_service_page

# ... restante do código e rotas da app ...


def base_layout(content: rx.Component, route: str) -> rx.Component:
    """Standard layout for authenticated pages."""
    return rx.el.div(
        sidebar(route),
        rx.el.header(
            rx.el.div(
                rx.el.button(
                    rx.icon("menu", class_name="h-6 w-6 text-gray-700"),
                    on_click=SidebarState.toggle_sidebar,
                    class_name="p-2 hover:bg-gray-100 rounded-xl transition-colors",
                ),
                rx.el.div(
                    rx.icon("trending-up", class_name="h-5 w-5 text-blue-600"),
                    rx.el.span(
                        "Gestão Markup", class_name="font-bold text-gray-900"
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex items-center gap-4 px-4 h-full",
            ),
            class_name="sticky top-0 bg-white border-b border-gray-200 h-16 w-full z-40 md:hidden",
        ),
        rx.el.main(
            rx.el.div(content, class_name="max-w-6xl mx-auto"),
            class_name="ml-0 md:ml-64 p-4 md:p-8 min-h-screen bg-gray-50",
        ),
        class_name="min-h-screen font-['Inter']",
    )