import reflex as rx
from gestor_de_ganhos_motoristas.states.admin_state import AdminState
from gestor_de_ganhos_motoristas.components.layout import base_layout


def admin_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Painel Administrativo",
                    class_name="text-2xl font-bold text-gray-900",
                ),
                rx.el.p(
                    "Monitoramento de usuários e resultados",
                    class_name="text-gray-500 text-sm",
                ),
                class_name="mb-8",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("users", class_name="h-8 w-8 text-blue-600"),
                        class_name="p-3 bg-blue-50 rounded-xl mb-4 w-fit",
                    ),
                    rx.el.p(
                        "Total Usuários",
                        class_name="text-gray-500 text-sm font-semibold uppercase tracking-wide",
                    ),
                    rx.el.h2(
                        AdminState.total_users,
                        class_name="text-3xl font-bold text-gray-900 mt-1",
                    ),
                    class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "bar-chart-3", class_name="h-8 w-8 text-emerald-600"
                        ),
                        class_name="p-3 bg-emerald-50 rounded-xl mb-4 w-fit",
                    ),
                    rx.el.p(
                        "Total Resultados Salvos",
                        class_name="text-gray-500 text-sm font-semibold uppercase tracking-wide",
                    ),
                    rx.el.h2(
                        AdminState.total_results,
                        class_name="text-3xl font-bold text-gray-900 mt-1",
                    ),
                    class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "activity", class_name="h-8 w-8 text-amber-600"
                        ),
                        class_name="p-3 bg-amber-50 rounded-xl mb-4 w-fit",
                    ),
                    rx.el.p(
                        "Usuários Ativos (7 dias)",
                        class_name="text-gray-500 text-sm font-semibold uppercase tracking-wide",
                    ),
                    rx.el.h2(
                        AdminState.active_users_week,
                        class_name="text-3xl font-bold text-gray-900 mt-1",
                    ),
                    class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm",
                ),
                class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10",
            ),
            rx.el.h3(
                "Usuários Cadastrados",
                class_name="text-xl font-bold text-gray-800 mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="absolute left-3 top-3 h-5 w-5 text-gray-400",
                    ),
                    rx.el.input(
                        placeholder="Buscar por usuário ou e-mail...",
                        on_change=AdminState.set_users_search,
                        class_name="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none",
                    ),
                    class_name="relative max-w-md mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                "Usuário",
                                class_name="px-4 py-3 text-left text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "E-mail",
                                class_name="px-4 py-3 text-left text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "Cadastro",
                                class_name="px-4 py-3 text-left text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "Veículos",
                                class_name="px-4 py-3 text-center text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "Resultados",
                                class_name="px-4 py-3 text-center text-sm font-semibold text-gray-600",
                            ),
                            class_name="grid grid-cols-5 bg-gray-50 border-b border-gray-200 min-w-[600px]",
                        ),
                        rx.foreach(
                            AdminState.filtered_users,
                            lambda u: rx.el.div(
                                rx.el.div(
                                    u["username"],
                                    class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                                ),
                                rx.el.div(
                                    u["email"],
                                    class_name="px-4 py-3 text-sm text-gray-500 truncate",
                                ),
                                rx.el.div(
                                    u["created_at"],
                                    class_name="px-4 py-3 text-sm text-gray-500",
                                ),
                                rx.el.div(
                                    u["vehicle_count"].to_string(),
                                    class_name="px-4 py-3 text-sm text-gray-900 text-center",
                                ),
                                rx.el.div(
                                    u["results_count"].to_string(),
                                    class_name="px-4 py-3 text-sm text-gray-900 text-center",
                                ),
                                class_name="grid grid-cols-5 border-b border-gray-100 hover:bg-gray-50 items-center min-w-[600px]",
                            ),
                        ),
                        class_name="w-full text-left",
                    ),
                    class_name="overflow-x-auto rounded-xl border border-gray-200",
                ),
                class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm mb-10",
            ),
            rx.el.h3(
                "Resultados Salvos (Geral)",
                class_name="text-xl font-bold text-gray-800 mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="absolute left-3 top-3 h-5 w-5 text-gray-400",
                    ),
                    rx.el.input(
                        placeholder="Buscar por usuário ou veículo...",
                        on_change=AdminState.set_results_search,
                        class_name="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none",
                    ),
                    class_name="relative max-w-md mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                "Usuário",
                                class_name="px-4 py-3 text-left text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "Veículo",
                                class_name="px-4 py-3 text-left text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "Rotina",
                                class_name="px-4 py-3 text-left text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "Taxas",
                                class_name="px-4 py-3 text-left text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "Custo/km",
                                class_name="px-4 py-3 text-right text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "Ideal/km",
                                class_name="px-4 py-3 text-right text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "Markup",
                                class_name="px-4 py-3 text-right text-sm font-semibold text-gray-600",
                            ),
                            rx.el.div(
                                "Data",
                                class_name="px-4 py-3 text-right text-sm font-semibold text-gray-600",
                            ),
                            class_name="grid grid-cols-8 bg-gray-50 border-b border-gray-200 min-w-[1000px]",
                        ),
                        rx.foreach(
                            AdminState.filtered_results,
                            lambda r: rx.el.div(
                                rx.el.div(
                                    r["username"],
                                    class_name="px-4 py-3 text-sm text-gray-900 font-medium",
                                ),
                                rx.el.div(
                                    r["veiculo_nome"],
                                    class_name="px-4 py-3 text-sm text-gray-500",
                                ),
                                rx.el.div(
                                    f"{r['dias_semana']}d {r['horas_dia']}h {r['km_dia']}km",
                                    class_name="px-4 py-3 text-sm text-gray-500 whitespace-nowrap",
                                ),
                                rx.el.div(
                                    f"ISS {r['cp_iss']}% M {r['margem_iss']}%",
                                    class_name="px-4 py-3 text-sm text-gray-500 whitespace-nowrap",
                                ),
                                rx.el.div(
                                    f"R$ {r['custo_por_km'].to(float):.2f}",
                                    class_name="px-4 py-3 text-sm text-red-600 font-medium text-right whitespace-nowrap",
                                ),
                                rx.el.div(
                                    f"R$ {r['valor_ideal_km'].to(float):.2f}",
                                    class_name="px-4 py-3 text-sm text-emerald-600 font-medium text-right whitespace-nowrap",
                                ),
                                rx.el.div(
                                    f"{r['markup_sugerido'].to(float):.1f}%",
                                    class_name="px-4 py-3 text-sm text-blue-600 font-medium text-right whitespace-nowrap",
                                ),
                                rx.el.div(
                                    r["created_at"],
                                    class_name="px-4 py-3 text-sm text-gray-500 text-right whitespace-nowrap",
                                ),
                                class_name="grid grid-cols-8 border-b border-gray-100 hover:bg-gray-50 items-center min-w-[1000px]",
                            ),
                        ),
                        class_name="w-full text-left",
                    ),
                    class_name="overflow-x-auto rounded-xl border border-gray-200",
                ),
                class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm",
            ),
        ),
        "/admin",
    )