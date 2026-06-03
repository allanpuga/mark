import reflex as rx
import os
import uuid
import urllib.parse
from gestor_de_ganhos_motoristas.states.auth_state import AuthState
from gestor_de_ganhos_motoristas.states.legal_state import LegalState


_GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:3000/auth/google/callback",
)

# Public, stable fallback client ID used when GOOGLE_CLIENT_ID env var is
# not available at render time (e.g. SSR/HTML public render in production).
# This is a public OAuth client identifier (not a secret) and is safe to
# embed in the frontend. The corresponding GOOGLE_CLIENT_SECRET is kept
# strictly on the backend and is never exposed.
GOOGLE_PUBLIC_CLIENT_ID_FALLBACK = (
    "279822128338-d1u9rt6vbvg8g9f5hamqu070rrf3sbl8.apps.googleusercontent.com"
)


def build_google_oauth_url() -> str:
    """Build the Google OAuth authorization URL at render time.

    Resolution order for the client ID:
      1. GOOGLE_CLIENT_ID environment variable (preferred).
      2. Public stable fallback embedded above.
    Only when BOTH are empty do we return /?google_error=not_configured.
    Never emit a placeholder, empty, or invalid client_id.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if not client_id:
        client_id = GOOGLE_PUBLIC_CLIENT_ID_FALLBACK.strip()
    if not client_id:
        return "/?google_error=not_configured"
    params = {
        "client_id": client_id,
        "redirect_uri": _GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "state": str(uuid.uuid4()),
    }
    return (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode(params)
    )


GOOGLE_OAUTH_URL = build_google_oauth_url()


_GOOGLE_ERROR_MESSAGES: dict[str, str] = {
    "not_configured": "O login com Google não está configurado neste ambiente. Use seu usuário e senha.",
    "invalid_client": "Credenciais Google inválidas. Use seu usuário e senha ou tente novamente em instantes.",
    "callback_timeout": "O login com Google demorou demais para responder. Tente novamente.",
    "finalize_timeout": "Não conseguimos finalizar seu login com Google. Tente novamente.",
    "token_failed": "Falha ao validar o token do Google. Tente novamente.",
    "no_access_token": "O Google não retornou um token válido. Tente novamente.",
    "userinfo_failed": "Não conseguimos obter seus dados do Google. Tente novamente.",
    "email_not_verified": "Seu e-mail Google não está verificado. Verifique no Google e tente novamente.",
    "missing_code": "Código de autorização ausente. Tente novamente.",
    "missing_token": "Sessão de login expirada. Tente novamente.",
    "cancelled": "Login com Google cancelado.",
    "network_error": "Erro de rede ao falar com o Google. Tente novamente.",
    "db_error": "Erro ao registrar seu acesso. Tente novamente em instantes.",
    "preflight_error": "Erro inesperado ao iniciar o login Google. Tente novamente.",
    "session_error": "Erro ao criar a sessão. Tente novamente.",
    "start_error": "Erro ao iniciar o login com Google. Tente novamente.",
}


class GoogleErrorState(rx.State):
    """Reads google_error from query string for friendly UI messaging."""

    @rx.var
    def error_code(self) -> str:
        return self.router.page.params.get("google_error", "") or ""

    @rx.var
    def error_message(self) -> str:
        code = self.router.page.params.get("google_error", "") or ""
        if not code:
            return ""
        return _GOOGLE_ERROR_MESSAGES.get(
            code,
            "Não foi possível concluir o login com Google. Use seu usuário e senha ou tente novamente.",
        )

    @rx.var
    def has_error(self) -> bool:
        return bool(self.router.page.params.get("google_error", ""))


def google_error_banner() -> rx.Component:
    return rx.cond(
        GoogleErrorState.has_error,
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "circle_alert",
                    class_name="h-5 w-5 text-amber-600 shrink-0 mt-0.5",
                ),
                rx.el.div(
                    rx.el.p(
                        "Login com Google indisponível",
                        class_name="text-sm font-bold text-amber-900",
                    ),
                    rx.el.p(
                        GoogleErrorState.error_message,
                        class_name="text-sm text-amber-800 mt-0.5",
                    ),
                    class_name="flex flex-col",
                ),
                class_name="flex items-start gap-3",
            ),
            class_name="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-2xl",
        ),
        rx.fragment(),
    )


def legal_card(title: str, content_component: rx.Component) -> rx.Component:
    """Standard layout for legal views."""
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.el.div(
                    rx.icon("arrow-left", class_name="h-4 w-4"),
                    rx.el.span(
                        "Voltar para o Login", class_name="font-semibold"
                    ),
                    class_name="flex items-center gap-2 text-blue-600 hover:text-blue-700 transition-colors mb-6",
                ),
                on_click=LegalState.show_login,
                type="button",
            ),
            rx.el.h1(title, class_name="text-3xl font-bold text-gray-900 mb-2"),
            rx.el.p(
                "Última atualização: 20 de Maio de 2024",
                class_name="text-gray-500 text-sm mb-8",
            ),
            content_component,
            class_name="bg-white p-8 md:p-12 rounded-3xl border border-gray-100 shadow-sm w-full max-w-4xl",
        ),
        class_name="flex items-center justify-center min-h-screen p-4 bg-gray-50",
    )


def privacy_content() -> rx.Component:
    return rx.el.div(
        rx.el.section(
            rx.el.h2(
                "1. Coleta de Dados",
                class_name="text-xl font-bold text-gray-800 mb-4",
            ),
            rx.el.p(
                "O Gestão Markup coleta informações essenciais para o cálculo de rentabilidade do motorista de aplicativo. Ao utilizar nossa plataforma via login local ou Google OAuth, armazenamos seu nome, e-mail e identificadores únicos de sessão.",
                class_name="text-gray-600 mb-4",
            ),
            class_name="mb-10",
        ),
        rx.el.section(
            rx.el.h2(
                "2. Security",
                class_name="text-xl font-bold text-gray-800 mb-4",
            ),
            rx.el.p(
                "Suas senhas são criptografadas utilizando algoritmos de hashing robustos (bcrypt). Mantemos seus dados enquanto sua conta estiver ativa.",
                class_name="text-gray-600 mb-4",
            ),
            class_name="mb-10",
        ),
    )


def terms_content() -> rx.Component:
    return rx.el.div(
        rx.el.section(
            rx.el.h2(
                "1. Aceite dos Termos",
                class_name="text-xl font-bold text-gray-800 mb-4",
            ),
            rx.el.p(
                "Ao acessar o Gestão Markup, você concorda em cumprir estes termos de serviço. Esta ferramenta foi desenvolvida exclusivamente para auxiliar motoristas de aplicativo na gestão de seus custos operacionais.",
                class_name="text-gray-600 mb-4",
            ),
            class_name="mb-10",
        ),
        rx.el.section(
            rx.el.h2(
                "2. Isenção de Responsabilidade",
                class_name="text-xl font-bold text-gray-800 mb-4",
            ),
            rx.el.p(
                "Os cálculos de Markup são estimativas baseadas nos dados fornecidos pelo usuário. O Gestão Markup não garante lucros específicos.",
                class_name="text-gray-600 mb-4",
            ),
            class_name="mb-10",
        ),
    )


def login_card() -> rx.Component:
    """Login form card used in the landing hero."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("log-in", class_name="h-6 w-6 text-blue-600"),
                    class_name="p-3 bg-blue-50 rounded-xl w-fit mb-4",
                ),
                rx.el.h2(
                    "Acesse sua conta",
                    class_name="text-2xl font-bold text-gray-900",
                ),
                rx.el.p(
                    "Entre para gerenciar sua lucratividade",
                    class_name="text-gray-500 mt-1 text-sm",
                ),
                class_name="mb-6",
            ),
            google_error_banner(),
            rx.el.form(
                rx.el.div(
                    rx.el.label(
                        "Usuário",
                        class_name="block text-sm font-semibold text-gray-700 mb-1",
                    ),
                    rx.el.input(
                        name="username",
                        placeholder="Seu usuário",
                        class_name="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition-all mb-4",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "Senha",
                        class_name="block text-sm font-semibold text-gray-700 mb-1",
                    ),
                    rx.el.input(
                        type="password",
                        name="password",
                        placeholder="••••••••",
                        class_name="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-600 outline-none transition-all mb-5",
                    ),
                ),
                rx.el.button(
                    "Entrar",
                    type="submit",
                    class_name="w-full bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition-all shadow-md hover:shadow-lg",
                ),
                on_submit=AuthState.handle_login,
            ),
            rx.el.div(
                rx.el.span(
                    "ou",
                    class_name="px-3 bg-white text-gray-400 text-xs font-medium uppercase tracking-wider",
                ),
                class_name="relative flex justify-center text-sm mt-6 mb-6 before:absolute before:inset-0 before:top-1/2 before:h-px before:w-full before:bg-gray-200 before:z-[-1]",
            ),
            rx.el.a(
                rx.el.div(
                    rx.icon("omega", class_name="h-5 w-5 text-gray-700"),
                    rx.el.span(
                        "Entrar com Google",
                        class_name="text-gray-700 font-bold",
                    ),
                    class_name="w-full bg-white border border-gray-200 py-3 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all flex items-center justify-center gap-2",
                ),
                href="/api/auth/google/start",
                class_name="block w-full",
            ),
            rx.el.div(
                rx.el.a(
                    "Esqueceu a senha?",
                    href="/recuperar-senha",
                    class_name="text-sm text-blue-600 hover:underline",
                ),
                rx.el.div(
                    rx.el.span(
                        "Não tem uma conta? ",
                        class_name="text-sm text-gray-500",
                    ),
                    rx.el.a(
                        "Cadastre-se grátis",
                        href="/registrar",
                        class_name="text-sm text-blue-600 font-semibold hover:underline",
                    ),
                    class_name="mt-3",
                ),
                class_name="mt-6 text-center",
            ),
            class_name="bg-white p-8 rounded-3xl border border-gray-200 shadow-sm w-full",
        ),
        class_name="w-full max-w-md",
    )


