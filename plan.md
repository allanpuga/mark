# Plano de Correção do Callback Google e Banco

## Phase 1: Diagnóstico do banco e callback ✅
- [x] Validar conexão com o banco sem expor credenciais.
- [x] Conferir colunas exigidas pelo login Google nas tabelas existentes.
- [x] Identificar incompatibilidades entre banco antigo e fluxo atual.
- [x] Confirmar se o travamento ocorre por falha silenciosa no callback.

## Phase 2: Correção de compatibilidade ✅
- [x] Adicionar migração automática segura para bancos já existentes.
- [x] Garantir que login Google funcione com usuários novos e existentes.
- [x] Melhorar fallback do callback para retornar ao login com erro claro.
- [x] Manter visual atual com fundo cinza-50, cartões brancos e acento azul.

## Phase 3: Validação final ✅
- [x] Executar a migração automática no banco real.
- [x] Validar colunas necessárias após a correção.
- [x] Testar autenticação local principal.
- [x] Validar build de produção.