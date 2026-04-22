from typing import Any, Dict, List, Optional, Tuple

from core.caixa_session import CaixaSession
from modules.venda.models.caixa_model import CaixaModel

class CaixaService:
    @staticmethod
    def listar_pdvs_ativos() -> List[Dict[str, Any]]:
        return CaixaModel.listar_pdvs_ativos()

    @staticmethod
    def listar_ultimas_aberturas(limit: int = 10) -> List[Dict[str, Any]]:
        return CaixaModel.listar_ultimas_aberturas(limit)

    @staticmethod
    def restaurar_caixa_aberto(usuario_id: Optional[int]) -> Optional[Dict[str, Any]]:
        if not usuario_id:
            return None

        caixa = CaixaModel.buscar_caixa_aberto_por_usuario(int(usuario_id))
        if not caixa:
            return None

        caixa_data = {
            "id": int(caixa["id"]),
            "pdv_id": int(caixa["pdv_id"]),
            "pdv_label": f"{caixa['identificacao']} - {caixa['descricao']}",
            "usuario_id": int(caixa["usuario_abertura_id"]),
            "usuario_nome": caixa["usuario_nome"],
            "valor_abertura": float(caixa["valor_abertura"] or 0),
            "observacoes": "",
            "breakdown": {},
            "status": caixa["status"],
        }
        CaixaSession.open(caixa_data)
        return caixa_data

    @staticmethod
    def abrir_caixa(
        pdv_id: Optional[int],
        pdv_label: str,
        usuario_id: Optional[int],
        usuario_nome: str,
        valor_abertura: float,
        observacoes: str,
        breakdown: Dict[str, int],
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        if not usuario_id:
            return False, "Nao foi possivel identificar o operador logado.", None

        if pdv_id is None:
            return False, "Selecione um PDV valido para a abertura.", None

        if valor_abertura < 0:
            return False, "O valor de abertura nao pode ser negativo.", None

        caixa_existente = CaixaModel.buscar_caixa_aberto_por_pdv(int(pdv_id))
        if caixa_existente:
            return False, "Ja existe um caixa aberto para este PDV.", None

        try:
            caixa_id = CaixaModel.abrir_caixa(
                pdv_id=int(pdv_id),
                usuario_id=int(usuario_id),
                valor_abertura=float(valor_abertura),
            )
        except Exception as exc:
            return False, f"Erro ao registrar abertura de caixa: {exc}", None

        caixa_data = {
            "id": caixa_id,
            "pdv_id": int(pdv_id),
            "pdv_label": pdv_label,
            "usuario_id": int(usuario_id),
            "usuario_nome": usuario_nome,
            "valor_abertura": float(valor_abertura),
            "observacoes": observacoes,
            "breakdown": breakdown,
            "status": "aberto",
        }
        CaixaSession.open(caixa_data)
        return True, "Caixa aberto com sucesso.", caixa_data