def benefit_card(icon: str, title: str, desc: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-blue-600"),
            class_name="p-3 bg-blue-50 rounded-xl w-fit mb-4",
        ),
        rx.el.h3(title, class_name="text-lg font-bold text-gray-900 mb-2"),
        rx.el.p(desc, class_name="text-gray-600 text-sm leading-relaxed"),
        class_name="bg-white p-6 rounded-2xl border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all",
    )


def step_card(number: str, title: str, desc: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                number,
                class_name="text-sm font-bold text-blue-600 bg-blue-50 rounded-lg w-8 h-8 flex items-center justify-center",
            ),
            rx.icon(icon, class_name="h-5 w-5 text-gray-400"),
            class_name="flex items-center justify-between mb-4",
        ),
        rx.el.h3(title, class_name="text-lg font-bold text-gray-900 mb-2"),
        rx.el.p(desc, class_name="text-gray-600 text-sm leading-relaxed"),
        class_name="bg-white p-6 rounded-2xl border border-gray-200",
    )


def metric_card(value: str, label: str) -> rx.Component:
    return rx.el.div(
        rx.el.p(
            value,
            class_name="text-3xl md:text-4xl font-extrabold text-blue-600",
        ),
        rx.el.p(
            label,
            class_name="text-gray-600 text-sm font-medium mt-1",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-200 text-center",
    )


def public_navbar() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("trending-up", class_name="h-5 w-5 text-blue-600"),
                    class_name="p-2 bg-blue-50 rounded-lg",
                ),
                rx.el.span(
                    "Gestão Markup",
                    class_name="text-lg font-bold text-gray-900",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.div(
                rx.el.a(
                    "Recursos",
                    href="#recursos",
                    class_name="hidden md:inline text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors",
                ),
                rx.el.a(
                    "Como funciona",
                    href="#como-funciona",
                    class_name="hidden md:inline text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors",
                ),
                rx.el.a(
                    "Entrar",
                    href="#login",
                    class_name="text-sm font-semibold text-gray-700 hover:text-blue-600 transition-colors",
                ),
                rx.el.a(
                    "Cadastre-se",
                    href="/registrar",
                    class_name="px-4 py-2 bg-blue-600 text-white text-sm font-bold rounded-xl hover:bg-blue-700 transition-all shadow-sm",
                ),
                class_name="flex items-center gap-4 md:gap-6",
            ),
            class_name="max-w-6xl mx-auto px-4 md:px-8 h-16 flex items-center justify-between",
        ),
        class_name="bg-white border-b border-gray-200 sticky top-0 z-40",
    )


