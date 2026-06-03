import reflex as rx
from gestor_de_ganhos_motoristas.states.costs_state import CostsState
from gestor_de_ganhos_motoristas.components.layout import base_layout


def cost_field(
    label: str,
    name: str,
    value_var: rx.Var,
    editable: bool = True,
    info: str = "",
    type: str = "number",
    step: str = "0.01",
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label, class_name="block text-sm font-semibold text-gray-700 mb-1"
        ),
        rx.cond(
            editable,
            rx.el.input(
                name=name,
                type=type,
                step=step,
                default_value=value_var.to_string(),
                key=value_var.to_string(),
                class_name="w-full px-4 py-2 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition-all",
            ),
            rx.el.div(
                rx.el.input(
                    disabled=True,
                    class_name="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-gray-500 cursor-not-allowed",
                    default_value=value_var.to_string(),
                    key=value_var.to_string(),
                ),
                rx.el.input(
                    type="hidden", name=name, value=value_var.to_string()
                ),
            ),
        ),
        rx.cond(
            info != "",
            rx.el.p(info, class_name="text-xs text-blue-500 mt-1 italic"),
            rx.fragment(),
        ),
        class_name="flex flex-col",
    )


def costs_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Custos Operacionais",
                    class_name="text-2xl font-bold text-gray-900",
                ),
                rx.el.p(
                    "Configure detalhadamente todos os custos para um markup preciso",
                    class_name="text-gray-500 text-sm mt-1",
                ),
                class_name="mb-6",
            ),
            rx.cond(
                CostsState.is_costs_loaded,
                rx.cond(
                    CostsState.has_active_vehicle,
                    rx.el.form(
                        rx.el.div(
                            rx.el.div(
                                rx.el.h2(
                                    "Custos Fixos (CF)",
                                    class_name="text-lg font-bold text-gray-800 border-b-2 border-blue-500 pb-2 mb-6",
                                ),
                                rx.el.div(
                                    cost_field(
                                        "CF1 Depreciação",
                                        "cf_depreciacao",
                                        CostsState.cf_depreciacao,
                                        False,
                                        "24% ao ano sobre valor FIPE (automático)",
                                    ),
                                    cost_field(
                                        "CF2 IPVA Anual",
                                        "cf_ipva",
                                        CostsState.cf_ipva,
                                        False,
                                        CostsState.info_ipva,
                                    ),
                                    cost_field(
                                        "CF3 Licenciamento",
                                        "cf_licenciamento",
                                        CostsState.cf_licenciamento,
                                        False,
                                        CostsState.info_licenciamento,
                                    ),
                                    cost_field(
                                        "CF4 Seguro Obrigatório",
                                        "cf_seguro_obrig",
                                        CostsState.cf_seguro_obrig,
                                    ),
                                    cost_field(
                                        "CF5 Seguro do Carro",
                                        "cf_seguro_carro",
                                        CostsState.cf_seguro_carro,
                                    ),
                                    cost_field(
                                        "CF6 Parcela/Aluguel",
                                        "parcela_info",
                                        rx.Var.create(0),
                                        False,
                                        "Incluído via dados do veículo",
                                    ),
                                    cost_field(
                                        "CF7 Salário DIEESE",
                                        "salario_dieese",
                                        rx.Var.create(7200),
                                        False,
                                        "Valor referência DIEESE",
                                    ),
                                    cost_field(
                                        "CF8 INSS Mensal",
                                        "cf_inss",
                                        CostsState.cf_inss,
                                        False,
                                        "11% × salário mínimo (R$ 1.412)",
                                    ),
                                    cost_field(
                                        "CF9 Internet Celular",
                                        "cf_internet",
                                        CostsState.cf_internet,
                                    ),
                                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10",
                                ),
                                rx.el.h2(
                                    "Custos Variáveis (CV)",
                                    class_name="text-lg font-bold text-gray-800 border-b-2 border-blue-500 pb-2 mb-6",
                                ),
                                rx.el.div(
                                    cost_field(
                                        "CV1 Alimentação/Dia",
                                        "cv_alim_dia",
                                        CostsState.cv_alim_dia,
                                    ),
                                    cost_field(
                                        "CV2 Preço Combustível",
                                        "preco_comb",
                                        CostsState.preco_comb,
                                        True,
                                        CostsState.info_combustivel,
                                    ),
                                    cost_field(
                                        "CV2 Consumo (km/l)",
                                        "consumo_comb",
                                        CostsState.consumo_comb,
                                        True,
                                        CostsState.info_consumo,
                                    ),
                                    cost_field(
                                        "CV3 Óleo e Filtro",
                                        "cv_oleo",
                                        CostsState.cv_oleo,
                                        True,
                                        "Valor total da troca (cada 10k km)",
                                    ),
                                    cost_field(
                                        "CV4 Troca de Pneus",
                                        "cv_pneu",
                                        CostsState.cv_pneu,
                                        True,
                                        "Valor do jogo completo (cada 60k km)",
                                    ),
                                    cost_field(
                                        "CV5 Manut. Preventiva",
                                        "cv_manut_mensal",
                                        CostsState.cv_manut_mensal,
                                        True,
                                        "Mensal: filtros, paletas, lâmpadas",
                                    ),
                                    cost_field(
                                        "CV6 Lavagem (Mês)",
                                        "cv_lavagem",
                                        CostsState.cv_lavagem,
                                    ),
                                    cost_field(
                                        "CV7 Alinhamento",
                                        "cv_alinhamento",
                                        CostsState.cv_alinhamento,
                                        True,
                                        "Valor por serviço (cada 10k km)",
                                    ),
                                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10",
                                ),
                                rx.el.h2(
                                    "Custos Percentuais & Margens (CP)",
                                    class_name="text-lg font-bold text-gray-800 border-b-2 border-blue-500 pb-2 mb-6",
                                ),
                                rx.el.div(
                                    cost_field(
                                        "Remuneração Semanal (R$)",
                                        "remuneracao_semanal",
                                        CostsState.remuneracao_semanal,
                                        True,
                                        "Valor semanal desejado — base para cálculo de ISS e ICMS",
                                    ),
                                    cost_field(
                                        "CP1 IRPF Estimado",
                                        "cp_irpf",
                                        CostsState.cp_irpf,
                                        False,
                                        "11% sobre 60% de (CF+CV) — calculado nos resultados",
                                    ),
                                    cost_field(
                                        "CP2 ISS (%)",
                                        "cp_iss",
                                        CostsState.cp_iss,
                                    ),
                                    cost_field(
                                        "CP3 ICMS (%)",
                                        "cp_icms",
                                        CostsState.cp_icms,
                                        True,
                                        "Apenas corridas intermunicipais",
                                    ),
                                    cost_field(
                                        "CP4 IPCA (%)",
                                        "cp_ipca",
                                        CostsState.cp_ipca,
                                        False,
                                        "Fonte: IBGE (automático)",
                                    ),
                                    cost_field(
                                        "Margem Lucro ISS (%)",
                                        "margem_iss",
                                        CostsState.margem_iss,
                                    ),
                                    cost_field(
                                        "Margem Lucro ICMS (%)",
                                        "margem_icms",
                                        CostsState.margem_icms,
                                    ),
                                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6",
                                ),
                                class_name="bg-white p-8 rounded-3xl border border-gray-200 shadow-sm",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Salvar Todos os Custos",
                                    type="submit",
                                    class_name="bg-blue-600 text-white font-bold py-4 px-12 rounded-2xl hover:bg-blue-700 transition-all shadow-lg hover:shadow-blue-200",
                                ),
                                class_name="mt-8 flex justify-end",
                            ),
                        ),
                        on_submit=CostsState.save_costs,
                        reset_on_submit=False,
                    ),
                    rx.el.div(
                        rx.icon(
                            "circle_alert",
                            class_name="h-12 w-12 text-red-500 mb-4 mx-auto",
                        ),
                        rx.el.p(
                            "Nenhum veículo ativo selecionado.",
                            class_name="text-red-700 font-bold text-lg",
                        ),
                        rx.el.p(
                            "Vá até a página de Veículos e selecione um veículo para calcular os custos.",
                            class_name="text-red-600 mt-2",
                        ),
                        rx.el.a(
                            rx.el.button(
                                "Ir para Veículos",
                                class_name="mt-6 bg-red-600 text-white font-bold py-2 px-6 rounded-xl",
                            ),
                            href="/app/veiculos",
                        ),
                        class_name="bg-red-50 text-center p-12 rounded-3xl border border-red-200",
                    ),
                ),
                rx.el.div(
                    rx.icon(
                        "loader",
                        class_name="h-8 w-8 text-blue-500 animate-spin mx-auto",
                    ),
                    rx.el.p(
                        "Carregando custos...",
                        class_name="text-gray-500 text-center mt-4",
                    ),
                    class_name="flex flex-col items-center justify-center py-20",
                ),
            ),
        ),
        "/app/custos",
    )