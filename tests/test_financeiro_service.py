"""
    python -m pytest tests/test_financeiro_service.py -v
"""

from datetime import datetime
from decimal import Decimal
from typing import cast
from unittest.mock import patch

import pytest

from modules.financeiro.services.financeiro_service import FinanceiroService


class TestFinanceiroService:
    def test_registrar_recebimento_bloqueia_conta_invalida(self):
        with pytest.raises(ValueError, match="conta válida"):
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
        with pytest.raises(ValueError, match="forma de pagamento válida"):
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
        with pytest.raises(ValueError, match="data de recebimento válida"):
            FinanceiroService.registrar_recebimento_conta(
                conta_id=1,
                usuario_id=1,
                caixa_id=1,
                forma_pagamento_id=1,
                valor_recebido=Decimal("10.00"),
                observacao="",
                data_recebimento=cast(datetime, None),
            )

    @patch("modules.financeiro.services.financeiro_service.FinanceiroModel.registrar_recebimento_conta")
    def test_registrar_recebimento_normaliza_observacao_antes_de_salvar(self, mock_registrar):
        data_recebimento = datetime.now()

        FinanceiroService.registrar_recebimento_conta(
            conta_id=1,
            usuario_id=2,
            caixa_id=3,
            forma_pagamento_id=4,
            valor_recebido=Decimal("15.50"),
            observacao="  Recebido no balcão  ",
            data_recebimento=data_recebimento,
        )

        _, kwargs = mock_registrar.call_args
        assert kwargs["conta_id"] == 1
        assert kwargs["usuario_id"] == 2
        assert kwargs["caixa_id"] == 3
        assert kwargs["forma_pagamento_id"] == 4
        assert kwargs["valor_recebido"] == Decimal("15.50")
        assert kwargs["observacao"] == "Recebido no balcão"
        assert kwargs["data_recebimento"] == data_recebimento
