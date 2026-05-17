from datetime import datetime
from decimal import Decimal
from typing import cast
from unittest.mock import patch

import pytest

from modules.financeiro.services.financeiro_service import FinanceiroService


class TestFinanceiroService:
    def test_registrar_recebimento_bloqueia_conta_invalida(self):
        with pytest.raises(ValueError, match="conta v.+lida"):
            FinanceiroService.registrar_recebimento_conta(
                conta_id=0,
                usuario_id=1,
                caixa_id=1,
                forma_pagamento_id=1,
                valor_recebido=Decimal("10.00"),
                observacao="",
                data_recebimento=datetime.now(),
            )

    def test_registrar_recebimento_bloqueia_caixa_invalido(self):
        with pytest.raises(ValueError, match="Abra um caixa"):
            FinanceiroService.registrar_recebimento_conta(
                conta_id=1,
                usuario_id=1,
                caixa_id=0,
                forma_pagamento_id=1,
                valor_recebido=Decimal("10.00"),
                observacao="",
                data_recebimento=datetime.now(),
            )

    def test_registrar_recebimento_bloqueia_forma_pagamento_invalida(self):
        with pytest.raises(ValueError, match="forma de pagamento v.+lida"):
            FinanceiroService.registrar_recebimento_conta(
                conta_id=1,
                usuario_id=1,
                caixa_id=1,
                forma_pagamento_id=0,
                valor_recebido=Decimal("10.00"),
                observacao="",
                data_recebimento=datetime.now(),
            )

    def test_registrar_recebimento_bloqueia_data_invalida(self):
        with pytest.raises(ValueError, match="data de recebimento v.+lida"):
            FinanceiroService.registrar_recebimento_conta(
                conta_id=1,
                usuario_id=1,
                caixa_id=1,
                forma_pagamento_id=1,
                valor_recebido=Decimal("10.00"),
                observacao="",
                data_recebimento=cast(datetime, None),
            )

    @patch("modules.financeiro.services.financeiro_service.AuditoriaService.registrar_evento")
    @patch("modules.financeiro.services.financeiro_service.FinanceiroModel.registrar_recebimento_conta")
    def test_registrar_recebimento_normaliza_observacao_antes_de_salvar(
        self,
        mock_registrar,
        mock_auditar,
    ):
        data_recebimento = datetime.now()
        mock_registrar.return_value = {
            "venda_id": 9,
            "forma_pagamento": "Dinheiro",
            "valor_recebido": Decimal("15.50"),
            "valor_aberto": Decimal("30.00"),
            "status": "PARCIAL",
        }

        FinanceiroService.registrar_recebimento_conta(
            conta_id=1,
            usuario_id=2,
            caixa_id=3,
            forma_pagamento_id=4,
            valor_recebido=Decimal("15.50"),
            observacao="  Recebido no balcao  ",
            data_recebimento=data_recebimento,
        )

        _, kwargs = mock_registrar.call_args
        assert kwargs["conta_id"] == 1
        assert kwargs["usuario_id"] == 2
        assert kwargs["caixa_id"] == 3
        assert kwargs["forma_pagamento_id"] == 4
        assert kwargs["valor_recebido"] == Decimal("15.50")
        assert kwargs["observacao"] == "Recebido no balcao"
        assert kwargs["data_recebimento"] == data_recebimento
        mock_auditar.assert_called_once()
