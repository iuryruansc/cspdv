**Fase 1 Técnica**
Migrações e integridade do banco

**Já implantado**
- Infraestrutura de migrations em [D:\Python\cspdv\database\migrations\runner.py](D:\Python\cspdv\database\migrations\runner.py:1)
- Tabela `schema_migrations`
- Primeira migration versionada para `config_empresa`
- Segunda migration versionada para integridade operacional:
  - unicidade de `pdvs.identificacao`
  - unicidade de `formas_pagamento.nome`
- Terceira migration versionada para baseline operacional:
  - timestamps padrão em `formas_pagamento`, `pdvs` e `unidades_medida`
  - índices em `caixas`, `caixa_movimentacoes` e unicidade em `caixa_motivos.tipo_padrao`
- Quarta migration versionada para fechamento de caixa:
  - `valor_fechamento`
  - `diferenca_fechamento`
  - `observacoes_fechamento`
- Quinta migration versionada para integridade relacional:
  - `vendas.usuario_id -> usuarios.id`
  - `caixas.usuario_fechamento_id -> usuarios.id`
  - índice de `caixas.usuario_fechamento_id`
- Sexta migration versionada para chaves operacionais:
  - unicidade de `pdvs.identificacao`
  - unicidade de `unidades_medida.sigla`
  - unicidade de `formas_pagamento.nome`
  - unicidade de `produtos.cod_produto`
  - unicidade de `produtos.codigo_barras`
- Sétima migration versionada para regras referenciais históricas:
  - `vendas.usuario_id -> usuarios.id` com `ON DELETE SET NULL`
  - `contas_receber.caixa_id -> caixas.id` com `ON DELETE SET NULL`
  - `venda_reembolsos.usuario_autorizador_id -> usuarios.id` com `ON DELETE SET NULL`
- Execução automática no startup em [D:\Python\cspdv\main.py](D:\Python\cspdv\main.py:1)
- Execução manual em [D:\Python\cspdv\tools\migrar_banco.py](D:\Python\cspdv\tools\migrar_banco.py:1)

**Pontos ainda com compatibilidade de schema em runtime**
- Não há mais pontos centrais de compatibilidade estrutural obrigatória nos fluxos revisados desta fase.
- O sistema agora assume schema governado por migrations nas áreas cobertas.

**Situação dos pontos antigos de compatibilidade**
- [D:\Python\cspdv\modules\setup\models\setup_model.py](D:\Python\cspdv\modules\setup\models\setup_model.py:1)
  - não depende mais de `SHOW COLUMNS` para `formas_pagamento`
- [D:\Python\cspdv\modules\venda\models\caixa_model.py](D:\Python\cspdv\modules\venda\models\caixa_model.py:1)
  - listagem admin e fechamento usam colunas padronizadas por migration
- [D:\Python\cspdv\modules\admin\models\dashboard_model.py](D:\Python\cspdv\modules\admin\models\dashboard_model.py:1)
  - não depende mais de `SHOW TABLES` / `SHOW COLUMNS`
  - passou a assumir o schema estabilizado pelas migrations

**Estado atual da fase**
1. Defaults estruturais: cobertos
2. Índices e unicidades operacionais: cobertos
3. Núcleo principal de chaves estrangeiras: coberto
4. Vínculos históricos com `SET NULL` onde faz sentido: cobertos
5. Compatibilidades estruturais remanescentes: encerradas para o escopo desta fase

**Status**
- Fase 1 concluída.

**Próximo passo recomendado**
1. Criar uma fase 2 técnica para:
   - seeds/versionamento de dados padrão
   - revisão de índices de busca e dashboard
   - auditoria estrutural complementar
