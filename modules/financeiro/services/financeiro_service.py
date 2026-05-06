from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

from modules.financeiro.models.financeiro_model import FinanceiroModel


class FinanceiroService:
    @staticmethod
    def listar_pdvs() -> List[Dict[str, Any]]:
        return FinanceiroModel.listar_pdvs()

    @staticmethod
    def listar_formas_pagamento() -> List[Dict[str, Any]]:
        return FinanceiroModel.listar_formas_pagamento()

    @staticmethod
    def obter_resumo_financeiro(
        *,
        data_inicial,
        data_final,
        pdv_id=None,
        forma_pagamento=None,
    ) -> Dict[str, Any]:
        return FinanceiroModel.obter_resumo_financeiro(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
            forma_pagamento=forma_pagamento,
        )

    @staticmethod
    def listar_movimentacoes_caixa(
        *,
        data_inicial,
        data_final,
        pdv_id=None,
    ) -> List[Dict[str, Any]]:
        return FinanceiroModel.listar_movimentacoes_caixa(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
        )

    @staticmethod
    def listar_recebimentos(
        *,
        data_inicial,
        data_final,
        pdv_id=None,
        forma_pagamento=None,
    ) -> List[Dict[str, Any]]:
        return FinanceiroModel.listar_recebimentos(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
            forma_pagamento=forma_pagamento,
        )

    @staticmethod
    def listar_vendas_registradas(
        *,
        data_inicial,
        data_final,
        pdv_id=None,
        forma_pagamento=None,
        busca=None,
    ) -> List[Dict[str, Any]]:
        return FinanceiroModel.listar_vendas_registradas(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
            forma_pagamento=forma_pagamento,
            busca=busca,
        )

    @staticmethod
    def listar_reembolsos(
        *,
        data_inicial,
        data_final,
        pdv_id=None,
        forma_pagamento=None,
    ) -> List[Dict[str, Any]]:
        return FinanceiroModel.listar_reembolsos(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
            forma_pagamento=forma_pagamento,
        )

    @staticmethod
    def obter_venda_detalhada(venda_id: int) -> Dict[str, Any] | None:
        return FinanceiroModel.obter_venda_detalhada(venda_id)

    @staticmethod
    def listar_contas_receber(
        *,
        data_inicial,
        data_final,
        pdv_id=None,
        busca=None,
        status_filtro=None,
    ) -> List[Dict[str, Any]]:
        return FinanceiroModel.listar_contas_receber(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
            busca=busca,
            status_filtro=status_filtro,
        )

    @staticmethod
    def obter_conta_receber_detalhada(conta_id: int) -> Dict[str, Any] | None:
        return FinanceiroModel.obter_conta_receber_detalhada(conta_id)

    @staticmethod
    def registrar_recebimento_conta(
        *,
        conta_id: int,
        usuario_id: int,
        caixa_id: int,
        forma_pagamento_id: int,
        valor_recebido: Decimal,
        observacao: str,
        data_recebimento: datetime,
    ) -> Dict[str, Any]:
        return FinanceiroModel.registrar_recebimento_conta(
            conta_id=conta_id,
            usuario_id=usuario_id,
            caixa_id=caixa_id,
            forma_pagamento_id=forma_pagamento_id,
            valor_recebido=valor_recebido,
            observacao=observacao,
            data_recebimento=data_recebimento,
        )
