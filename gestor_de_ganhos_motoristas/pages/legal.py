import reflex as rx


def legal_header(title: str) -> rx.Component:
    return rx.el.div(
        rx.el.a(
            rx.el.div(
                rx.icon("arrow-left", class_name="h-4 w-4"),
                rx.el.span("Voltar para o Login", class_name="font-semibold"),
                class_name="flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors mb-6",
            ),
            href="/",
        ),
        rx.el.h1(title, class_name="text-3xl font-bold text-gray-900 mb-2"),
        rx.el.p(
            "Última atualização: 20 de Maio de 2024",
            class_name="text-gray-500 text-sm mb-8",
        ),
    )


def legal_section(title: str, content: list[str]) -> rx.Component:
    return rx.el.section(
        rx.el.h2(title, class_name="text-xl font-bold text-gray-800 mb-4"),
        rx.el.div(
            *[
                rx.el.p(p, class_name="text-gray-600 mb-4 leading-relaxed")
                for p in content
            ]
        ),
        class_name="mb-10",
    )


def privacy_policy_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                legal_header("Política de Privacidade"),
                legal_section(
                    "1. Coleta de Dados",
                    [
                        "Coletamos informações necessárias para o cálculo do markup, como dados do veículo e estimativas de custos operacionais.",
                    ],
                ),
                legal_section(
                    "2. Uso das Informações",
                    [
                        "Os dados são processados exclusivamente localmente ou no banco de dados seguro da aplicação para gerar os relatórios de lucratividade.",
                    ],
                ),
                rx.el.div(
                    rx.el.span(
                        "Dúvidas sobre os termos? ", class_name="text-gray-500"
                    ),
                    rx.el.a(
                        "Veja nossos Termos de Serviço",
                        href="/termos",
                        class_name="text-blue-600 font-semibold hover:underline",
                    ),
                    class_name="mt-8 pt-8 border-t border-gray-100 text-center",
                ),
                class_name="bg-white p-8 md:p-12 rounded-3xl border border-gray-200 shadow-sm",
            ),
            class_name="max-w-4xl mx-auto py-12 px-4",
        ),
        class_name="bg-gray-50 min-h-screen font-['Inter']",
    )


def terms_of_service_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                legal_header("Termos de Serviço"),
                legal_section(
                    "1. Aceite dos Termos",
                    [
                        "Ao utilizar a aplicação Gestão Markup, você concorda com as condições de uso aqui descritas para o cálculo de seus indicadores operacionais.",
                    ],
                ),
                legal_section(
                    "2. Precisão dos Cálculos",
                    [
                        "A ferramenta fornece estimativas analíticas baseadas nos valores inseridos pelo usuário e dados referenciais de mercado, como a Tabela FIPE e índices de impostos em sua região específica.",
                    ],
                ),
                legal_section(
                    "3. Uso da Conta",
                    [
                        "A conta é pessoal e intransferível. O uso indevido da plataforma para extração massiva de dados da Tabela FIPE ou outros serviços integrados resultará em suspensão imediata.",
                    ],
                ),
                legal_section(
                    "4. Suporte e Contato",
                    [
                        "O suporte técnico é oferecido via e-mail para usuários cadastrados. Como ferramenta de apoio, o serviço é fornecido 'como está', sem garantias de disponibilidade ininterrupta.",
                    ],
                ),
                rx.el.div(
                    rx.el.span(
                        "Como tratamos seus dados? ", class_name="text-gray-500"
                    ),
                    rx.el.a(
                        "Veja nossa Política de Privacidade",
                        href="/privacidade",
                        class_name="text-blue-600 font-semibold hover:underline",
                    ),
                    class_name="mt-8 pt-8 border-t border-gray-100 text-center",
                ),
                class_name="bg-white p-8 md:p-12 rounded-3xl border border-gray-200 shadow-sm",
            ),
            class_name="max-w-4xl mx-auto py-12 px-4",
        ),
        class_name="bg-gray-50 min-h-screen font-['Inter']",
    )