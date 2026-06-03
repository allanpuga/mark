import reflex as rx
from gestor_de_ganhos_motoristas.states.vehicle_state import VehicleState, Vehicle
from gestor_de_ganhos_motoristas.states.profile_state import ProfileState
from gestor_de_ganhos_motoristas.components.layout import base_layout


def vehicle_card(v: Vehicle):
    is_active = v["id"] == ProfileState.veiculo_ativo_id
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    f"{v['marca']} {v['modelo']}",
                    class_name="text-lg font-bold text-gray-900",
                ),
                rx.el.p(
                    f"Ano: {v['ano']} | FIPE: {v['valor_fipe']}",
                    class_name="text-sm text-gray-500",
                ),
                rx.el.div(
                    rx.el.span(
                        v["tipo_posse"],
                        class_name="inline-block px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full",
                    ),
                    rx.cond(
                        v["categorias"].length() > 0,
                        rx.el.div(
                            rx.foreach(
                                v["categorias"],
                                lambda cat: rx.el.span(
                                    cat,
                                    class_name="inline-block px-2 py-0.5 bg-blue-50 text-blue-600 text-[10px] font-bold rounded-md border border-blue-100 uppercase",
                                ),
                            ),
                            class_name="flex flex-wrap gap-1 mt-2",
                        ),
                        rx.fragment(),
                    ),
                    class_name="mt-2 flex flex-col",
                ),
            ),
            rx.el.div(
                rx.cond(
                    is_active,
                    rx.el.span(
                        "Ativo",
                        class_name="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-bold rounded-xl border border-blue-200 w-fit",
                    ),
                    rx.el.button(
                        "Tornar Ativo",
                        on_click=lambda: VehicleState.set_active_vehicle(
                            v["id"]
                        ),
                        class_name="px-3 py-1 bg-white text-gray-600 text-sm font-medium rounded-xl border border-gray-300 hover:bg-gray-50",
                    ),
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-4 w-4"),
                    on_click=lambda: VehicleState.remove_vehicle(v["id"]),
                    class_name="p-2 text-red-500 hover:bg-red-50 rounded-xl",
                ),
                class_name="flex items-center gap-2",
            ),
            class_name="flex justify-between items-start",
        ),
        class_name=rx.cond(
            is_active,
            "bg-white p-6 rounded-2xl border-2 border-blue-500 shadow-md mb-4",
            "bg-white p-6 rounded-2xl border border-gray-200 shadow-sm mb-4",
        ),
    )