def public_footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("trending-up", class_name="h-5 w-5 text-blue-600"),
                    rx.el.span(
                        "Gestão Markup",
                        class_name="font-bold text-gray-900",
                    ),
                    class_name="flex items-center gap-2 mb-2",
                ),
                rx.el.p(
                    "Calcule o markup ideal e garanta lucratividade real nas corridas.",
                    class_name="text-gray-500 text-sm max-w-md",
                ),
            ),
            rx.el.div(
                rx.el.a(
                    "Termos",
                    href="/termos",
                    class_name="text-sm text-gray-500 hover:text-blue-600 transition-colors",
                ),
                rx.el.a(
                    "Privacidade",
                    href="/privacidade",
                    class_name="text-sm text-gray-500 hover:text-blue-600 transition-colors",
                ),
                rx.el.a(
                    "Entrar",
                    href="#login",
                    class_name="text-sm text-gray-500 hover:text-blue-600 transition-colors",
                ),
                rx.el.a(
                    "Cadastre-se",
                    href="/registrar",
                    class_name="text-sm text-gray-500 hover:text-blue-600 transition-colors",
                ),
                class_name="flex flex-wrap gap-6",
            ),
            class_name="max-w-6xl mx-auto px-4 md:px-8 py-8 flex flex-col md:flex-row md:items-center md:justify-between gap-6",
        ),
        rx.el.div(
            rx.el.p(
                "© 2024 Gestão Markup. Todos os direitos reservados.",
                class_name="text-xs text-gray-400 text-center",
            ),
            class_name="border-t border-gray-200 py-4 px-4",
        ),
        class_name="bg-white border-t border-gray-200 mt-16",
    )


