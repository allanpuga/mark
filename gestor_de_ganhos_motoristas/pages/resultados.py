import reflex as rx
from gestor_de_ganhos_motoristas.states.results_state import ResultsState
from gestor_de_ganhos_motoristas.components.layout import base_layout


def saved_result_card(r: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h4(
                    r["veiculo_nome"], class_name="font-bold text-gray-900"
                ),
                rx.el.p(
                    r["created_at"], class_name="text-xs text-gray-400 mt-0.5"
                ),
                rx.el.div(
                    rx.el.span(
                        f"{r['dias_semana']}d/sem",
                        class_name="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-md text-xs font-medium",
                    ),
                    rx.el.span(
                        f"{r['horas_dia']}h/dia",
                        class_name="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-md text-xs font-medium",
                    ),
                    rx.el.span(
                        f"{r['km_dia']} km/dia",
                        class_name="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-md text-xs font-medium",
                    ),
                    rx.el.span(
                        f"ISS {r['cp_iss']}%",
                        class_name="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-md text-xs font-medium",
                    ),
                    rx.el.span(
                        f"Margem {r['margem_iss']}%",
                        class_name="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-md text-xs font-medium",
                    ),
                    class_name="flex flex-wrap gap-2 mt-2",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Custo", class_name="text-xs text-gray-500 block mb-0.5"
                    ),
                    rx.el.span(
                        f"R$ {r['custo_por_km'].to(float):.2f}/km",
                        class_name="text-sm font-bold text-red-600",
                    ),
                    class_name="text-center",
                ),
                rx.el.div(
                    rx.el.span(
                        "Ideal", class_name="text-xs text-gray-500 block mb-0.5"
                    ),
                    rx.el.span(
                        f"R$ {r['valor_ideal_km'].to(float):.2f}/km",
                        class_name="text-sm font-bold text-emerald-600",
                    ),
                    class_name="text-center",
                ),
                rx.el.div(
                    rx.el.span(
                        "Markup",
                        class_name="text-xs text-gray-500 block mb-0.5",
                    ),
                    rx.el.span(
                        f"{r['markup_sugerido'].to(float):.1f}%",
                        class_name="text-sm font-bold text-blue-600",
                    ),
                    class_name="text-center",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-4 w-4"),
                    on_click=lambda: ResultsState.delete_saved_result(r["id"]),
                    class_name="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-xl",
                ),
                class_name="flex items-center gap-4",
            ),
            class_name="flex justify-between items-start",
        ),
        class_name="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all",
    )


