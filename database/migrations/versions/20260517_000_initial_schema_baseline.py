from __future__ import annotations

from database.migrations.runner import CursorLike

VERSION = "20260517_000"
DESCRIPTION = "Cria a baseline inicial completa do schema para bancos vazios"

TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS `cargos` (
      `id` int NOT NULL AUTO_INCREMENT,
      `nome_cargo` varchar(100) DEFAULT NULL,
      `createdAt` datetime DEFAULT NULL,
      `updatedAt` datetime DEFAULT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      `cbo` varchar(10) DEFAULT NULL,
      `salario_base` decimal(15,2) DEFAULT '0.00',
      `percent_comissao_venda` decimal(15,2) DEFAULT '0.00',
      `departamento_id` int DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='cbo = classificação brasileira de cupações'
    """,
    """
    CREATE TABLE IF NOT EXISTS `perfis` (
      `id` int NOT NULL AUTO_INCREMENT,
      `nome` varchar(50) NOT NULL,
      `descricao` varchar(255) DEFAULT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      `criatedAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updateAt` datetime NOT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `nome` (`nome`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `permissoes` (
      `id` int NOT NULL AUTO_INCREMENT,
      `chave` varchar(100) NOT NULL,
      `nome_amigavel` varchar(100) DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `chave` (`chave`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `funcionarios` (
      `id` int NOT NULL AUTO_INCREMENT,
      `nome` varchar(255) NOT NULL,
      `cpf` varchar(255) NOT NULL,
      `cargo_id` int NOT NULL,
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      `ativo` enum('S','N') DEFAULT 'S',
      `data_admissao` date DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `nome` (`nome`),
      UNIQUE KEY `cpf` (`cpf`),
      KEY `id_cargo` (`cargo_id`),
      CONSTRAINT `funcionarios_ibfk_1` FOREIGN KEY (`cargo_id`) REFERENCES `cargos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `usuarios` (
      `id` int NOT NULL AUTO_INCREMENT,
      `funcionario_id` int DEFAULT NULL,
      `nome` varchar(255) NOT NULL,
      `email` varchar(255) DEFAULT NULL,
      `senha` varchar(255) NOT NULL,
      `cargo` varchar(255) DEFAULT NULL,
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      `perfil_acesso_id` int DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `nome` (`nome`),
      UNIQUE KEY `email` (`email`),
      KEY `fk_funcionario` (`funcionario_id`),
      KEY `fk_perfis_acesso_idx` (`perfil_acesso_id`),
      CONSTRAINT `fk_funcionario` FOREIGN KEY (`funcionario_id`) REFERENCES `funcionarios` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
      CONSTRAINT `fk_perfis_acesso` FOREIGN KEY (`perfil_acesso_id`) REFERENCES `perfis` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `perfil_permissoes` (
      `perfil_id` int NOT NULL,
      `permissao_id` int NOT NULL,
      PRIMARY KEY (`perfil_id`,`permissao_id`),
      KEY `permissao_id` (`permissao_id`),
      CONSTRAINT `perfil_permissoes_ibfk_1` FOREIGN KEY (`perfil_id`) REFERENCES `perfis` (`id`),
      CONSTRAINT `perfil_permissoes_ibfk_2` FOREIGN KEY (`permissao_id`) REFERENCES `permissoes` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `pdvs` (
      `id` int NOT NULL AUTO_INCREMENT,
      `identificacao` varchar(255) NOT NULL,
      `descricao` varchar(255) NOT NULL,
      `status` enum('ativo','inativo') NOT NULL,
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      PRIMARY KEY (`id`),
      UNIQUE KEY `uniq_pdvs_identificacao` (`identificacao`),
      KEY `idx_pdvs_ativo_status_identificacao` (`ativo`,`status`,`identificacao`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `formas_pagamento` (
      `id` int NOT NULL AUTO_INCREMENT,
      `nome` varchar(50) NOT NULL,
      `tipo_sefaz` varchar(2) NOT NULL,
      `permite_parcelamento` enum('S','N') DEFAULT 'S',
      `taxa_administrativa` decimal(5,2) DEFAULT '0.00',
      `ativo` enum('S','N') DEFAULT 'S',
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `uniq_formas_pagamento_nome` (`nome`),
      KEY `idx_formas_pagamento_ativo_nome` (`ativo`,`nome`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `caixa_motivos` (
      `id` int unsigned NOT NULL AUTO_INCREMENT,
      `descricao` varchar(50) NOT NULL,
      `tipo_padrao` varchar(15) NOT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `id_caixa_motivo` (`id`),
      UNIQUE KEY `uniq_caixa_motivos_tipo_padrao` (`tipo_padrao`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='O tipo_padrão é Sangria ou Suprimento'
    """,
    """
    CREATE TABLE IF NOT EXISTS `categorias` (
      `id` int NOT NULL AUTO_INCREMENT,
      `nome` varchar(255) NOT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      `usuario_cadastro_id` int DEFAULT NULL,
      `createdAt` datetime DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      KEY `idx_categorias_ativo_nome` (`ativo`,`nome`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `marcas` (
      `id` int NOT NULL AUTO_INCREMENT,
      `nome_marca` varchar(255) NOT NULL,
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      `ativo` enum('S','N') DEFAULT 'S',
      PRIMARY KEY (`id`),
      KEY `idx_marcas_ativo_nome_marca` (`ativo`,`nome_marca`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `fornecedores` (
      `id_fornecedor` int NOT NULL AUTO_INCREMENT,
      `nome_fantasia` varchar(255) NOT NULL,
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      `razao_social` varchar(255) DEFAULT NULL,
      `cnpj_cpf` varchar(18) DEFAULT NULL,
      `ie` varchar(15) DEFAULT NULL,
      `logradouro` varchar(255) DEFAULT NULL,
      `numero` varchar(15) DEFAULT NULL,
      `bairro` varchar(45) DEFAULT NULL,
      `cep` varchar(8) DEFAULT NULL,
      `cidade` varchar(45) DEFAULT NULL,
      `estado` varchar(2) DEFAULT NULL,
      `telefone` varchar(45) DEFAULT NULL,
      `email` varchar(200) DEFAULT NULL,
      `usuario_cadastro_id` int DEFAULT NULL,
      `observacao` longtext,
      `ativo` enum('S','N') DEFAULT 'S',
      PRIMARY KEY (`id_fornecedor`),
      KEY `idx_fornecedores_ativo_nome_fantasia` (`ativo`,`nome_fantasia`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `unidades_medida` (
      `id` bigint unsigned NOT NULL AUTO_INCREMENT,
      `sigla` varchar(6) NOT NULL,
      `descricao` varchar(50) NOT NULL,
      `codigo_sefaz` varchar(6) DEFAULT NULL,
      `fracionável` tinyint(1) DEFAULT '0',
      `ativo` enum('S','N') DEFAULT 'S',
      `data_criacao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `id` (`id`),
      UNIQUE KEY `sigla` (`sigla`),
      KEY `idx_unidades_medida_ativo_sigla` (`ativo`,`sigla`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `clientes` (
      `id` int NOT NULL AUTO_INCREMENT,
      `nome` varchar(255) NOT NULL,
      `email` varchar(255) DEFAULT NULL,
      `telefone` varchar(255) NOT NULL,
      `cpf` varchar(255) DEFAULT NULL,
      `logradouro` varchar(50) DEFAULT NULL,
      `numero` int DEFAULT NULL,
      `bairro` varchar(45) DEFAULT NULL,
      `cep` varchar(8) DEFAULT NULL,
      `cidade` varchar(45) DEFAULT NULL,
      `estado` varchar(45) DEFAULT NULL,
      `observacao` longtext,
      `cliente_sistema` char(1) NOT NULL DEFAULT 'N',
      `ativo` enum('S','N') DEFAULT 'S',
      `createdAt` datetime DEFAULT NULL,
      `updatedAt` datetime DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `email` (`email`),
      UNIQUE KEY `cpf` (`cpf`),
      KEY `idx_clientes_ativo_sistema_nome` (`ativo`,`cliente_sistema`,`nome`),
      KEY `idx_clientes_ativo_sistema_cpf` (`ativo`,`cliente_sistema`,`cpf`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `config_empresa` (
      `id` int NOT NULL AUTO_INCREMENT,
      `razao_social` varchar(255) NOT NULL,
      `nome_fantasia` varchar(255) DEFAULT NULL,
      `cnpj` varchar(14) NOT NULL,
      `inscricao_estadual` varchar(20) DEFAULT NULL,
      `email` varchar(100) DEFAULT NULL,
      `telefone` varchar(20) DEFAULT NULL,
      `logotipo_path` varchar(255) DEFAULT NULL,
      `logradouro` varchar(255) DEFAULT NULL,
      `numero` varchar(10) DEFAULT NULL,
      `bairro` varchar(100) DEFAULT NULL,
      `cidade` varchar(100) DEFAULT NULL,
      `estado` char(2) DEFAULT NULL,
      `cep` varchar(8) DEFAULT NULL,
      `regime_tributario` varchar(50) DEFAULT NULL,
      `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      `pdv_padrao_id` int DEFAULT NULL,
      `moeda_padrao` varchar(10) DEFAULT 'BRL',
      `cliente_padrao_venda` varchar(40) DEFAULT 'CONSUMIDOR_FINAL',
      `regra_desconto_venda` varchar(40) DEFAULT 'PERMITIR_DESCONTO',
      `habilitar_venda_rapida_admin` char(1) DEFAULT 'S',
      `permitir_venda_sem_estoque` char(1) DEFAULT 'N',
      `fundo_inicial_sugerido` decimal(10,2) DEFAULT '0.00',
      `exigir_admin_sangria` char(1) DEFAULT 'S',
      `exigir_admin_reembolso` char(1) DEFAULT 'S',
      `exigir_admin_diferenca_fechamento` char(1) DEFAULT 'S',
      `prioridade_promocional` varchar(50) DEFAULT 'PROMOCAO_ANTES_DESCONTO',
      `bloquear_promocoes_simultaneas` char(1) DEFAULT 'S',
      `ativar_promocoes_por_vigencia` char(1) DEFAULT 'S',
      `horas_sessao_persistida` int DEFAULT '12',
      `restaurar_login_automaticamente` char(1) DEFAULT 'S',
      `bloquear_fechamento_programa_caixa_aberto` char(1) DEFAULT 'S',
      `intervalo_backup_horas` int DEFAULT '24',
      `perfil_log` varchar(30) DEFAULT 'OPERACIONAL',
      `versao_referencia` varchar(60) DEFAULT 'CSPdv v1.0.0',
      `regime_tributario_padrao` varchar(40) DEFAULT 'SIMPLES_NACIONAL',
      `origem_mercadoria_padrao` varchar(5) DEFAULT '0',
      `cfop_venda_padrao` varchar(10) DEFAULT '5102',
      `cfop_devolucao_padrao` varchar(10) DEFAULT '1202',
      `csosn_cst_padrao` varchar(10) DEFAULT '102',
      `natureza_operacao_padrao` varchar(120) DEFAULT 'VENDA DE MERCADORIA',
      `exigir_ncm_cest_produto` char(1) DEFAULT 'S',
      `exigir_unidade_tributavel_produto` char(1) DEFAULT 'S',
      PRIMARY KEY (`id`),
      UNIQUE KEY `cnpj` (`cnpj`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `produtos` (
      `id` int NOT NULL AUTO_INCREMENT,
      `nome` varchar(255) NOT NULL,
      `preco_compra` float DEFAULT NULL,
      `preco_venda` float NOT NULL,
      `quantidade_estoque` int DEFAULT '0',
      `categoria_id` int NOT NULL,
      `fornecedor_id` int NOT NULL,
      `marca_id` int NOT NULL,
      `codigo_barras` varchar(255) NOT NULL,
      `createdAt` datetime DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      `ncm` varchar(8) DEFAULT NULL,
      `cest` varchar(7) DEFAULT NULL,
      `unidade_id` int DEFAULT NULL,
      `unidade_tributavel_id` int DEFAULT NULL,
      `cod_produto` varchar(7) DEFAULT NULL,
      `ativo` enum('S','N') NOT NULL DEFAULT 'S',
      `imagem_path` varchar(255) DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `codigo_barras` (`codigo_barras`),
      UNIQUE KEY `cod_produto_UNIQUE` (`cod_produto`),
      KEY `idx_produtos_ativo_nome` (`ativo`,`nome`),
      KEY `idx_produtos_ativo_categoria_fornecedor_nome` (`ativo`,`categoria_id`,`fornecedor_id`,`nome`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='cest =  Código Especificador da Substituição Tributária    e      ncm = nomeclatura comum do mercosul'
    """,
    """
    CREATE TABLE IF NOT EXISTS `lotes` (
      `id` int NOT NULL AUTO_INCREMENT,
      `produto_id` int NOT NULL,
      `preco_compra` float NOT NULL,
      `preco_venda` float NOT NULL,
      `numero_lote` varchar(255) NOT NULL,
      `quantidade` int DEFAULT NULL,
      `data_validade` date NOT NULL,
      `localizacao` varchar(255) DEFAULT NULL,
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      PRIMARY KEY (`id`),
      KEY `idx_lotes_produto_ativo_validade_numero` (`produto_id`,`ativo`,`data_validade`,`numero_lote`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `caixas` (
      `id` int NOT NULL AUTO_INCREMENT,
      `pdv_id` int NOT NULL,
      `usuario_abertura_id` int NOT NULL,
      `data_abertura` datetime DEFAULT NULL,
      `data_fechamento` datetime DEFAULT NULL,
      `valor_abertura` decimal(10,2) DEFAULT NULL,
      `valor_fechamento_sistema` decimal(10,2) DEFAULT NULL,
      `status` enum('aberto','fechado') NOT NULL,
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      `usuario_fechamento_id` int NOT NULL,
      `valor_fechamento_informado` decimal(12,2) DEFAULT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      `valor_fechamento` decimal(12,2) DEFAULT NULL,
      `diferenca_fechamento` decimal(12,2) DEFAULT NULL,
      `observacoes_fechamento` text,
      PRIMARY KEY (`id`),
      KEY `fk_pdv_idx` (`pdv_id`),
      KEY `fk_usuario_abertura_idx` (`usuario_abertura_id`),
      KEY `idx_caixas_pdv_status_ativo` (`pdv_id`,`status`,`ativo`),
      KEY `idx_caixas_usuario_status_ativo` (`usuario_abertura_id`,`status`,`ativo`),
      KEY `idx_caixas_usuario_fechamento` (`usuario_fechamento_id`),
      CONSTRAINT `fk_caixas_usuario_fechamento` FOREIGN KEY (`usuario_fechamento_id`) REFERENCES `usuarios` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
      CONSTRAINT `fk_pdv` FOREIGN KEY (`pdv_id`) REFERENCES `pdvs` (`id`),
      CONSTRAINT `fk_usuario_abertura` FOREIGN KEY (`usuario_abertura_id`) REFERENCES `usuarios` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `caixa_movimentacoes` (
      `id` int unsigned NOT NULL AUTO_INCREMENT,
      `caixa_id` int NOT NULL,
      `usuario_id` int NOT NULL,
      `caixa_motivo_id` int DEFAULT NULL,
      `valor` decimal(15,2) NOT NULL,
      `data_hora` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
      `forma_pagamento_id` int NOT NULL,
      `observacao` text,
      `estornado` tinyint(1) DEFAULT '0',
      `movimentacao_estorno_id` int DEFAULT NULL,
      `createdAt` datetime DEFAULT NULL,
      `updatedAt` datetime DEFAULT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      PRIMARY KEY (`id`),
      UNIQUE KEY `id_caixa_mov` (`id`),
      KEY `fk_caixa_idx` (`caixa_id`),
      KEY `fk_usuario_idx` (`usuario_id`),
      KEY `idx_caixa_mov_caixa_ativo_estorno_data` (`caixa_id`,`ativo`,`estornado`,`data_hora`),
      CONSTRAINT `fk_caixa` FOREIGN KEY (`caixa_id`) REFERENCES `caixas` (`id`),
      CONSTRAINT `fk_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `vendas` (
      `id` int NOT NULL AUTO_INCREMENT,
      `data_hora` datetime DEFAULT NULL,
      `cliente_id` int DEFAULT NULL,
      `usuario_id` int DEFAULT NULL,
      `caixa_id` int DEFAULT NULL,
      `valor_total` decimal(10,2) NOT NULL,
      `status` varchar(255) NOT NULL DEFAULT 'PENDENTE',
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      PRIMARY KEY (`id`),
      KEY `id_cliente` (`cliente_id`),
      KEY `id_funcionario` (`usuario_id`),
      KEY `id_caixa` (`caixa_id`),
      KEY `idx_vendas_status_data_hora` (`status`,`data_hora`),
      CONSTRAINT `fk_vendas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
      CONSTRAINT `vendas_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
      CONSTRAINT `vendas_ibfk_3` FOREIGN KEY (`caixa_id`) REFERENCES `caixas` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `itens_venda` (
      `id` int NOT NULL AUTO_INCREMENT,
      `venda_id` int NOT NULL,
      `lote_id` int NOT NULL,
      `produto_id` int NOT NULL,
      `quantidade` int NOT NULL,
      `preco_unitario` decimal(10,2) NOT NULL,
      PRIMARY KEY (`id`),
      KEY `id_venda` (`venda_id`),
      KEY `id_produto` (`produto_id`),
      CONSTRAINT `itens_venda_ibfk_1` FOREIGN KEY (`venda_id`) REFERENCES `vendas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
      CONSTRAINT `itens_venda_ibfk_2` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `movimentacao_estoque` (
      `id` int NOT NULL AUTO_INCREMENT,
      `lote_id` int NOT NULL,
      `venda_id` int DEFAULT NULL,
      `data_hora` datetime NOT NULL,
      `tipo` varchar(255) NOT NULL,
      `quantidade` int NOT NULL,
      `usuario_id` int DEFAULT NULL,
      `observacao` text,
      `tipo_movimento_id` int DEFAULT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      PRIMARY KEY (`id`),
      KEY `id_lote` (`lote_id`),
      KEY `id_venda` (`venda_id`),
      KEY `id_funcionario` (`usuario_id`),
      KEY `idx_movimentacao_estoque_ativo_data_lote` (`ativo`,`data_hora`,`lote_id`),
      CONSTRAINT `movimentacao_estoque_ibfk_1` FOREIGN KEY (`lote_id`) REFERENCES `lotes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
      CONSTRAINT `movimentacao_estoque_ibfk_2` FOREIGN KEY (`venda_id`) REFERENCES `vendas` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
      CONSTRAINT `movimentacao_estoque_ibfk_3` FOREIGN KEY (`usuario_id`) REFERENCES `funcionarios` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `pagamento_parcial` (
      `id` int NOT NULL AUTO_INCREMENT,
      `venda_id` int NOT NULL,
      `data_pagamento` datetime NOT NULL,
      `valor_pago` decimal(10,2) NOT NULL,
      `forma_pagamento` varchar(255) NOT NULL,
      `observacao` varchar(255) DEFAULT NULL,
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      PRIMARY KEY (`id`),
      KEY `id_venda` (`venda_id`),
      KEY `idx_pagamento_parcial_data_forma_venda` (`data_pagamento`,`forma_pagamento`,`venda_id`),
      CONSTRAINT `pagamento_parcial_ibfk_1` FOREIGN KEY (`venda_id`) REFERENCES `vendas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `contas_receber` (
      `id` int NOT NULL AUTO_INCREMENT,
      `venda_id` int NOT NULL,
      `cliente_id` int NOT NULL,
      `usuario_id` int NOT NULL,
      `caixa_id` int DEFAULT NULL,
      `descricao` varchar(255) NOT NULL,
      `observacao` text,
      `valor_total` decimal(10,2) NOT NULL DEFAULT '0.00',
      `valor_recebido` decimal(10,2) NOT NULL DEFAULT '0.00',
      `valor_aberto` decimal(10,2) NOT NULL DEFAULT '0.00',
      `data_emissao` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `data_vencimento` date NOT NULL,
      `status` varchar(30) NOT NULL DEFAULT 'PENDENTE',
      `ativo` char(1) NOT NULL DEFAULT 'S',
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      KEY `idx_contas_receber_venda_id` (`venda_id`),
      KEY `idx_contas_receber_cliente_id` (`cliente_id`),
      KEY `idx_contas_receber_usuario_id` (`usuario_id`),
      KEY `idx_contas_receber_caixa_id` (`caixa_id`),
      KEY `idx_contas_receber_status` (`status`),
      KEY `idx_contas_receber_vencimento` (`data_vencimento`),
      KEY `idx_contas_receber_ativo_status_vencimento_caixa` (`ativo`,`status`,`data_vencimento`,`caixa_id`),
      CONSTRAINT `fk_contas_receber_caixa` FOREIGN KEY (`caixa_id`) REFERENCES `caixas` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
      CONSTRAINT `fk_contas_receber_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`),
      CONSTRAINT `fk_contas_receber_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
      CONSTRAINT `fk_contas_receber_venda` FOREIGN KEY (`venda_id`) REFERENCES `vendas` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `contas_receber_recebimentos` (
      `id` int NOT NULL AUTO_INCREMENT,
      `conta_receber_id` int NOT NULL,
      `usuario_id` int NOT NULL,
      `caixa_id` int DEFAULT NULL,
      `forma_pagamento_id` int DEFAULT NULL,
      `valor_recebido` decimal(10,2) NOT NULL DEFAULT '0.00',
      `data_recebimento` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `observacao` varchar(255) DEFAULT NULL,
      `ativo` char(1) NOT NULL DEFAULT 'S',
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      KEY `idx_contas_receber_recebimentos_conta_id` (`conta_receber_id`),
      KEY `idx_contas_receber_recebimentos_usuario_id` (`usuario_id`),
      KEY `idx_contas_receber_recebimentos_caixa_id` (`caixa_id`),
      KEY `idx_contas_receber_recebimentos_forma_id` (`forma_pagamento_id`),
      KEY `idx_contas_receber_recebimentos_data` (`data_recebimento`),
      KEY `idx_crr_ativo_data_conta` (`ativo`,`data_recebimento`,`conta_receber_id`),
      CONSTRAINT `fk_contas_receber_recebimentos_caixa` FOREIGN KEY (`caixa_id`) REFERENCES `caixas` (`id`),
      CONSTRAINT `fk_contas_receber_recebimentos_conta` FOREIGN KEY (`conta_receber_id`) REFERENCES `contas_receber` (`id`),
      CONSTRAINT `fk_contas_receber_recebimentos_forma` FOREIGN KEY (`forma_pagamento_id`) REFERENCES `formas_pagamento` (`id`),
      CONSTRAINT `fk_contas_receber_recebimentos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `promocoes` (
      `id` int NOT NULL AUTO_INCREMENT,
      `codigo` varchar(30) NOT NULL,
      `nome` varchar(150) NOT NULL,
      `classificacao` varchar(20) NOT NULL DEFAULT 'PROMOCAO',
      `tipo_desconto` varchar(30) NOT NULL,
      `status` varchar(20) NOT NULL DEFAULT 'RASCUNHO',
      `descricao` varchar(255) DEFAULT NULL,
      `observacao` text,
      `desconto_percentual` decimal(10,2) NOT NULL DEFAULT '0.00',
      `desconto_valor` decimal(10,2) NOT NULL DEFAULT '0.00',
      `preco_fixo` decimal(10,2) NOT NULL DEFAULT '0.00',
      `data_inicio` datetime NOT NULL,
      `data_fim` datetime NOT NULL,
      `cumulativa` char(1) NOT NULL DEFAULT 'N',
      `aplica_em_todos_pdvs` char(1) NOT NULL DEFAULT 'S',
      `ativo` char(1) NOT NULL DEFAULT 'S',
      `usuario_id` int NOT NULL,
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `uk_promocoes_codigo` (`codigo`),
      KEY `idx_promocoes_status` (`status`),
      KEY `idx_promocoes_periodo` (`data_inicio`,`data_fim`),
      KEY `idx_promocoes_usuario` (`usuario_id`),
      KEY `idx_promocoes_ativo_status_data_fim` (`ativo`,`status`,`data_fim`),
      CONSTRAINT `fk_promocoes_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `promocao_produtos` (
      `id` int NOT NULL AUTO_INCREMENT,
      `promocao_id` int NOT NULL,
      `produto_id` int NOT NULL,
      `preco_original` decimal(10,2) NOT NULL DEFAULT '0.00',
      `preco_promocional` decimal(10,2) NOT NULL DEFAULT '0.00',
      `desconto_aplicado` decimal(10,2) NOT NULL DEFAULT '0.00',
      `observacao` varchar(255) DEFAULT NULL,
      `ativo` char(1) NOT NULL DEFAULT 'S',
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `uk_promocao_produto` (`promocao_id`,`produto_id`),
      KEY `idx_promocao_produtos_produto` (`produto_id`),
      KEY `idx_promocao_produtos_produto_ativo_promocao` (`produto_id`,`ativo`,`promocao_id`),
      KEY `idx_promocao_produtos_promocao_ativo_produto` (`promocao_id`,`ativo`,`produto_id`),
      CONSTRAINT `fk_promocao_produtos_produto` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`),
      CONSTRAINT `fk_promocao_produtos_promocao` FOREIGN KEY (`promocao_id`) REFERENCES `promocoes` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `promocao_categorias` (
      `id` int NOT NULL AUTO_INCREMENT,
      `promocao_id` int NOT NULL,
      `categoria_id` int NOT NULL,
      `ativo` char(1) NOT NULL DEFAULT 'S',
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `uk_promocao_categoria` (`promocao_id`,`categoria_id`),
      KEY `idx_promocao_categorias_categoria` (`categoria_id`),
      CONSTRAINT `fk_promocao_categorias_categoria` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`),
      CONSTRAINT `fk_promocao_categorias_promocao` FOREIGN KEY (`promocao_id`) REFERENCES `promocoes` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `promocao_marcas` (
      `id` int NOT NULL AUTO_INCREMENT,
      `promocao_id` int NOT NULL,
      `marca_id` int NOT NULL,
      `ativo` char(1) NOT NULL DEFAULT 'S',
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `uk_promocao_marca` (`promocao_id`,`marca_id`),
      KEY `idx_promocao_marcas_marca` (`marca_id`),
      CONSTRAINT `fk_promocao_marcas_marca` FOREIGN KEY (`marca_id`) REFERENCES `marcas` (`id`),
      CONSTRAINT `fk_promocao_marcas_promocao` FOREIGN KEY (`promocao_id`) REFERENCES `promocoes` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `promocao_pdvs` (
      `id` int NOT NULL AUTO_INCREMENT,
      `promocao_id` int NOT NULL,
      `pdv_id` int NOT NULL,
      `ativo` char(1) NOT NULL DEFAULT 'S',
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `uk_promocao_pdv` (`promocao_id`,`pdv_id`),
      KEY `idx_promocao_pdvs_pdv` (`pdv_id`),
      CONSTRAINT `fk_promocao_pdvs_pdv` FOREIGN KEY (`pdv_id`) REFERENCES `pdvs` (`id`),
      CONSTRAINT `fk_promocao_pdvs_promocao` FOREIGN KEY (`promocao_id`) REFERENCES `promocoes` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `venda_reembolsos` (
      `id` int NOT NULL AUTO_INCREMENT,
      `venda_id` int NOT NULL,
      `tipo` varchar(20) NOT NULL,
      `status` varchar(20) NOT NULL DEFAULT 'CONCLUIDO',
      `valor_total` decimal(10,2) NOT NULL DEFAULT '0.00',
      `motivo` varchar(255) NOT NULL,
      `observacao` text,
      `usuario_id` int NOT NULL,
      `usuario_autorizador_id` int DEFAULT NULL,
      `data_hora` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `ativo` char(1) NOT NULL DEFAULT 'S',
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      KEY `idx_venda_reembolsos_venda_id` (`venda_id`),
      KEY `idx_venda_reembolsos_usuario_id` (`usuario_id`),
      KEY `idx_venda_reembolsos_usuario_aut_id` (`usuario_autorizador_id`),
      KEY `idx_venda_reembolsos_data_hora` (`data_hora`),
      KEY `idx_venda_reembolsos_ativo_status_data_venda` (`ativo`,`status`,`data_hora`,`venda_id`),
      CONSTRAINT `fk_venda_reembolsos_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
      CONSTRAINT `fk_venda_reembolsos_usuario_aut` FOREIGN KEY (`usuario_autorizador_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
      CONSTRAINT `fk_venda_reembolsos_venda` FOREIGN KEY (`venda_id`) REFERENCES `vendas` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `venda_reembolso_itens` (
      `id` int NOT NULL AUTO_INCREMENT,
      `reembolso_id` int NOT NULL,
      `item_venda_id` int NOT NULL,
      `produto_id` int NOT NULL,
      `lote_id` int DEFAULT NULL,
      `quantidade` int NOT NULL,
      `valor_unitario` decimal(10,2) NOT NULL DEFAULT '0.00',
      `valor_total` decimal(10,2) NOT NULL DEFAULT '0.00',
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      KEY `idx_venda_reembolso_itens_reembolso_id` (`reembolso_id`),
      KEY `idx_venda_reembolso_itens_item_venda_id` (`item_venda_id`),
      KEY `idx_venda_reembolso_itens_produto_id` (`produto_id`),
      KEY `idx_venda_reembolso_itens_lote_id` (`lote_id`),
      CONSTRAINT `fk_venda_reembolso_itens_item_venda` FOREIGN KEY (`item_venda_id`) REFERENCES `itens_venda` (`id`),
      CONSTRAINT `fk_venda_reembolso_itens_lote` FOREIGN KEY (`lote_id`) REFERENCES `lotes` (`id`),
      CONSTRAINT `fk_venda_reembolso_itens_produto` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`),
      CONSTRAINT `fk_venda_reembolso_itens_reembolso` FOREIGN KEY (`reembolso_id`) REFERENCES `venda_reembolsos` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `venda_reembolso_pagamentos` (
      `id` int NOT NULL AUTO_INCREMENT,
      `reembolso_id` int NOT NULL,
      `forma_pagamento` varchar(100) NOT NULL,
      `valor` decimal(10,2) NOT NULL DEFAULT '0.00',
      `observacao` varchar(255) DEFAULT NULL,
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      KEY `idx_venda_reembolso_pagamentos_reembolso_id` (`reembolso_id`),
      KEY `idx_venda_reembolso_pagamentos_forma` (`forma_pagamento`),
      CONSTRAINT `fk_venda_reembolso_pagamentos_reembolso` FOREIGN KEY (`reembolso_id`) REFERENCES `venda_reembolsos` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `auditoria_eventos` (
      `id` bigint NOT NULL AUTO_INCREMENT,
      `evento` varchar(80) NOT NULL,
      `categoria` varchar(80) NOT NULL,
      `entidade` varchar(80) DEFAULT NULL,
      `entidade_id` int DEFAULT NULL,
      `usuario_id` int DEFAULT NULL,
      `caixa_id` int DEFAULT NULL,
      `detalhes_json` longtext,
      `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      KEY `idx_auditoria_categoria_data` (`categoria`,`createdAt`),
      KEY `idx_auditoria_usuario_data` (`usuario_id`,`createdAt`),
      KEY `idx_auditoria_caixa_data` (`caixa_id`,`createdAt`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `schema_seeds` (
      `version` varchar(64) NOT NULL,
      `description` varchar(255) NOT NULL,
      `applied_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY (`version`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `descontos` (
      `id` int NOT NULL AUTO_INCREMENT,
      `lote_id` int NOT NULL,
      `tipo` enum('porcentagem','valor_fixo') NOT NULL,
      `valor` decimal(10,2) NOT NULL,
      `data_inicio` datetime NOT NULL,
      `data_fim` datetime NOT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      `observacao` text,
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `estoque_ajustes` (
      `id` bigint unsigned NOT NULL AUTO_INCREMENT,
      `usuario_id` int NOT NULL,
      `data_ajuste` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
      `motivo_ajuste_id` int DEFAULT NULL,
      `observacoes` text,
      PRIMARY KEY (`id`),
      UNIQUE KEY `id_estoque_ajuste` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `estoque_ajustes_itens` (
      `id` bigint unsigned NOT NULL AUTO_INCREMENT,
      `estoque_ajuste_id` int DEFAULT NULL,
      `produto_id` int DEFAULT NULL,
      `tipo_movimento_id` int DEFAULT NULL,
      `quantidade_informada` decimal(15,4) DEFAULT NULL,
      `quantidade_anterior` decimal(15,4) DEFAULT NULL,
      `quantidade_ajuste` decimal(15,4) DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `id_item_estoque_ajuste` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `estoque_tipos_movimento` (
      `id` bigint unsigned NOT NULL AUTO_INCREMENT,
      `descricao` varchar(50) NOT NULL,
      `sentido` char(1) NOT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      `creatadAt` datetime DEFAULT NULL,
      `updatedAt` datetime DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `id_tipo_movimento` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `fiscal_parametros` (
      `id` int unsigned NOT NULL AUTO_INCREMENT,
      `nome_regra` varchar(100) NOT NULL,
      `cst_ibs_cbs` char(3) NOT NULL,
      `cclass_trib` varchar(10) DEFAULT NULL,
      `aliq_cbs_padrao` decimal(5,2) DEFAULT '0.90',
      `aliq_ibs_padrao` decimal(5,2) DEFAULT '0.10',
      `ind_imposto_seletivo` tinyint(1) DEFAULT '0',
      `perc_reducao_aliquota` decimal(5,2) DEFAULT '0.00',
      `c_cred_pres` varchar(10) DEFAULT NULL,
      `data_atualizacao` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
      `ativo` enum('S','N') DEFAULT 'S',
      PRIMARY KEY (`id`),
      UNIQUE KEY `id` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='cbs = contribuição sobre bens e serviços(federal)   ibs = imposto sobre bens e serviços (estadual/municipal)     cts = codigo da situacao tributaria  class = codigo daclassificação tributaria'
    """,
    """
    CREATE TABLE IF NOT EXISTS `item_reembolsos` (
      `id` int NOT NULL AUTO_INCREMENT,
      `reembolso_id` int NOT NULL,
      `item_venda_id` int NOT NULL,
      `produto_id` int NOT NULL,
      `lote_id` int NOT NULL,
      `quantidade` int NOT NULL,
      `preco_unitario` decimal(10,2) NOT NULL,
      `desconto_tipo` enum('none','porcentagem','valor_fixo') DEFAULT 'none',
      `desconto_valor` decimal(10,2) DEFAULT '0.00',
      PRIMARY KEY (`id`),
      KEY `id_reembolso` (`reembolso_id`),
      KEY `id_item_venda` (`item_venda_id`),
      KEY `id_produto` (`produto_id`),
      KEY `id_lote` (`lote_id`),
      CONSTRAINT `item_reembolsos_ibfk_1` FOREIGN KEY (`reembolso_id`) REFERENCES `reembolsos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
      CONSTRAINT `item_reembolsos_ibfk_2` FOREIGN KEY (`item_venda_id`) REFERENCES `itens_venda` (`id`) ON UPDATE CASCADE,
      CONSTRAINT `item_reembolsos_ibfk_3` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`) ON UPDATE CASCADE,
      CONSTRAINT `item_reembolsos_ibfk_4` FOREIGN KEY (`lote_id`) REFERENCES `lotes` (`id`) ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `motivos_estoque_ajuste` (
      `id` bigint unsigned NOT NULL AUTO_INCREMENT,
      `usuario_id` int NOT NULL,
      `data_cadastro_motivo` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
      `descricao` varchar(100) DEFAULT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      `createdAt` datetime DEFAULT NULL,
      `pdatedAt` datetime DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `id_motivo_estoque_ajuste` (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `pagamentos` (
      `id` int NOT NULL AUTO_INCREMENT,
      `venda_id` int NOT NULL,
      `forma_pagamento` enum('dinheiro','cartao_credito','cartao_debito','pix','outro') NOT NULL,
      `valor_total` decimal(10,2) NOT NULL,
      `parcelas` int DEFAULT NULL,
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      PRIMARY KEY (`id`),
      KEY `id_venda` (`venda_id`),
      CONSTRAINT `pagamentos_ibfk_1` FOREIGN KEY (`venda_id`) REFERENCES `vendas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `parcela_pagamento` (
      `id` int NOT NULL AUTO_INCREMENT,
      `pagamento_id` int NOT NULL,
      `numero_parcela` int NOT NULL,
      `valor_parcela` decimal(10,2) NOT NULL,
      `data_vencimento` datetime NOT NULL,
      `data_pagamento` datetime DEFAULT NULL,
      `status` enum('pendente','pago','atrasado') NOT NULL,
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      PRIMARY KEY (`id`),
      KEY `id_pagamento` (`pagamento_id`),
      CONSTRAINT `parcela_pagamento_ibfk_1` FOREIGN KEY (`pagamento_id`) REFERENCES `pagamentos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `reembolsos` (
      `id` int NOT NULL AUTO_INCREMENT,
      `venda_id` int NOT NULL,
      `usuario_id` int DEFAULT NULL,
      `valor_total` decimal(10,2) NOT NULL,
      `motivo` varchar(500) DEFAULT NULL,
      `tipo` enum('PARCIAL','TOTAL') NOT NULL DEFAULT 'PARCIAL',
      `status` enum('PROCESSANDO','CONCLUIDO','CANCELADO') NOT NULL DEFAULT 'PROCESSANDO',
      `data_reembolso` datetime NOT NULL,
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      `ativo` enum('S','N') DEFAULT 'S',
      PRIMARY KEY (`id`),
      KEY `id_venda` (`venda_id`),
      KEY `reembolsos_ibfk_2_idx` (`usuario_id`),
      CONSTRAINT `reembolsos_ibfk_1` FOREIGN KEY (`venda_id`) REFERENCES `vendas` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
      CONSTRAINT `reembolsos_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS `usermeta` (
      `id` int NOT NULL AUTO_INCREMENT,
      `usuario_id` int NOT NULL,
      `token` varchar(255) NOT NULL,
      `expiresAt` datetime NOT NULL,
      `createdAt` datetime NOT NULL,
      `updatedAt` datetime NOT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
]


def apply(cursor: CursorLike) -> None:
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    try:
        for sql in TABLES_SQL:
            cursor.execute(sql)
    finally:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
