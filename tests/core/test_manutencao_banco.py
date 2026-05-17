from __future__ import annotations

from unittest.mock import patch

from database.maintenance.validator import ValidationReport
from tools import manutencao_banco


def test_main_executa_fluxo_completo_por_padrao():
    report = ValidationReport([], [], [], [], 12)

    with patch("tools.manutencao_banco.run_pending_migrations", return_value=["20260517_001"]) as migrate, patch(
        "tools.manutencao_banco.run_pending_seeds",
        return_value=["20260517_001"],
    ) as seed, patch(
        "tools.manutencao_banco.validate_database_baseline",
        return_value=report,
    ) as validate:
        result = manutencao_banco.main([])

    assert result == 0
    migrate.assert_called_once()
    seed.assert_called_once()
    validate.assert_called_once()


def test_main_retorna_erro_quando_validacao_tem_pendencias():
    report = ValidationReport(["clientes"], [], [], [], 3)

    with patch("tools.manutencao_banco.validate_database_baseline", return_value=report):
        result = manutencao_banco.main(["--validate"])

    assert result == 1