def landing_hero() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "sparkles", class_name="h-3.5 w-3.5 text-blue-600"
                        ),
                        rx.el.span(
                            "Para motoristas de aplicativo",
                            class_name="text-xs font-semibold text-blue-700",
                        ),
                        class_name="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 border border-blue-100 rounded-full w-fit mb-6",
                    ),
                    rx.el.h1(
                        "Calcule o markup ideal e ",
                        rx.el.span(
                            "lucre de verdade",
                            class_name="text-blue-600",
                        ),
                        " em cada corrida",
                        class_name="text-4xl md:text-5xl lg:text-6xl font-extrabold text-gray-900 leading-tight tracking-tight mb-5",
                    ),
                    rx.el.p(
                        "O Gestão Markup é a ferramenta completa para Uber, 99 e demais apps que considera todos os seus custos fixos, variáveis e percentuais para revelar o valor mínimo por km e por hora — e quanto você precisa cobrar para ter margem real.",
                        class_name="text-lg text-gray-600 leading-relaxed mb-8 max-w-xl",
                    ),
                    rx.el.div(
                        rx.el.a(
                            rx.el.button(
                                rx.icon("rocket", class_name="h-4 w-4"),
                                "Criar conta grátis",
                                class_name="bg-blue-600 text-white font-bold py-3 px-6 rounded-xl hover:bg-blue-700 transition-all shadow-md hover:shadow-lg flex items-center gap-2",
                            ),
                            href="/registrar",
                        ),
                        rx.el.a(
                            rx.el.button(
                                "Já tenho conta",
                                class_name="bg-white text-gray-700 font-bold py-3 px-6 rounded-xl border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-all",
                            ),
                            href="#login",
                        ),
                        class_name="flex flex-wrap gap-3 mb-6",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "shield-check",
                                class_name="h-4 w-4 text-emerald-600",
                            ),
                            rx.el.span(
                                "Sem cartão",
                                class_name="text-xs font-medium text-gray-600",
                            ),
                            class_name="flex items-center gap-1.5",
                        ),
                        rx.el.div(
                            rx.icon(
                                "lock", class_name="h-4 w-4 text-emerald-600"
                            ),
                            rx.el.span(
                                "Dados criptografados",
                                class_name="text-xs font-medium text-gray-600",
                            ),
                            class_name="flex items-center gap-1.5",
                        ),
                        rx.el.div(
                            rx.icon(
                                "zap", class_name="h-4 w-4 text-emerald-600"
                            ),
                            rx.el.span(
                                "Resultados em 5 min",
                                class_name="text-xs font-medium text-gray-600",
                            ),
                            class_name="flex items-center gap-1.5",
                        ),
                        class_name="flex flex-wrap gap-4",
                    ),
                ),
                rx.el.div(
                    rx.el.div(id="login"),
                    login_card(),
                    class_name="w-full flex justify-center lg:justify-end",
                ),
                class_name="grid lg:grid-cols-2 gap-12 items-center",
            ),
            class_name="max-w-6xl mx-auto px-4 md:px-8 py-12 md:py-20",
        ),
    )


