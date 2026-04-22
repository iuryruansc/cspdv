# Arquitetura do Projeto

## Estrutura principal

```text
cspdv/
  core/
  database/
  modules/
    admin/
    auth/
    estoque/
    financeiro/
    fornecedores/
    produtos/
    relatorios/
    setup/
    shared/
  ui/
  utils/
  media/
  tests/
```

## Regras de responsabilidade

- `core/`: servicos transversais do sistema inteiro.
- `database/`: conexao e infraestrutura de persistencia.
- `modules/<dominio>/models/`: acesso ao banco daquele dominio.
- `modules/<dominio>/services/`: regras de negocio e orquestracao.
- `modules/<dominio>/views/`: telas e navegacao do dominio.
- `modules/shared/`: componentes reutilizaveis entre dominios.
- `ui/`: arquivos gerados pelo Qt Designer.
- `utils/`: helpers genericos sem regra de negocio.

## Convencao para novos recursos

Ao criar um novo recurso:

1. escolha o dominio correto dentro de `modules/`
2. coloque persistencia em `models/`
3. coloque regra de negocio em `services/`
4. deixe a `view` responsavel por interface e fluxo
5. reuse `core/`, `modules/shared/` e `utils/` somente quando fizer sentido
