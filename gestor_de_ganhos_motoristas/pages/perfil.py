import reflex as rx
from gestor_de_ganhos_motoristas.states.profile_state import ProfileState
from gestor_de_ganhos_motoristas.components.layout import base_layout


def profile_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.h1(
                "Perfil do Motorista",
                class_name="text-2xl font-bold text-gray-900 mb-6",
            ),
            rx.el.div(
                rx.el.form(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2(
                                "Dados Pessoais",
                                class_name="text-lg font-semibold text-gray-900 col-span-full border-b pb-2 mb-2",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Nome completo",
                                    class_name="block text-sm font-semibold text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    name="nome",
                                    default_value=ProfileState.nome,
                                    placeholder="Seu nome",
                                    class_name="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "E-mail",
                                    class_name="block text-sm font-semibold text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    name="email",
                                    type="email",
                                    default_value=ProfileState.email,
                                    placeholder="seu@email.com",
                                    class_name="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "WhatsApp",
                                    class_name="block text-sm font-semibold text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    name="whatsapp",
                                    default_value=ProfileState.whatsapp,
                                    placeholder="(11) 99999-9999",
                                    class_name="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Estado",
                                    class_name="block text-sm font-semibold text-gray-700 mb-1",
                                ),
                                rx.el.div(
                                    rx.el.select(
                                        rx.el.option(
                                            "Selecione um estado", value=""
                                        ),
                                        rx.foreach(
                                            ProfileState.estados,
                                            lambda s: rx.el.option(
                                                s["nome"], value=s["sigla"]
                                            ),
                                        ),
                                        name="estado",
                                        value=ProfileState.estado,
                                        on_change=ProfileState.set_estado,
                                        class_name="w-full px-4 py-2 appearance-none border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none bg-white",
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
                                    "Cidade",
                                    class_name="block text-sm font-semibold text-gray-700 mb-1",
                                ),
                                rx.el.div(
                                    rx.el.select(
                                        rx.el.option(
                                            "Selecione uma cidade", value=""
                                        ),
                                        rx.foreach(
                                            ProfileState.cidades,
                                            lambda c: rx.el.option(c, value=c),
                                        ),
                                        name="cidade",
                                        value=ProfileState.cidade,
                                        on_change=ProfileState.set_cidade,
                                        class_name="w-full px-4 py-2 appearance-none border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none bg-white",
                                        disabled=ProfileState.estado == "",
                                    ),
                                    rx.icon(
                                        "chevron-down",
                                        class_name="absolute right-3 top-3 h-4 w-4 text-gray-400 pointer-events-none",
                                    ),
                                    class_name="relative",
                                ),
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8",
                        ),
                        rx.el.div(
                            rx.el.h2(
                                "Rotina de Trabalho",
                                class_name="text-lg font-semibold text-gray-900 col-span-full border-b pb-2 mb-2",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Quantos dias por semana você trabalha?",
                                    class_name="block text-sm font-semibold text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    name="dias_semana",
                                    type="number",
                                    min="1",
                                    max="7",
                                    default_value=ProfileState.dias_semana.to_string(),
                                    class_name="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Quantas horas você trabalha por dia?",
                                    class_name="block text-sm font-semibold text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    name="horas_dia",
                                    type="number",
                                    min="1",
                                    max="24",
                                    default_value=ProfileState.horas_dia.to_string(),
                                    class_name="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Quantos km você roda por dia?",
                                    class_name="block text-sm font-semibold text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    name="km_dia",
                                    type="number",
                                    step="0.1",
                                    default_value=ProfileState.km_dia.to_string(),
                                    class_name="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none",
                                ),
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                        ),
                        class_name="flex flex-col",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.cond(
                                ProfileState.is_loading,
                                rx.icon(
                                    "loader", class_name="h-5 w-5 animate-spin"
                                ),
                                "Salvar Perfil",
                            ),
                            type="submit",
                            class_name="bg-blue-600 text-white font-bold py-3 px-8 rounded-xl hover:bg-blue-700 transition-all shadow-md flex items-center justify-center gap-2",
                            disabled=ProfileState.is_loading,
                        ),
                        class_name="mt-8 flex justify-end",
                    ),
                    on_submit=ProfileState.save_profile,
                ),
                class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm",
            ),
        ),
        "/app/perfil",
    )