def metrics_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                metric_card("R$ 0,00", "Custo mínimo por km"),
                metric_card("100%", "Custos contemplados"),
                metric_card("FIPE", "Integração automática"),
                metric_card("IBGE", "IPCA atualizado"),
                class_name="grid grid-cols-2 md:grid-cols-4 gap-4",
            ),
            class_name="max-w-6xl mx-auto px-4 md:px-8",
        ),
    )


def benefits_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Recursos",
                        class_name="text-xs font-bold text-blue-600 uppercase tracking-wider",
                    ),
                    rx.el.h2(
                        "Tudo que você precisa para precificar suas corridas",
                        class_name="text-3xl md:text-4xl font-bold text-gray-900 mt-2 mb-3",
                    ),
                    rx.el.p(
                        "Pare de adivinhar — calcule com base em dados reais do seu veículo, do seu estado e da sua rotina.",
                        class_name="text-gray-600 text-lg max-w-2xl mx-auto",
                    ),
                    class_name="text-center mb-12",
                ),
                rx.el.div(
                    benefit_card(
                        "car",
                        "Tabela FIPE integrada",
                        "Cadastre seu veículo selecionando marca, modelo e ano. Buscamos o valor FIPE automaticamente.",
                    ),
                    benefit_card(
                        "wallet",
                        "Custos completos",
                        "Custos fixos, variáveis e percentuais — depreciação, IPVA, combustível, manutenção e impostos.",
                    ),
                    benefit_card(
                        "calculator",
                        "Markup preciso",
                        "Calcule o valor mínimo por km e por hora considerando ISS, ICMS, IPCA e sua margem de lucro.",
                    ),
                    benefit_card(
                        "map-pin",
                        "Dados regionais",
                        "Alíquotas de IPVA, licenciamento e preço médio de combustível ajustados por estado.",
                    ),
                    benefit_card(
                        "history",
                        "Histórico salvo",
                        "Salve simulações, compare diferentes cenários e acompanhe a evolução dos seus custos.",
                    ),
                    benefit_card(
                        "shield",
                        "Login seguro",
                        "Senhas criptografadas com bcrypt e opção de login com Google.",
                    ),
                    class_name="grid md:grid-cols-2 lg:grid-cols-3 gap-5",
                ),
                id="recursos",
            ),
            class_name="max-w-6xl mx-auto px-4 md:px-8 py-16 md:py-20",
        ),
    )


def how_it_works_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Como funciona",
                        class_name="text-xs font-bold text-blue-600 uppercase tracking-wider",
                    ),
                    rx.el.h2(
                        "Em 4 passos você descobre seu markup ideal",
                        class_name="text-3xl md:text-4xl font-bold text-gray-900 mt-2 mb-3",
                    ),
                    rx.el.p(
                        "Um fluxo guiado para você focar no que importa: dirigir e lucrar.",
                        class_name="text-gray-600 text-lg max-w-2xl mx-auto",
                    ),
                    class_name="text-center mb-12",
                ),
                rx.el.div(
                    step_card(
                        "1",
                        "Cadastre seu perfil",
                        "Informe seu estado, cidade e rotina: dias por semana, horas por dia e km percorridos.",
                        "user",
                    ),
                    step_card(
                        "2",
                        "Adicione seu veículo",
                        "Selecione marca, modelo, ano e tipo de posse. Buscamos o valor FIPE automaticamente.",
                        "truck",
                    ),
                    step_card(
                        "3",
                        "Configure seus custos",
                        "Revise custos fixos, variáveis e percentuais. Vários campos vêm preenchidos para você.",
                        "wallet",
                    ),
                    step_card(
                        "4",
                        "Veja seu markup",
                        "Descubra custo mínimo, valor ideal por km, faturamento mensal e margem de lucro.",
                        "bar-chart-3",
                    ),
                    class_name="grid md:grid-cols-2 lg:grid-cols-4 gap-5",
                ),
                id="como-funciona",
            ),
            class_name="max-w-6xl mx-auto px-4 md:px-8 py-16 md:py-20",
        ),
        class_name="bg-white border-y border-gray-200",
    )


