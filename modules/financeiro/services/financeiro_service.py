from __future__ import annotations

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
