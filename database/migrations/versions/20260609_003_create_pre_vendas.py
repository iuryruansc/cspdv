from __future__ import annotations

from database.migrations.runner import CursorLike

VERSION = "20260609_003"
DESCRIPTION = "Cria tabela pre_vendas para armazenar pré-vendas"


def apply(cursor: CursorLike) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS `pre_vendas` (
          `id` int NOT NULL AUTO_INCREMENT,
          `numero_venda` int DEFAULT NULL,
          `cliente_id` int DEFAULT NULL,
          `usuario_id` int NOT NULL,
          `caixa_id` int DEFAULT NULL,
          `data_hora` datetime NOT NULL,
          `valor_total` decimal(10,2) NOT NULL DEFAULT 0.00,
          `itens_json` json NOT NULL,
          `desconto_global` decimal(10,2) DEFAULT 0.00,
          `desconto_itens` decimal(10,2) DEFAULT 0.00,
          `desconto_total` decimal(10,2) DEFAULT 0.00,
          `status` varchar(30) NOT NULL DEFAULT 'PENDENTE',
          `observacao` varchar(255) DEFAULT NULL,
          `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
          `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          KEY `idx_pre_vendas_status` (`status`),
          KEY `idx_pre_vendas_usuario` (`usuario_id`),
          KEY `idx_pre_vendas_caixa` (`caixa_id`),
          CONSTRAINT `fk_pre_vendas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
          CONSTRAINT `fk_pre_vendas_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`),
          CONSTRAINT `fk_pre_vendas_caixa` FOREIGN KEY (`caixa_id`) REFERENCES `caixas` (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        """
    )