def results_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "Resultados & Markup",
                        class_name="text-2xl font-bold text-gray-900",
                    ),
                    rx.el.p(
                        "Análise de viabilidade financeira e metas de faturamento",
                        class_name="text-gray-500 text-sm",
                    ),
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("rotate-cw", class_name="h-4 w-4 mr-2"),
                        "Recalcular",
                        on_click=ResultsState.recalculate,
                        class_name="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-bold flex items-center shadow-md transition-all",
                    ),
                    rx.el.button(
                        rx.icon("save", class_name="h-4 w-4 mr-2"),
                        "Salvar Resultado",
                        on_click=ResultsState.save_result,
                        disabled=ResultsState.is_saving,
                        class_name="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2.5 rounded-xl font-bold flex items-center shadow-md transition-all",
                    ),
                    class_name="flex gap-3",
                ),
                class_name="flex justify-between items-end mb-8",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "trending-down",
                                class_name="h-6 w-6 text-red-600",
                            ),
                            class_name="p-3 bg-white rounded-xl shadow-sm",
                        ),
                        rx.el.div(
                            rx.el.h2(
                                "Custo Mínimo",
                                class_name="text-xl font-bold text-red-900",
                            ),
                            rx.el.p(
                                "Quanto você gasta para operar (CF + CV)",
                                class_name="text-red-700 text-sm font-medium",
                            ),
                        ),
                        class_name="flex items-center gap-4 mb-8",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                f"R$ {ResultsState.custo_por_km:.2f}",
                                class_name="text-4xl font-extrabold text-red-600",
                            ),
                            rx.el.span(
                                "/km",
                                class_name="text-red-500 font-semibold ml-1",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.span(
                                f"R$ {ResultsState.custo_por_hora:.2f}",
                                class_name="text-4xl font-extrabold text-red-600",
                            ),
                            rx.el.span(
                                "/hora",
                                class_name="text-red-500 font-semibold ml-1",
                            ),
                        ),
                        class_name="flex flex-col",
                    ),
                    rx.el.p(
                        "Abaixo desse valor você está no prejuízo operacional",
                        class_name="mt-8 text-sm text-red-700 font-semibold italic",
                    ),
                    class_name="p-8 rounded-[2rem] bg-red-50 border-2 border-red-200 shadow-lg relative overflow-hidden",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "trending-up",
                                class_name="h-6 w-6 text-emerald-600",
                            ),
                            class_name="p-3 bg-white rounded-xl shadow-sm",
                        ),
                        rx.el.div(
                            rx.el.h2(
                                "Valor Ideal (Markup ISS)",
                                class_name="text-xl font-bold text-emerald-900",
                            ),
                            rx.el.p(
                                "Custos + Impostos + Margem de lucro",
                                class_name="text-emerald-700 text-sm font-medium",
                            ),
                        ),
                        class_name="flex items-center gap-4 mb-8",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                f"R$ {ResultsState.valor_ideal_km:.2f}",
                                class_name="text-4xl font-extrabold text-emerald-600",
                            ),
                            rx.el.span(
                                "/km",
                                class_name="text-emerald-500 font-semibold ml-1",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.span(
                                f"R$ {ResultsState.valor_ideal_hora:.2f}",
                                class_name="text-4xl font-extrabold text-emerald-600",
                            ),
                            rx.el.span(
                                "/hora",
                                class_name="text-emerald-500 font-semibold ml-1",
                            ),
                        ),
                        class_name="flex flex-col",
                    ),
                    rx.el.p(
                        "Valor para cobrir todos os custos e ter lucro",
                        class_name="mt-8 text-sm text-emerald-700 font-semibold italic",
                    ),
                    class_name="p-8 rounded-[2rem] bg-emerald-50 border-2 border-emerald-200 shadow-lg relative overflow-hidden",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12",
            ),
            rx.el.h3(
                "Informações Complementares",
                class_name="text-lg font-bold text-gray-700 mb-4 px-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Custo Mensal Total",
                        class_name="text-gray-500 text-xs font-bold uppercase tracking-wider mb-1",
                    ),
                    rx.el.p(
                        f"R$ {ResultsState.custo_mensal_total:.2f}",
                        class_name="text-xl font-bold text-gray-900",
                    ),
                    class_name="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm",
                ),
                rx.el.div(
                    rx.el.p(
                        "Custo Diário",
                        class_name="text-gray-500 text-xs font-bold uppercase tracking-wider mb-1",
                    ),
                    rx.el.p(
                        f"R$ {ResultsState.custo_diario:.2f}",
                        class_name="text-xl font-bold text-gray-900",
                    ),
                    class_name="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm",
                ),
                rx.el.div(
                    rx.el.p(
                        "Custo Semanal",
                        class_name="text-gray-500 text-xs font-bold uppercase tracking-wider mb-1",
                    ),
                    rx.el.p(
                        f"R$ {ResultsState.custo_semanal:.2f}",
                        class_name="text-xl font-bold text-gray-900",
                    ),
                    class_name="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm",
                ),
                rx.el.div(
                    rx.el.p(
                        "Markup Sugerido",
                        class_name="text-gray-500 text-xs font-bold uppercase tracking-wider mb-1",
                    ),
                    rx.el.p(
                        f"{ResultsState.markup_sugerido:.1f}%",
                        class_name="text-xl font-bold text-blue-600",
                    ),
                    class_name="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm",
                ),
                class_name="grid grid-cols-2 md:grid-cols-4 gap-4",
            ),
            rx.el.h3(
                "Resultados Salvos",
                class_name="text-lg font-bold text-gray-700 mb-4 px-2 mt-10",
            ),
            rx.cond(
                ResultsState.saved_results.length() > 0,
                rx.el.div(
                    rx.foreach(ResultsState.saved_results, saved_result_card),
                    class_name="flex flex-col gap-4",
                ),
                rx.el.div(
                    rx.el.p(
                        "Nenhum resultado salvo ainda.",
                        class_name="text-gray-500 text-center py-8",
                    ),
                    class_name="bg-white rounded-2xl border border-gray-200 shadow-sm",
                ),
            ),
        ),
        "/app/resultados",
    )