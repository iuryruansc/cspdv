# CSPdv

Sistema desktop de ponto de venda e operação administrativa desenvolvido em `Python + PyQt5`, com foco em operação de loja, caixa, financeiro, promoções e administração central.

## Visão geral

O projeto já cobre o fluxo principal de uma loja de pequeno e médio porte:

- setup inicial do sistema
- autenticação e seleção de módulo
- abertura e fechamento de caixa
- venda simples com cupom, descontos e pagamento
- venda rápida a partir do painel admin
- reembolso total e parcial
- contas a receber para vendas com pendência
- financeiro com movimentações, recebimentos e reembolsos
- estoque com consulta e ajuste
- promoções com vínculo de produtos

Hoje o sistema já está em um estágio utilizável para operação simples de balcão, com foco em:

- vendas à vista
- vendas com pagamento parcial
- recebimento posterior
- controle básico de estoque
- operação de caixa

## Stack

- `Python 3`
- `PyQt5`
- `MySQL`
- `python-dotenv`
- `bcrypt`

Dependências principais em [requirements.txt](D:\Python\cspdv\requirements.txt).

## Estrutura do projeto

```text
cspdv/
├── core/
├── database/
├── modules/
│   ├── admin/
│   ├── auth/
│   ├── categorias/
│   ├── clientes/
│   ├── estoque/
│   ├── financeiro/
│   ├── fornecedores/
│   ├── marcas/
│   ├── produtos/
│   ├── promocoes/
│   ├── relatorios/
│   ├── setup/
│   └── venda/
├── ui/
├── utils/
├── tests/
└── main.py
```

## Padrão de arquitetura

O projeto segue, de forma geral, esta separação:

- `modules/*/models`
  - acesso a dados e consultas
- `modules/*/services`
  - regras de negócio e orquestração
- `modules/*/views`
  - comportamento e integração das telas
- `ui/*`
  - layout visual das telas

O padrão atual prioriza:

- `ui/*.py` ou `ui/*.ui` cuidando do layout
- `views` focadas em comportamento
- lógica operacional concentrada em `services` e `models`

## Módulos atuais

### Auth

- login
- restauração de sessão
- seleção de modo no centro de operações

### Setup

- wizard de configuração inicial
- criação de registros-base
- criação das formas de pagamento padrão

### Admin

- dashboard administrativo
- ações rápidas
- gerenciamento central de cadastros
- venda rápida sem sair do painel
- card de status estrutural do sistema

### Venda

- frente de loja
- frente de venda
- consulta de produto
- seleção de cliente
- descontos
- confirmação de venda
- pagamento
- finalização com pendência
- pós-pagamento
- resumo do caixa atual

### Caixa

- abertura de caixa
- movimentação de caixa
- fechamento de caixa
- reforço de troco
- sangria e suprimento

### Financeiro

- movimentações de caixa
- vendas registradas
- contas a receber
- recebimento de pendências
- reembolsos registrados
- consulta de venda

### Estoque

- painel de estoque
- produtos e lotes
- últimas movimentações
- busca e filtros
- ajuste de quantidade

### Promoções

- painel de promoções e campanhas
- nova promoção
- edição
- duplicação
- encerramento
- cancelamento
- vínculo de produtos
- validação de conflito entre promoções sobrepostas

## Fluxos implementados

### Venda simples

1. abrir caixa
2. selecionar produtos
3. aplicar desconto, se necessário
4. confirmar venda
5. lançar pagamentos
6. concluir a venda
7. baixar estoque

### Venda com pendência

1. montar a venda normalmente
2. registrar pagamento parcial
3. finalizar com pendência
4. gerar conta a receber
5. receber o saldo depois no financeiro

### Reembolso

- reembolso total
- reembolso parcial
- devolução de estoque
- registro financeiro
- atualização de status da venda

### Promoções

- cadastro de promoção ou campanha
- regra por percentual, valor ou preço fixo
- vínculo de produtos
- prevenção de conflito com promoções ativas/agendadas no mesmo período

## Banco de dados

O projeto usa MySQL e depende de variáveis de ambiente carregadas via `.env`.

Além das tabelas-base do sistema, já existem estruturas específicas para:

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

## Como executar

### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

### 2. Configure o `.env`

Defina as credenciais e parâmetros de conexão do banco conforme o ambiente da loja.

Variáveis esperadas pelo projeto:

- `DB_HOST`
  - host do MySQL
  - exemplo: `127.0.0.1`
- `DB_PORT`
  - porta do MySQL
  - exemplo: `3306`
- `DB_USER`
  - usuário do banco
- `DB_PASSWORD`
  - senha do banco
- `DB_NAME`
  - nome do banco de dados
- `DB_CONNECTION_TIMEOUT`
  - timeout da conexão em segundos
  - exemplo: `5`
- `DB_USE_POOL`
  - habilita pool de conexões
  - valores aceitos na prática: `true`, `false`, `1`, `0`, `yes`, `on`
- `DB_POOL_NAME`
  - nome do pool de conexões
  - opcional
  - padrão usado pelo projeto: `cspdv_pool`
- `DB_POOL_SIZE`
  - quantidade de conexões no pool
  - exemplo: `10`

Variáveis auxiliares de identificação da aplicação:

- `APP_NAME`
- `APP_VERSION`

Exemplo de `.env`:

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

## Situação atual do projeto

O sistema está adequado para:

- piloto interno
- operação inicial de vendas simples
- testes operacionais de loja

Ainda é recomendado validar em homologação antes de produção plena, principalmente em:

- caixa
- promoções
- contas a receber
- reembolsos

Existe uma planilha de homologação no projeto:

- [checklist_homologacao_operacional.xlsx](D:\Python\cspdv\docs\homologacao\checklist_homologacao_operacional.xlsx)

## Próximas implementações sugeridas

### Curto prazo

- persistência real da área de configurações do admin
- melhoria da auditoria operacional
- mais refinamento visual e de usabilidade no financeiro
- histórico mais rico de contas a receber
- relatórios operacionais básicos

### Médio prazo

- destaque visual de preços promocionais na venda
- gestão mais completa de campanhas por categoria, marca e PDV
- mais regras de configuração de caixa e venda
- melhoria da área fiscal
- consolidação de logs administrativos

### Longo prazo

- impressão completa de documentos operacionais
- relatórios gerenciais
- regras avançadas de cumulatividade promocional
- dashboards mais analíticos
- possíveis integrações externas

## Pontos de atenção

- a área de `Relatórios` ainda não está no mesmo nível de maturidade dos módulos principais
- parte das funcionalidades fiscais ainda depende de evolução futura
- a política de promoções cumulativas ainda não está ativa no PDV
- o sistema foi estruturado para evolução incremental, então alguns módulos ainda estão em fase de consolidação funcional

## Objetivo do projeto

O objetivo do `CSPdv` é oferecer uma base sólida para:

- frente de caixa
- operação administrativa
- controle financeiro da loja
- campanhas promocionais
- evolução futura para um ERP/POS mais completo
