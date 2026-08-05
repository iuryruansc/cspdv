from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from modules.auditoria.services.auditoria_service import AuditoriaService
from modules.financeiro.models.financeiro_model import FinanceiroModel

class FinanceiroService:
    @staticmethod
    def listar_pdvs() -> list[dict[str, Any]]:
        return FinanceiroModel.listar_pdvs()

    @staticmethod
    def listar_formas_pagamento() -> list[dict[str, Any]]:
        return FinanceiroModel.listar_formas_pagamento()

    @staticmethod
    def obter_resumo_financeiro(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: int | None = None,
        forma_pagamento: str | None = None,
    ) -> dict[str, Any]:
        return FinanceiroModel.obter_resumo_financeiro(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
            forma_pagamento=forma_pagamento,
        )

    @staticmethod
    def listar_movimentacoes_caixa(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: int | None = None,
    ) -> list[dict[str, Any]]:
        return FinanceiroModel.listar_movimentacoes_caixa(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
        )

    @staticmethod
    def listar_recebimentos(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: int | None = None,
        forma_pagamento: str | None = None,
    ) -> list[dict[str, Any]]:
        return FinanceiroModel.listar_recebimentos(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
            forma_pagamento=forma_pagamento,
        )

    @staticmethod
    def listar_vendas_registradas(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: int | None = None,
        forma_pagamento: str | None = None,
        busca: str | None = None,
    ) -> list[dict[str, Any]]:
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
        data_inicial: date,
        data_final: date,
        pdv_id: int | None = None,
        forma_pagamento: str | None = None,
    ) -> list[dict[str, Any]]:
        return FinanceiroModel.listar_reembolsos(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
            forma_pagamento=forma_pagamento,
        )

    @staticmethod
    def obter_reembolso_detalhado(reembolso_id: int) -> dict[str, Any] | None:
        return FinanceiroModel.obter_reembolso_detalhado(reembolso_id)

    @staticmethod
    def obter_venda_detalhada(venda_id: int) -> dict[str, Any] | None:
        return FinanceiroModel.obter_venda_detalhada(venda_id)

    @staticmethod
    def listar_contas_receber(
        *,
        data_inicial: date,
        data_final: date,
        pdv_id: int | None = None,
        busca: str | None = None,
        status_filtro: str | None = None,
    ) -> list[dict[str, Any]]:
        return FinanceiroModel.listar_contas_receber(
            data_inicial=data_inicial,
            data_final=data_final,
            pdv_id=pdv_id,
            busca=busca,
            status_filtro=status_filtro,
        )

    @staticmethod
    def obter_conta_receber_detalhada(conta_id: int) -> dict[str, Any] | None:
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
    ) -> dict[str, Any]:
        if int(conta_id or 0) <= 0:
            raise ValueError("Selecione uma conta válida para registrar o recebimento.")
        if int(usuario_id or 0) <= 0:
            raise ValueError("Não foi possível identificar o operador que está registrando o recebimento.")
        if int(caixa_id or 0) <= 0:
            raise ValueError("Abra um caixa antes de registrar recebimentos de pendências.")
        if int(forma_pagamento_id or 0) <= 0:
            raise ValueError("Selecione uma forma de pagamento válida para continuar.")
        if valor_recebido <= Decimal("0.00"):
            raise ValueError("Informe um valor maior que zero para o recebimento.")
        if not isinstance(data_recebimento, datetime):
            raise ValueError("Informe uma data de recebimento válida.")

        resultado = FinanceiroModel.registrar_recebimento_conta(
            conta_id=int(conta_id),
            usuario_id=int(usuario_id),
            caixa_id=int(caixa_id),
            forma_pagamento_id=int(forma_pagamento_id),
            valor_recebido=valor_recebido,
            observacao=str(observacao or "").strip(),
            data_recebimento=data_recebimento,
        )
        AuditoriaService.registrar_evento(
            evento="recebimento_pendencia",
            categoria="financeiro",
            entidade="conta_receber",
            entidade_id=int(conta_id),
            usuario_id=int(usuario_id),
            caixa_id=int(caixa_id),
            detalhes={
                "venda_id": int(resultado.get("venda_id") or 0),
                "forma_pagamento": str(resultado.get("forma_pagamento") or ""),
                "valor_recebido": str(resultado.get("valor_recebido") or "0"),
                "valor_aberto": str(resultado.get("valor_aberto") or "0"),
                "status": str(resultado.get("status") or ""),
            },
        )
        return resultado
