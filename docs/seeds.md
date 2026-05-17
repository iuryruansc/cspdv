# Seeds

## Objetivo

Seeds versionam os dados-base do sistema.

Eles servem para garantir que registros estruturais e previsiveis existam de forma:

- repetivel
- idempotente
- consistente entre ambientes

## Regra principal

Seed e indicado para dados que:

- sempre devem existir
- nao dependem da empresa do cliente
- nao deveriam nascer soltos no setup

## Onde ficam

Arquivos:

- `database/seeds/runner.py`
- `database/seeds/versions/`

Tabela de controle:

- `schema_seeds`

## Quando rodam

Os seeds pendentes rodam no startup, logo depois das migrations.

Tambem podem ser executados manualmente por:

```powershell
python tools/seed_banco.py
```

## Dados-base atuais

Hoje os seeds versionados cobrem:

- formas de pagamento padrao
- unidades padrao
- motivos padrao de caixa
- cargo `Administrador`
- perfil `Admin Master`
- permissoes base
- vinculos `perfil_permissoes`
- cliente sistema `Consumidor Final`

## Relacao com o setup

O `setup` continua responsavel por dados da instalacao, como:

- empresa
- PDV inicial
- usuario administrador inicial

Ja os dados-base do sistema devem preferencialmente vir por seed.

## Convencao de nomes

Padrao:

```text
YYYYMMDD_NNN_descricao_curta.py
```

Exemplos:

- `20260517_001_operational_master_data.py`
- `20260517_002_access_master_data.py`
- `20260517_003_consumidor_final_client.py`

## Boas praticas

- seed deve ser idempotente
- seed nao deve duplicar registro ao rodar duas vezes
- dados-base protegidos devem ser identificaveis claramente

## Exemplo importante

`Consumidor Final` hoje existe como cliente real seeded e protegido por `cliente_sistema = 'S'`.

Isso permite:

- venda com `cliente_id` real por padrao
- consistencia melhor em financeiro e reembolso
- protecao contra edicao/desativacao indevida no admin

## O que evitar

- criar dados-base criticos espalhados em `setup_model`
- depender de cadastro manual para registros estruturais do sistema
