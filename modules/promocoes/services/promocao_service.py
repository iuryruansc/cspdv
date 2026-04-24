from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from core.session_manager import SessionManager
from modules.promocoes.models.promocao_model import PromocaoModel


class PromocaoService:
    @staticmethod
    def gerar_proximo_codigo() -> str:
        return PromocaoModel.gerar_proximo_codigo()

    @staticmethod
    def listar_promocoes(*, busca: str = "", status: str = "", tipo: str = "") -> list[dict[str, Any]]:
        return PromocaoModel.listar(busca=busca, status=status, tipo=tipo)

    @staticmethod
    def listar_itens_promocao(promocao_id: int) -> list[dict[str, Any]]:
        return PromocaoModel.listar_itens_promocao(int(promocao_id))

    @staticmethod
    def cadastrar_promocao(dados: dict[str, Any]) -> tuple[bool, str]:
        nome = str(dados.get("nome") or "").strip()
        if not nome:
            return False, "Informe o nome da promoção."

        data_inicio = dados.get("data_inicio")
        data_fim = dados.get("data_fim")
        if not data_inicio or not data_fim:
            return False, "Informe o período de vigência da promoção."
        if data_fim <= data_inicio:
            return False, "A data final da promoção deve ser maior que a data inicial."

        tipo = str(dados.get("tipo_desconto") or "").strip().upper()
        percentual = PromocaoService._decimal(dados.get("desconto_percentual"))
        valor = PromocaoService._decimal(dados.get("desconto_valor"))
        preco_fixo = PromocaoService._decimal(dados.get("preco_fixo"))

        if tipo == "PERCENTUAL" and percentual <= Decimal("0"):
            return False, "Informe um desconto percentual maior que zero."
        if tipo == "VALOR" and valor <= Decimal("0"):
            return False, "Informe um desconto em valor maior que zero."
        if tipo == "PRECO_FIXO" and preco_fixo <= Decimal("0"):
            return False, "Informe um preço fixo promocional maior que zero."

        usuario = SessionManager.current_user() or {}
        usuario_id = int(usuario.get("id") or 0)
        if usuario_id <= 0:
            return False, "Não foi possível identificar o usuário responsável pelo cadastro."

        payload = {
            "codigo": str(dados.get("codigo") or PromocaoModel.gerar_proximo_codigo()).strip().upper(),
            "nome": nome,
            "classificacao": str(dados.get("classificacao") or "PROMOCAO").strip().upper(),
            "tipo_desconto": tipo,
            "status": str(dados.get("status") or "RASCUNHO").strip().upper(),
            "descricao": str(dados.get("descricao") or "").strip(),
            "observacao": str(dados.get("observacao") or "").strip(),
            "desconto_percentual": float(percentual),
            "desconto_valor": float(valor),
            "preco_fixo": float(preco_fixo),
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "cumulativa": "S" if bool(dados.get("cumulativa")) else "N",
            "ativo": "S" if bool(dados.get("ativo", True)) else "N",
            "usuario_id": usuario_id,
        }

        try:
            promocao_id = PromocaoModel.inserir(payload)
        except Exception as exc:
            return False, f"Erro ao salvar a promoção: {exc}"

        if not promocao_id:
            return False, "Não foi possível concluir o cadastro da promoção."
        return True, "Promoção cadastrada com sucesso."

    @staticmethod
    def _decimal(valor: Any) -> Decimal:
        texto = str(valor or "").strip().replace(".", "").replace(",", ".")
        if not texto:
            return Decimal("0")
        try:
            return Decimal(texto)
        except (InvalidOperation, ValueError):
            return Decimal("0")