def vehicles_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "Meus Veículos",
                class_name="text-2xl font-bold text-gray-900 mb-6",
            ),
            rx.el.div(
                rx.foreach(VehicleState.vehicles, vehicle_card),
                class_name="mb-8",
            ),
            rx.el.div(
                rx.el.h2(
                    "Adicionar Veículo",
                    class_name="text-xl font-bold text-gray-900 mb-4",
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Marca (FIPE)",
                                class_name="block text-sm font-semibold text-gray-700 mb-1",
                            ),
                            rx.el.div(
                                rx.el.select(
                                    rx.el.option("Selecione", value=""),
                                    rx.foreach(
                                        VehicleState.brands,
                                        lambda b: rx.el.option(
                                            b["name"], value=b["code"]
                                        ),
                                    ),
                                    value=VehicleState.marca_code,
                                    on_change=VehicleState.set_marca,
                                    disabled=VehicleState.is_loading,
                                    class_name="w-full px-4 py-2 appearance-none border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 bg-white disabled:opacity-50 disabled:cursor-not-allowed",
                                ),
                                rx.icon(
                                    "chevron-down",
                                    class_name="absolute right-3 top-3 h-4 w-4 text-gray-400 pointer-events-none",
                                ),
                                class_name="relative",
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Modelo (FIPE)",
                                class_name="block text-sm font-semibold text-gray-700 mb-1",
                            ),
                            rx.el.div(
                                rx.el.select(
                                    rx.el.option("Selecione", value=""),
                                    rx.foreach(
                                        VehicleState.models,
                                        lambda m: rx.el.option(
                                            m["name"], value=m["code"]
                                        ),
                                    ),
                                    value=VehicleState.modelo_code,
                                    on_change=VehicleState.set_modelo,
                                    disabled=(VehicleState.marca_code == "")
                                    | VehicleState.is_loading,
                                    class_name="w-full px-4 py-2 appearance-none border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 bg-white disabled:opacity-50 disabled:cursor-not-allowed",
                                ),
                                rx.icon(
                                    "chevron-down",
                                    class_name="absolute right-3 top-3 h-4 w-4 text-gray-400 pointer-events-none",
                                ),
                                class_name="relative",
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Ano (FIPE)",
                                class_name="block text-sm font-semibold text-gray-700 mb-1",
                            ),
                            rx.el.div(
                                rx.el.select(
                                    rx.el.option("Selecione", value=""),
                                    rx.foreach(
                                        VehicleState.years,
                                        lambda y: rx.el.option(
                                            y["name"], value=y["code"]
                                        ),
                                    ),
                                    value=VehicleState.ano_code,
                                    on_change=VehicleState.set_ano,
                                    disabled=(VehicleState.modelo_code == "")
                                    | VehicleState.is_loading,
                                    class_name="w-full px-4 py-2 appearance-none border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 bg-white disabled:opacity-50 disabled:cursor-not-allowed",
                                ),
                                rx.icon(
                                    "chevron-down",
                                    class_name="absolute right-3 top-3 h-4 w-4 text-gray-400 pointer-events-none",
                                ),
                                class_name="relative",
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Valor FIPE",
                                class_name="block text-sm font-semibold text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                disabled=True,
                                class_name="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-gray-600",
                                default_value=VehicleState.valor_fipe,
                                key=VehicleState.valor_fipe,
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Tipo de Posse",
                                class_name="block text-sm font-semibold text-gray-700 mb-1",
                            ),
                            rx.el.div(
                                rx.el.select(
                                    rx.el.option("Próprio", value="Próprio"),
                                    rx.el.option(
                                        "Financiamento", value="Financiamento"
                                    ),
                                    rx.el.option("Aluguel", value="Aluguel"),
                                    value=VehicleState.tipo_posse,
                                    on_change=VehicleState.set_tipo_posse,
                                    class_name="w-full px-4 py-2 appearance-none border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 bg-white",
                                ),
                                rx.icon(
                                    "chevron-down",
                                    class_name="absolute right-3 top-3 h-4 w-4 text-gray-400 pointer-events-none",
                                ),
                                class_name="relative",
                            ),
                        ),
                        rx.cond(
                            VehicleState.tipo_posse == "Aluguel",
                            rx.el.div(
                                rx.el.label(
                                    "Valor Aluguel (Semana)",
                                    class_name="block text-sm font-semibold text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    name="valor_aluguel_semana",
                                    type="number",
                                    step="0.01",
                                    default_value="0",
                                    class_name="w-full px-4 py-2 border border-gray-200 rounded-xl",
                                ),
                            ),
                            rx.cond(
                                VehicleState.tipo_posse == "Financiamento",
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.label(
                                            "Valor Parcela (Mês)",
                                            class_name="block text-sm font-semibold text-gray-700 mb-1",
                                        ),
                                        rx.el.input(
                                            name="valor_parcela",
                                            type="number",
                                            step="0.01",
                                            default_value="0",
                                            class_name="w-full px-4 py-2 border border-gray-200 rounded-xl mb-4",
                                        ),
                                    ),
                                    rx.el.div(
                                        rx.el.label(
                                            "Parcelas Restantes",
                                            class_name="block text-sm font-semibold text-gray-700 mb-1",
                                        ),
                                        rx.el.input(
                                            name="parcelas_restantes",
                                            type="number",
                                            default_value="0",
                                            class_name="w-full px-4 py-2 border border-gray-200 rounded-xl",
                                        ),
                                    ),
                                ),
                                rx.el.div(),
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Quais categorias seu carro atende?",
                                class_name="block text-sm font-semibold text-gray-700 mb-2",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    VehicleState.available_categories,
                                    lambda cat: rx.el.div(
                                        cat,
                                        on_click=lambda: (
                                            VehicleState.toggle_category(cat)
                                        ),
                                        class_name=rx.cond(
                                            VehicleState.selected_categories.contains(
                                                cat
                                            ),
                                            "px-4 py-2 rounded-xl border-2 border-blue-500 bg-blue-50 text-blue-700 text-sm font-bold cursor-pointer transition-all shadow-sm",
                                            "px-4 py-2 rounded-xl border border-gray-200 bg-white text-gray-600 text-sm font-medium cursor-pointer hover:border-blue-300 hover:bg-gray-50 transition-all",
                                        ),
                                    ),
                                ),
                                class_name="flex flex-wrap gap-2",
                            ),
                            class_name="col-span-full mt-4",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.cond(
                                VehicleState.is_loading,
                                rx.icon(
                                    "loader", class_name="h-5 w-5 animate-spin"
                                ),
                                "Cadastrar Veículo",
                            ),
                            type="submit",
                            class_name="bg-blue-600 text-white font-bold py-3 px-8 rounded-xl hover:bg-blue-700 transition-all shadow-md flex items-center justify-center gap-2",
                            disabled=VehicleState.is_loading,
                        ),
                        class_name="mt-8 flex justify-end",
                    ),
                    on_submit=VehicleState.add_vehicle,
                ),
                class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm",
            ),
        ),
        "/app/veiculos",
    )