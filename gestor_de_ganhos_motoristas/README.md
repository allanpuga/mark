
# Gestão Markup

**Gestão Markup** é uma aplicação web completa para motoristas de aplicativo (Uber, 99, etc.) calcularem o markup ideal por quilômetro e por hora, considerando todos os custos operacionais — fixos, variáveis e percentuais — para garantir lucratividade real nas corridas.

---

## Funcionalidades

- **Autenticação** — Login, registro e gerenciamento de sessão com senhas criptografadas (bcrypt)
- **Perfil do Motorista** — Dados pessoais, estado/cidade (API IBGE) e rotina de trabalho (dias/semana, horas/dia, km/dia)
- **Gestão de Veículos** — Cadastro com integração à tabela FIPE (marca, modelo, ano, valor), tipo de posse (próprio, financiamento, aluguel) e categorias de app
- **Custos Operacionais** — Custos fixos (depreciação, IPVA, licenciamento, INSS, seguro), custos variáveis (combustível, manutenção, pneus, alimentação) e custos percentuais (ISS, ICMS, IPCA, IRPF, margens de lucro)
- **Cálculo de Markup** — Custo mínimo por km/hora, valor ideal com impostos e margem, markup sugerido, faturamento bruto mensal
- **Histórico de Resultados** — Salvar, comparar e excluir simulações
- **Painel Administrativo** — Monitoramento de usuários, veículos e resultados salvos

---

## Tech Stack

| Camada        | Tecnologia                                      |
|---------------|--------------------------------------------------|
| Framework     | [Reflex](https://reflex.dev) 0.8.26             |
| Banco de Dados| MySQL 8.x (pymysql + aiomysql)                  |
| Autenticação  | bcrypt                                           |
| Estilização   | Tailwind CSS v3 (via plugin Reflex)              |
| APIs Externas | FIPE (parallelum), IBGE (estados/cidades/IPCA)  |
| Fonte         | Inter (Google Fonts)                             |

---

## Pré-requisitos

- **Python 3.11+**
- **MySQL 8.x** (ou compatível: MariaDB 10.6+)
- **Node.js 18+** (utilizado internamente pelo Reflex)
- **pip** ou **uv** para gerenciamento de pacotes

---

## Instalação

### 1. Clone o repositório

bash
git clone <repo-url>
cd gestao-markup


### 2. Instale as dependências Python

bash
pip install -r requirements.txt


### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (ou exporte as variáveis diretamente):

env
# Google OAuth2 para login (Opcional)
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-client-secret


**URI de Redirecionamento Google:**
Adicione a seguinte URL autorizada no console do Google Cloud para o ambiente de testes atual:
`https://8080-331b29ba-aebd-41c3-8bbc-0531b291adc1.build.reflexsandbox.com`

env
# Conexão MySQL síncrona (pymysql)
DB_URL=mysql+pymysql://usuario:senha@host:3306/nome_do_banco

# Conexão MySQL para o Reflex ORM (mesmo formato)
REFLEX_DB_URL=mysql+pymysql://usuario:senha@host:3306/nome_do_banco

# Conexão MySQL assíncrona (aiomysql)
REFLEX_ASYNC_DB_URL=mysql+aiomysql://usuario:senha@host:3306/nome_do_banco


> **Nota:** As três variáveis apontam para o mesmo banco de dados, apenas com drivers diferentes (`pymysql` para síncrono, `aiomysql` para assíncrono).

#### Exemplo com MySQL local

env
DB_URL=mysql+pymysql://root:minhasenha@localhost:3306/gestao_markup
REFLEX_DB_URL=mysql+pymysql://root:minhasenha@localhost:3306/gestao_markup
REFLEX_ASYNC_DB_URL=mysql+aiomysql://root:minhasenha@localhost:3306/gestao_markup


### 4. Inicialize o banco de dados

bash
reflex db init


A aplicação também cria automaticamente as tabelas necessárias na primeira execução (via `db_init.py`), incluindo um usuário admin padrão:
- **Usuário:** `admin`
- **Senha:** `123456`

### 5. Execute a aplicação

bash
reflex run


A aplicação estará disponível em `http://localhost:3000`.

---

## Estrutura do Projeto


app/
├── app.py                  # Configuração principal, rotas e páginas
├── db_init.py              # Inicialização automática do banco de dados
├── utils.py                # Utilitários (requisições HTTP com retry)
├── components/
│   ├── layout.py           # Layout base com sidebar
│   └── sidebar.py          # Navegação lateral responsiva
├── pages/
│   ├── auth.py             # Login, registro, recuperação de senha
│   ├── perfil.py           # Perfil do motorista
│   ├── veiculos.py         # Gestão de veículos (FIPE)
│   ├── custos.py           # Custos operacionais
│   ├── resultados.py       # Resultados e markup
│   └── admin.py            # Painel administrativo
└── states/
    ├── auth_state.py        # Autenticação e sessão
    ├── profile_state.py     # Perfil e API IBGE
    ├── vehicle_state.py     # Veículos e API FIPE
    ├── costs_state.py       # Custos operacionais
    ├── results_state.py     # Cálculo de markup
    ├── admin_state.py       # Dados administrativos
    └── sidebar_state.py     # Estado da sidebar (mobile)


---

## Deploy em Produção

### Configuração do `rxconfig.py`

Para deploy em produção, edite o `rxconfig.py` adicionando o `api_url` com o domínio público do seu servidor:


import reflex as rx

config = rx.Config(
    app_name="gestor_de_ganhos_motoristas",
    plugins=[rx.plugins.TailwindV3Plugin()],
    # Produção: defina o URL público da API
    api_url="https://seu-dominio.com:8000",
)


> **Importante:** O arquivo `rxconfig.py` atual não inclui `api_url` por padrão, pois em desenvolvimento local o Reflex utiliza `http://localhost:8000` automaticamente. Em produção, este valor **deve** ser configurado para o domínio público.

### Variáveis de ambiente em produção

Certifique-se de que todas as variáveis de ambiente estejam configuradas no ambiente de produção:

env
DB_URL=mysql+pymysql://usuario:senha@db-host:3306/gestao_markup
REFLEX_DB_URL=mysql+pymysql://usuario:senha@db-host:3306/gestao_markup
REFLEX_ASYNC_DB_URL=mysql+aiomysql://usuario:senha@db-host:3306/gestao_markup


### Comandos de deploy

bash
# Build para produção
reflex export

# Ou executar diretamente em modo produção
reflex run --env prod


### Considerações de segurança

- Altere a senha do usuário admin padrão imediatamente após o primeiro deploy
- Use conexões MySQL com SSL em produção (`?ssl=true` na connection string)
- Configure `secure=True` para cookies em ambientes HTTPS
- Mantenha as dependências atualizadas (`pip install -U -r requirements.txt`)

---

## APIs Externas

| API | Uso | Documentação |
|-----|-----|-------------|
| FIPE (Parallelum) | Marcas, modelos, anos e valores de veículos | https://fipe.parallelum.com.br |
| IBGE Localidades | Estados e municípios brasileiros | https://servicodados.ibge.gov.br/api/docs/localidades |
| IBGE IPCA | Índice de inflação atualizado | https://servicodados.ibge.gov.br/api/docs/agregados |

Todas as chamadas a APIs externas utilizam retry automático com backoff exponencial (até 2 tentativas).

---

## Licença

Projeto privado. Todos os direitos reservados.

