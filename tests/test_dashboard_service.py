from decimal import Decimal
from unittest.mock import patch

from modules.admin.services.dashboard_service import DashboardAdminService

@patch("modules.admin.services.dashboard_service.BackupService.backup_esta_vencido", return_value=True)
@patch("modules.admin.services.dashboard_service.BackupService.resumo_ultimo_backup", return_value="12/05/2026 14:00")
@patch("modules.admin.services.dashboard_service.DashboardAdminModel.obter_resumo")
def test_carregar_dashboard_formata_metricas_e_backup(mock_obter_resumo, _mock_resumo_backup, _mock_backup_vencido):
    mock_obter_resumo.return_value = {
        "vendas_hoje": 12,
        "faturamento_dia": Decimal("245.50"),
        "produtos_ativos": 150,
        "clientes_ativos": 42,
        "usuarios_ativos": 5,
        "perfis_ativos": 3,
        "pdvs_ativos": 2,
        "formas_pagamento_ativas": 6,
        "caixas_abertos": 1,
        "contas_vencidas": 4,
        "promocoes_vencidas_ativas": 2,
        "recebimentos_dia": Decimal("80.25"),
        "reembolsos_dia": Decimal("15.00"),
        "ultimas_vendas": [
            {
                "numero_venda": 1001,
                "data_hora": "12/05/2026 13:45",
                "operador": "Iury",
                "forma_pagamento": "Pix",
                "total": Decimal("19.90"),
            }
        ],
    }

    resumo = DashboardAdminService.carregar_dashboard()

    assert resumo["vendas_hoje"] == 12
    assert resumo["faturamento_dia"] == "R$ 245,50"
    assert resumo["recebimentos_dia"] == "R$ 80,25"
    assert resumo["reembolsos_dia"] == "R$ 15,00"
    assert resumo["ultimo_backup_resumo"] == "12/05/2026 14:00"
    assert resumo["ultimas_vendas"][0]["total"] == "R$ 19,90"
    assert any(alerta["acao"] == "abrir_financeiro" for alerta in resumo["alertas_dashboard"])
    assert any(alerta["acao"] == "abrir_promocoes" for alerta in resumo["alertas_dashboard"])
    assert any(alerta["acao"] == "fechar_caixa" for alerta in resumo["alertas_dashboard"])
    assert any(alerta["acao"] == "abrir_configuracoes" for alerta in resumo["alertas_dashboard"])

@patch("modules.admin.services.dashboard_service.BackupService.backup_esta_vencido", return_value=False)
@patch("modules.admin.services.dashboard_service.BackupService.resumo_ultimo_backup", return_value="Nenhum backup realizado ainda")
@patch("modules.admin.services.dashboard_service.DashboardAdminModel.obter_resumo")
def test_carregar_dashboard_monta_alerta_ok_quando_nao_ha_alertas(mock_obter_resumo, _mock_resumo_backup, _mock_backup_vencido):
    mock_obter_resumo.return_value = {
        "vendas_hoje": 0,
        "faturamento_dia": Decimal("0"),
        "produtos_ativos": 0,
        "clientes_ativos": 0,
        "usuarios_ativos": 0,
        "perfis_ativos": 0,
        "pdvs_ativos": 0,
        "formas_pagamento_ativas": 0,
        "caixas_abertos": 0,
        "contas_vencidas": 0,
        "promocoes_vencidas_ativas": 0,
        "recebimentos_dia": Decimal("0"),
        "reembolsos_dia": Decimal("0"),
        "ultimas_vendas": [],
    }

    resumo = DashboardAdminService.carregar_dashboard()

    assert resumo["alertas_dashboard"] == [
        {
            "nivel": "ok",
            "texto": "Nenhum alerta estrutural no momento.",
            "acao": "nenhuma",
        }
    ]
