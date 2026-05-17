# CSPdv

Sistema desktop de ponto de venda e operacao administrativa desenvolvido em `Python + PyQt5`, com foco em operacao de loja, caixa, financeiro, promocoes e administracao central.

## Visao geral

O projeto cobre hoje o fluxo principal de uma operacao de pequeno e medio porte:

- setup inicial do sistema
- autenticacao e selecao de modulo
- abertura, movimentacao e fechamento de caixa
- venda simples com cupom, descontos e pagamento
- venda rapida a partir do painel admin
- venda com pagamento parcial e geracao de conta a receber
- reembolso total e parcial
- financeiro com recebimentos, contas a receber e reembolsos
- estoque com consulta e ajuste
- promocoes com vinculo de produtos
- configuracoes operacionais persistidas
- parametros fiscais persistidos
- gestao de PDVs, unidades e formas de pagamento no painel admin
- backup manual e acompanhamento do ultimo backup
- migrations de banco aplicadas automaticamente no startup

O sistema ja se encontra em um estagio funcional para operacao assistida, com cobertura automatizada relevante nas areas criticas.

## Stack

- `Python 3`
- `PyQt5`
- `MySQL`
- `python-dotenv`
- `bcrypt`

Dependencias principais em [requirements.txt](D:\Python\cspdv\requirements.txt).

## Estrutura do projeto

```text
cspdv/
  core/
  database/
    migrations/
      versions/
  docs/
  modules/
    admin/
    auth/
    categorias/
    clientes/
    estoque/
    financeiro/
    formas_pagamento/
    fornecedores/
    marcas/
    pdvs/
    produtos/
    promocoes/
    relatorios/
    setup/
    shared/
    unidades/
    venda/
  ui/
  utils/
  media/
  tests/
    admin/
    auth/
    core/
    financeiro/
    produtos/
    promocoes/
    setup/
    utils/
    venda/
  main.py
```

## Padrao de arquitetura

O projeto segue, de forma geral, esta separacao:

- `modules/*/models`
  - acesso a dados e consultas
- `modules/*/services`
  - regras de negocio e orquestracao
- `modules/*/views`
  - comportamento e integracao das telas
- `database/migrations/*`
  - evolucao versionada do schema
- `ui/*`
  - layout visual gerado pelo Qt Designer
- `utils/*`
  - helpers compartilhados sem regra de negocio
- `tests/*`
  - testes automatizados organizados por dominio funcional

Hoje o projeto ja usa alguns helpers compartilhados como base:

- [utils/format_utils.py](D:\Python\cspdv\utils\format_utils.py)
- [utils/table_widget_utils.py](D:\Python\cspdv\utils\table_widget_utils.py)
- [utils/combo_loader.py](D:\Python\cspdv\utils\combo_loader.py)
- [utils/ui_messages.py](D:\Python\cspdv\utils\ui_messages.py)

Mais detalhes em [docs/architecture.md](D:\Python\cspdv\docs\architecture.md).

## Migrations e banco

O projeto agora trabalha com schema governado por migrations.

- mudancas estruturais no banco nao devem mais ser feitas em runtime dentro de `models`
- toda alteracao de schema deve virar migration em [database/migrations/versions](D:\Python\cspdv\database\migrations\versions:1)
- as migrations pendentes sao aplicadas automaticamente no inicio da aplicacao
- as versoes aplicadas ficam registradas em `schema_migrations`

Regra pratica:

- mudou estrutura do banco: criar migration
- mudou dado de configuracao ou cadastro: salvar normalmente via `services` e `models`

Padrao atual de nomenclatura:

- `YYYYMMDD_NNN_descricao_curta.py`

Exemplos:

- `20260517_001_config_empresa_defaults.py`
- `20260517_004_caixas_closing_columns.py`
- `20260517_007_referential_actions_history.py`

## Modulos atuais

### Auth

- login
- restauracao de sessao
- selecao de modo no centro de operacoes

### Setup

- wizard de configuracao inicial
- criacao de registros-base
- criacao das formas de pagamento padrao

### Admin

- dashboard administrativo
- alertas operacionais
- acoes essenciais
- gerenciamento central de cadastros
- navegacao reorganizada por grupos
- venda rapida sem sair do painel
- configuracoes persistidas
- area `Operacao e Fiscal`
  - formas de pagamento
  - caixas
  - parametros fiscais
  - unidades
  - PDVs
- status de backup

### Venda

- frente de venda
- venda rapida
- consulta de produto
- consulta de preco
- selecao de cliente
- descontos
- confirmacao de venda
- pagamento
- finalizacao com pendencia
- pos-pagamento
- resumo do caixa atual

### Caixa

- abertura de caixa
- movimentacao de caixa
- fechamento de caixa
- reforco de troco
- sangria e suprimento

### Financeiro

- movimentacoes de caixa
- vendas registradas
- contas a receber
- recebimento de pendencias
- comprovante simples de recebimento
- reembolsos registrados
- consulta de venda