def cta_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("trending-up", class_name="h-6 w-6 text-white"),
                    class_name="p-3 bg-white/20 rounded-xl w-fit mx-auto mb-5",
                ),
                rx.el.h2(
                    "Comece a precificar com inteligência hoje",
                    class_name="text-3xl md:text-4xl font-bold text-white mb-3",
                ),
                rx.el.p(
                    "Crie sua conta grátis em menos de 1 minuto e descubra quanto você realmente precisa cobrar.",
                    class_name="text-blue-100 text-lg mb-8 max-w-xl mx-auto",
                ),
                rx.el.div(
                    rx.el.a(
                        rx.el.button(
                            "Criar conta grátis",
                            class_name="bg-white text-blue-600 font-bold py-3 px-6 rounded-xl hover:bg-gray-50 transition-all shadow-md",
                        ),
                        href="/registrar",
                    ),
                    rx.el.a(
                        rx.el.button(
                            "Fazer login",
                            class_name="bg-transparent text-white font-bold py-3 px-6 rounded-xl border border-white/40 hover:bg-white/10 transition-all",
                        ),
                        href="#login",
                    ),
                    class_name="flex flex-wrap gap-3 justify-center",
                ),
                class_name="text-center",
            ),
            class_name="max-w-4xl mx-auto px-4 md:px-8 py-14 md:py-16 bg-blue-600 rounded-3xl my-16 mx-4 md:mx-8",
        ),
    )


def login_form() -> rx.Component:
    """Full public landing page that does not depend on the database."""
    return rx.el.div(
        public_navbar(),
        landing_hero(),
        metrics_section(),
        benefits_section(),
        how_it_works_section(),
        cta_section(),
        public_footer(),
        class_name="bg-gray-50 min-h-screen",
    )


def login_page() -> rx.Component:
    """Public entry page that handles safe legal views."""
    return rx.el.div(
        rx.match(
            LegalState.current_view,
            ("terms", legal_card("Termos de Uso", terms_content())),
            (
                "privacy",
                legal_card("Política de Privacidade", privacy_content()),
            ),
            login_form(),
        ),
        class_name="font-['Inter']",
    )


# Legacy direct pages as fallback
def privacy_policy_page() -> rx.Component:
    return legal_card("Política de Privacidade", privacy_content())


def terms_of_service_page() -> rx.Component:
    return legal_card("Termos de Uso", terms_content())


