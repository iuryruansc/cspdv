# Arquitetura do Projeto

## Estrutura principal

```text
cspdv/
  core/
  database/
  docs/
  modules/
    admin/
    auth/
    estoque/
    financeiro/
    fornecedores/
    produtos/
    promocoes/
    relatorios/
    setup/
    shared/
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
```

## Regras de responsabilidade

- `core/`: servicos transversais do sistema inteiro, como sessao e contexto operacional.
- `database/`: conexao e infraestrutura de persistencia.
- `docs/`: arquitetura, comandos de apoio e material de homologacao.
- `modules/<dominio>/models/`: acesso ao banco daquele dominio.
- `modules/<dominio>/services/`: regras de negocio e orquestracao.
- `modules/<dominio>/views/`: telas e navegacao do dominio.
- `modules/shared/`: componentes reutilizaveis entre dominios.
- `ui/`: arquivos gerados pelo Qt Designer.
- `utils/`: helpers genericos sem regra de negocio.
- `tests/<dominio>/`: testes automatizados agrupados por contexto funcional.

## Convencoes atuais

### Identidade de produto

- o campo `codigo` exibido no cadastro e na edicao de produto representa `cod_produto`
- `cod_produto` e `codigo_barras` podem ser usados na busca operacional de venda

### Shared e utils

Os helpers compartilhados devem ser preferidos antes de criar implementacoes locais repetidas. Hoje isso vale especialmente para:

- `utils/format_utils.py`
  - moeda
  - decimais
  - inteiros
  - data
  - data e hora
- `utils/table_widget_utils.py`
  - criacao e alinhamento de `QTableWidgetItem`
- `utils/combo_loader.py`
  - carregamento de combos
  - leitura segura de `currentData()`
- `utils/ui_messages.py`
  - mensagens padronizadas de aviso, confirmacao e informacao

### Camada de testes

- os testes ficam organizados por dominio funcional, acompanhando a estrutura de `modules/`
- novos testes de venda devem ir em `tests/venda/`
- novos testes de financeiro devem ir em `tests/financeiro/`
- helpers transversais devem ser testados em `tests/utils/` ou `tests/core/`
- a preferencia e por testes focados em servicos e views criticas, com baixo acoplamento a detalhes visuais desnecessarios

## Convencao para novos recursos

Ao criar um novo recurso:

1. escolha o dominio correto dentro de `modules/`
2. coloque persistencia em `models/`
3. coloque regra de negocio em `services/`
4. deixe a `view` responsavel por interface e fluxo
5. reuse `core/`, `modules/shared/` e `utils/` antes de duplicar implementacao
6. crie ou atualize testes no subdiretorio correspondente em `tests/`
7. se surgir uma duplicacao pequena e recorrente, prefira extrair helper compartilhado em vez de replicar codigo