### Operacao e Fiscal

- formas de pagamento sincronizadas com a tela de pagamento
- PDVs com cadastro, edicao e ativacao/desativacao
- unidades com cadastro, edicao e ativacao/desativacao
- parametros fiscais persistidos e ligados ao cadastro de produto

### Estoque

- painel de estoque
- consulta de produtos
- ultimas movimentacoes
- busca e filtros
- ajuste de quantidade

### Promocoes

- painel de promocoes e campanhas
- nova promocao
- edicao
- duplicacao
- encerramento
- cancelamento
- vinculo de produtos
- validacao de conflito entre promocoes sobrepostas

## Fluxos implementados

### Venda simples

1. abrir caixa
2. selecionar produtos
3. aplicar desconto, se necessario
4. confirmar venda
5. lancar pagamentos
6. concluir a venda
7. baixar estoque

### Venda com pendencia

1. montar a venda normalmente
2. registrar pagamento parcial
3. finalizar com pendencia
4. gerar conta a receber
5. receber o saldo depois no financeiro

### Reembolso

- reembolso total
- reembolso parcial
- devolucao de estoque
- registro financeiro
- atualizacao de status da venda

### Promocoes

- cadastro de promocao ou campanha
- regra por percentual, valor ou preco fixo
- vinculo de produtos
- prevencao de conflito com promocoes ativas ou agendadas no mesmo periodo

## Convencoes operacionais importantes

### Identidade de produto

- o `id` da tabela continua sendo a chave interna do sistema
- o campo `Codigo` do cadastro de produto representa `cod_produto`
- `cod_produto`, `codigo_barras` e nome podem ser usados na busca operacional de venda

### Cupom e comprovante

- o pos-pagamento gera `comprovante nao fiscal`
- o botao atual imprime comprovante operacional, nao documento fiscal autorizado

### Itens no cupom

- leituras repetidas do mesmo produto entram como linhas separadas
- `3*produto` adiciona a quantidade diretamente na linha lancada

## Banco de dados

O projeto usa MySQL e depende de variaveis de ambiente carregadas via `.env`.

Entre as tabelas relevantes da operacao atual:

- `vendas`
- `itens_venda`
- `pagamento_parcial`
- `movimentacao_estoque`
- `caixas`
- `caixa_movimentacoes`
- `venda_reembolsos`
- `venda_reembolso_itens`
- `venda_reembolso_pagamentos`
- `contas_receber`
- `contas_receber_recebimentos`
- `promocoes`
- `promocao_produtos`
- `promocao_categorias`
- `promocao_marcas`
- `promocao_pdvs`

A estrutura atual do banco e preparada por migrations versionadas, e nao mais por autoajuste de schema em runtime nos fluxos principais.

## Como executar

### 1. Instale as dependencias

```bash
pip install -r requirements.txt
```

### 2. Configure o `.env`

Variaveis esperadas pelo projeto:

- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `DB_CONNECTION_TIMEOUT`
- `DB_USE_POOL`
- `DB_POOL_NAME`
- `DB_POOL_SIZE`
- `APP_NAME`
- `APP_VERSION`

Exemplo:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=cspdv
DB_CONNECTION_TIMEOUT=5

DB_USE_POOL=true
DB_POOL_NAME=cspdv_pool
DB_POOL_SIZE=10

APP_NAME=CSPdv
APP_VERSION=1.0.0
```

### 3. Execute o sistema

```bash
python main.py
```

### 4. Aplicar migrations manualmente, se necessario

```bash
python tools/migrar_banco.py
```

## Testes

A suite automatizada fica organizada por dominio em [tests](D:\Python\cspdv\tests:1).

Exemplos:

```bash
pytest tests/venda -q
pytest tests/financeiro -q
pytest tests/produtos -q
pytest -q
```

Estado atual validado:

- `100+` testes passando nas baterias principais de regressao usadas durante a estabilizacao

## Documentacao auxiliar

- [docs/architecture.md](D:\Python\cspdv\docs\architecture.md)
- [docs/tooling_commands.md](D:\Python\cspdv\docs\tooling_commands.md)
- [docs/homologacao/checklist_homologacao_operacional.xlsx](D:\Python\cspdv\docs\homologacao\checklist_homologacao_operacional.xlsx)

## Situacao atual do projeto

O sistema esta adequado para:

- operacao assistida
- piloto interno
- homologacao operacional estruturada
- evolucao incremental com base ja testada
- evolucao de schema com migrations versionadas

Ainda e recomendado validar o ambiente real de loja antes de producao plena, principalmente em:

- impressao operacional
- infraestrutura de banco
- dispositivos e perifericos
- rotina de backup
- eventual integracao fiscal futura

## Proximas frentes naturais

- relatorios
- lotes
- permissoes
- camada fiscal real
- refinamentos de UX e operacao