def register_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Criar Conta",
                    class_name="text-2xl font-bold text-gray-900 text-center mb-8",
                ),
                rx.el.form(
                    rx.el.div(
                        rx.el.label(
                            "Nome de Usuário",
                            class_name="block text-sm font-semibold text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            name="username",
                            placeholder="Escolha um usuário",
                            class_name="w-full px-4 py-3 border border-gray-200 rounded-xl mb-4",
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
                            placeholder="seu@email.com",
                            class_name="w-full px-4 py-3 border border-gray-200 rounded-xl mb-4",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Senha",
                            class_name="block text-sm font-semibold text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            name="password",
                            type="password",
                            placeholder="Mínimo 6 caracteres",
                            class_name="w-full px-4 py-3 border border-gray-200 rounded-xl mb-4",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Confirmar Senha",
                            class_name="block text-sm font-semibold text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            name="confirm_password",
                            type="password",
                            placeholder="Repita a senha",
                            class_name="w-full px-4 py-3 border border-gray-200 rounded-xl mb-6",
                        ),
                    ),
                    rx.el.button(
                        "Registrar",
                        type="submit",
                        class_name="w-full bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition-all shadow-md",
                    ),
                    on_submit=AuthState.handle_register,
                ),
                rx.el.div(
                    rx.el.span(
                        "ou",
                        class_name="px-3 bg-white text-gray-400 text-xs font-medium uppercase tracking-wider",
                    ),
                    class_name="relative flex justify-center text-sm mt-6 mb-6 before:absolute before:inset-0 before:top-1/2 before:h-px before:w-full before:bg-gray-200 before:z-[-1]",
                ),
                rx.el.a(
                    rx.el.div(
                        rx.icon("omega", class_name="h-5 w-5 text-gray-700"),
                        rx.el.span(
                            "Cadastrar com Google",
                            class_name="text-gray-700 font-bold",
                        ),
                        class_name="w-full bg-white border border-gray-200 py-3 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all flex items-center justify-center gap-2",
                    ),
                    href="/api/auth/google/start",
                    class_name="block w-full mb-6",
                ),
                rx.el.div(
                    rx.el.a(
                        "Voltar para login",
                        href="/",
                        class_name="text-sm text-blue-600 font-semibold hover:underline",
                    ),
                    rx.el.div(
                        rx.el.span(
                            "Ao registrar, você concorda com nossos ",
                            class_name="text-xs text-gray-400",
                        ),
                        rx.el.a(
                            "Termos",
                            href="/termos",
                            class_name="text-xs text-blue-500 hover:underline",
                        ),
                        rx.el.span(" e ", class_name="text-xs text-gray-400"),
                        rx.el.a(
                            "Privacidade",
                            href="/privacidade",
                            class_name="text-xs text-blue-500 hover:underline",
                        ),
                        class_name="mt-8",
                    ),
                    class_name="mt-6 text-center",
                ),
                class_name="bg-white p-10 rounded-3xl shadow-xl border border-gray-100 w-full max-w-md",
            ),
            class_name="flex items-center justify-center min-h-screen p-4 bg-gray-50",
        ),
        class_name="font-['Inter']",
    )


def google_start_page() -> rx.Component:
    """Fallback page that redirects to Google via meta refresh + JS + link.

    Builds the Google OAuth URL at render time (server-side) using the
    public client_id resolution (env var or stable fallback). Does NOT
    depend on AuthState, websocket, /auth/google/start or
    /api/auth/google/start endpoints.
    """
    oauth_url = build_google_oauth_url()
    js_redirect = (
        "(function(){try{window.location.replace("
        + repr(oauth_url)
        + ");}catch(e){window.location.href="
        + repr(oauth_url)
        + ";}})();"
    )
    return rx.el.div(
        rx.el.script(js_redirect),
        rx.el.meta(http_equiv="refresh", content=f"0; url={oauth_url}"),
        rx.el.div(
            rx.icon(
                "loader",
                class_name="h-10 w-10 text-blue-600 animate-spin mb-4",
            ),
            rx.el.h2(
                "Redirecionando para o Google...",
                class_name="text-xl font-bold text-gray-900",
            ),
            rx.el.p(
                "Você será encaminhado em instantes.",
                class_name="text-gray-500 text-sm mt-2 text-center max-w-sm",
            ),
            rx.el.p(
                "Se a página não carregar automaticamente, use o botão abaixo.",
                class_name="text-gray-400 text-xs mt-4 text-center max-w-sm",
            ),
            rx.el.a(
                "Continuar para o Google",
                href=oauth_url,
                class_name="mt-6 inline-block px-5 py-2.5 bg-blue-600 text-white text-sm font-bold rounded-xl hover:bg-blue-700 transition-all",
            ),
            rx.el.a(
                "Voltar para o login",
                href="/",
                class_name="mt-3 inline-block text-sm text-blue-600 font-semibold hover:underline",
            ),
            class_name="flex flex-col items-center justify-center bg-white p-10 rounded-3xl shadow-sm border border-gray-200 max-w-md w-full",
        ),
        class_name="flex items-center justify-center min-h-screen p-4 bg-gray-50 font-['Inter']",
    )


