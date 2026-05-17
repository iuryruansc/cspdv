# Migrations

## Objetivo

As migrations governam a evolucao do schema do banco.

Elas existem para garantir que toda mudanca estrutural:

- seja versionada
- seja repetivel entre ambientes
- rode antes da operacao do sistema
- nao fique espalhada em `models/` via `ALTER TABLE` em runtime

## Regra principal

- mudou schema: criar migration
- mudou valor de configuracao ou dado de negocio: salvar normalmente via `services` e `models`

Exemplos de mudanca que exigem migration:

- criar tabela
- adicionar coluna
- alterar tipo de coluna
- adicionar `DEFAULT`
- adicionar `NOT NULL`
- adicionar ou revisar indice
- adicionar ou revisar `UNIQUE`
- adicionar ou revisar chave estrangeira
- ajustar `ON DELETE` / `ON UPDATE`

## Onde ficam

Arquivos:

- `database/migrations/runner.py`
- `database/migrations/versions/`

Tabela de controle:

- `schema_migrations`

## Quando rodam

As migrations pendentes rodam no startup da aplicacao por:

- `main.py`

Tambem podem ser executadas manualmente por:

```powershell
python tools/migrar_banco.py
```

## Convencao de nomes

Padrao:

```text
YYYYMMDD_NNN_descricao_curta.py
```

Exemplos:

- `20260517_001_config_empresa_defaults.py`
- `20260517_004_caixas_closing_columns.py`
- `20260517_007_referential_actions_history.py`

Boas praticas:

- uma migration por intencao estrutural clara
- nomes tecnicos curtos e objetivos
- evitar nomes vagos como `ajustes.py` ou `migration_nova.py`

## Estado atual coberto

A base atual ja tem migrations para:

- defaults e colunas de `config_empresa`
- colunas operacionais de fechamento de caixa
- timestamps de tabelas operacionais
- unicidades e indices principais
- integridade relacional central
- regras referenciais em historico operacional
- auditoria de eventos
- flags estruturais como `cliente_sistema`

## Fluxo recomendado para novos recursos

1. identificar a mudanca estrutural
2. criar a migration em `database/migrations/versions/`
3. validar localmente com:

```powershell
python tools/migrar_banco.py
```

4. so depois atualizar `models/`, `services/` e `views/`

## O que evitar

- `SHOW COLUMNS` como estrategia principal de funcionamento
- `ALTER TABLE` dentro de `models/`
- depender de tela ou fluxo operacional para "consertar" schema
