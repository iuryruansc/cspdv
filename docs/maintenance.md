# Maintenance

## Objetivo

Consolidar a manutencao tecnica do banco em um fluxo unico.

Essa camada existe para facilitar:

- aplicacao de migrations
- aplicacao de seeds
- validacao de baseline estrutural
- validacao de dados-base essenciais

## Comando principal

```powershell
python tools/manutencao_banco.py
```

Sem parametros, ele executa:

1. migrations pendentes
2. seeds pendentes
3. validacao de baseline

## Modos disponiveis

### Apenas migrations

```powershell
python tools/manutencao_banco.py --migrate
```

### Apenas seeds

```powershell
python tools/manutencao_banco.py --seed
```

### Apenas validacao

```powershell
python tools/manutencao_banco.py --validate
```

## Validador de baseline

Arquivo:

- `database/maintenance/validator.py`

Ele valida:

- tabelas obrigatorias
- migrations pendentes
- seeds pendentes
- dados-base essenciais

## Tabelas verificadas atualmente

- `schema_migrations`
- `schema_seeds`
- `config_empresa`
- `clientes`
- `formas_pagamento`
- `unidades_medida`
- `caixa_motivos`
- `cargos`
- `perfis`
- `permissoes`
- `perfil_permissoes`

## Dados-base validados atualmente

- `Consumidor Final`
- cargo `Administrador`
- perfil `Admin Master`
- permissoes base
- formas de pagamento base
- unidades base
- motivos de caixa base

## Quando usar

Fluxos recomendados:

- apos atualizar branch ou release local
- antes de subir ambiente novo
- antes de homologacao
- em manutencao de suporte tecnico

## Resultado esperado

Quando tudo estiver consistente, a validacao retorna baseline sem pendencias.

Se houver problema, o comando aponta:

- tabela ausente
- migration pendente
- seed pendente
- dado-base ausente

## Relacao com a operacao

Essa manutencao e tecnica. Ela nao substitui:

- testes funcionais
- homologacao operacional
- conferencia manual de ambiente real