def google_callback_page() -> rx.Component:
    """Callback page that triggers AuthState.handle_google_callback on_load.

    The on_load event processes the OAuth code directly with httpx in the
    Reflex backend and redirects to /app/perfil on success or to /
    with a google_error code on failure. A client-side timeout sends the
    user back to /?google_error=callback_timeout if the on_load event
    never completes (e.g. websocket failure).
    """
    timeout_script = (
        "(function(){"
        "setTimeout(function(){"
        "try{"
        "if(window.location.pathname.indexOf('/auth/google/callback')===0){"
        "window.location.replace('/?google_error=callback_timeout');"
        "}"
        "}catch(e){}"
        "},10000);"
        "})();"
    )
    return rx.el.div(
        rx.el.script(timeout_script),
        rx.el.div(
            rx.icon(
                "loader",
                class_name="h-10 w-10 text-blue-600 animate-spin mb-4",
            ),
            rx.el.h2(
                "Processando login com Google...",
                class_name="text-xl font-bold text-gray-900",
            ),
            rx.el.p(
                "Aguarde enquanto validamos sua autenticação.",
                class_name="text-gray-500 text-sm mt-2 text-center max-w-sm",
            ),
            rx.el.p(
                "Se demorar mais de alguns segundos, sua sessão será reiniciada.",
                class_name="text-gray-400 text-xs mt-4 text-center max-w-sm",
            ),
            rx.el.a(
                "Voltar para o login",
                href="/?google_error=cancelled",
                class_name="mt-6 inline-block text-sm text-blue-600 font-semibold hover:underline",
            ),
            class_name="flex flex-col items-center justify-center bg-white p-10 rounded-3xl shadow-sm border border-gray-200 max-w-md w-full",
        ),
        class_name="flex items-center justify-center min-h-screen p-4 bg-gray-50 font-['Inter']",
    )


def google_finalize_page() -> rx.Component:
    """Final step page that consumes the OTT and sets the Reflex session.

    The Reflex on_load event AuthState.finalize_google_auth performs the
    actual session activation. As a safety net, if the user lands here
    without a valid OTT (or the websocket fails to connect), a visible
    fallback button always lets them return to the login screen.
    """
    fallback_script = (
        "(function(){"
        "setTimeout(function(){"
        "try{"
        "var p=new URLSearchParams(window.location.search);"
        "if(!p.get('ott')){window.location.replace('/?google_error=missing_token');}"
        "}catch(e){}"
        "},800);"
        "setTimeout(function(){"
        "try{"
        "if(window.location.pathname.indexOf('/auth/google/finalize')===0){"
        "window.location.replace('/?google_error=finalize_timeout');"
        "}"
        "}catch(e){}"
        "},8000);"
        "})();"
    )
    return rx.el.div(
        rx.el.script(fallback_script),
        rx.el.div(
            rx.icon(
                "loader",
                class_name="h-10 w-10 text-blue-600 animate-spin mb-4",
            ),
            rx.el.h2(
                "Concluindo seu login...",
                class_name="text-xl font-bold text-gray-900",
            ),
            rx.el.p(
                "Estamos preparando seu painel.",
                class_name="text-gray-500 text-sm mt-2 text-center max-w-sm",
            ),
            rx.el.p(
                "Se demorar mais de alguns segundos, sua sessão pode ter expirado.",
                class_name="text-gray-400 text-xs mt-4 text-center max-w-sm",
            ),
            rx.el.a(
                "Voltar para o login",
                href="/?google_error=finalize_timeout",
                class_name="mt-6 inline-block px-5 py-2.5 bg-blue-600 text-white text-sm font-bold rounded-xl hover:bg-blue-700 transition-all",
            ),
            class_name="flex flex-col items-center justify-center bg-white p-10 rounded-3xl shadow-sm border border-gray-200 max-w-md w-full",
        ),
        class_name="flex items-center justify-center min-h-screen p-4 bg-gray-50 font-['Inter']",
    )


def recover_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Recuperar Senha",
                    class_name="text-2xl font-bold text-gray-900 mb-4",
                ),
                rx.el.div(
                    rx.icon(
                        "info",
                        class_name="h-12 w-12 text-blue-500 mb-4 mx-auto",
                    ),
                    rx.el.p(
                        "A recuperação de senha estará disponível em breve.",
                        class_name="text-gray-600 mb-6 text-center",
                    ),
                    rx.el.a(
                        rx.el.button(
                            "Voltar para Login",
                            class_name="w-full bg-gray-100 text-gray-700 font-bold py-3 rounded-xl hover:bg-gray-200 transition-all",
                        ),
                        href="/",
                    ),
                    class_name="text-center",
                ),
                class_name="bg-white p-10 rounded-3xl shadow-xl border border-gray-100 w-full max-w-md",
            ),
            class_name="flex items-center justify-center min-h-screen p-4 bg-gray-50",
        ),
        class_name="font-['Inter']",
    )