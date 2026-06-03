import reflex as rx
from gestor_de_ganhos_motoristas.states.auth_state import AuthState
from gestor_de_ganhos_motoristas.states.sidebar_state import SidebarState


def nav_item(
    label: str, icon: str, url: str, current_page: str
) -> rx.Component:
    is_active = current_page == url
    return rx.el.a(
        rx.icon(
            icon,
            class_name=rx.cond(
                is_active, "h-5 w-5 text-white", "h-5 w-5 text-gray-500"
            ),
        ),
        rx.el.span(
            label,
            class_name=rx.cond(
                is_active,
                "font-semibold text-white",
                "font-medium text-gray-700",
            ),
        ),
        href=url,
        class_name=rx.cond(
            is_active,
            "flex items-center gap-3 px-4 py-3 rounded-xl bg-blue-600 shadow-sm transition-all",
            "flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-100 transition-all",
        ),
    )


def sidebar(current_route: str) -> rx.Component:
    return rx.fragment(
        rx.cond(
            SidebarState.is_open,
            rx.el.div(
                on_click=SidebarState.toggle_sidebar,
                class_name="fixed inset-0 bg-black/50 z-40 md:hidden",
            ),
        ),
        rx.el.aside(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "trending-up",
                                class_name="h-6 w-6 text-blue-600",
                            ),
                            class_name="p-2 bg-blue-50 rounded-lg",
                        ),
                        rx.el.h1(
                            "Gestão Markup",
                            class_name="text-xl font-bold text-gray-900 tracking-tight",
                        ),
                        class_name="flex items-center gap-3",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-6 w-6 text-gray-500"),
                        on_click=SidebarState.toggle_sidebar,
                        class_name="md:hidden p-1 hover:bg-gray-100 rounded-lg transition-colors",
                    ),
                    class_name="flex items-center justify-between px-2 py-8 mb-4 border-b border-gray-100",
                ),
                rx.el.nav(
                    rx.el.div(
                        nav_item(
                            "Perfil", "user", "/app/perfil", current_route
                        ),
                        nav_item(
                            "Veículos", "truck", "/app/veiculos", current_route
                        ),
                        nav_item(
                            "Custos", "wallet", "/app/custos", current_route
                        ),
                        nav_item(
                            "Resultados",
                            "bar-chart-3",
                            "/app/resultados",
                            current_route,
                        ),
                        rx.cond(
                            AuthState.is_admin,
                            nav_item(
                                "Admin", "shield", "/admin", current_route
                            ),
                            rx.fragment(),
                        ),
                        class_name="flex flex-col gap-2",
                        on_click=SidebarState.close_sidebar,
                    ),
                    class_name="flex-1",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("log-out", class_name="h-5 w-5"),
                        rx.el.span("Sair", class_name="font-medium"),
                        on_click=AuthState.logout,
                        class_name="flex items-center gap-3 w-full px-4 py-3 text-red-600 hover:bg-red-50 rounded-xl transition-all",
                    ),
                    class_name="pt-4 border-t border-gray-100",
                ),
                class_name="flex flex-col h-full p-4",
            ),
            class_name=rx.cond(
                SidebarState.is_open,
                "fixed left-0 top-0 bottom-0 w-64 bg-white border-r border-gray-200 z-50 transition-all transform translate-x-0 md:translate-x-0",
                "fixed left-0 top-0 bottom-0 w-64 bg-white border-r border-gray-200 z-50 transition-all transform -translate-x-full md:translate-x-0",
            ),
        ),
    )