from typing import Any, Dict, List, Optional, Tuple

from core.caixa_session import CaixaSession
from modules.auth.models.usuario_model import UsuarioModel
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

    @staticmethod
    def obter_resumo_fechamento() -> Dict[str, Any]:
        caixa = CaixaSession.current() or {}
        fundo_inicial = float(caixa.get("valor_abertura") or 0.0)
        total_sangrias = 0.0
        total_suprimentos = 0.0
        faturamento_dinheiro = 0.0
        vendas_dia = 0
        faturamento_total = 0.0
        total_esperado = fundo_inicial - total_sangrias + total_suprimentos + faturamento_dinheiro

        return {
            "caixa_id": caixa.get("id"),
            "fundo_inicial": fundo_inicial,
            "total_sangrias": total_sangrias,
            "total_suprimentos": total_suprimentos,
            "faturamento_dinheiro": faturamento_dinheiro,
            "vendas_dia": vendas_dia,
            "faturamento_total": faturamento_total,
            "total_esperado": total_esperado,
            "totais_forma_pagamento": [],
        }

    @staticmethod
    def validar_admin_para_diferenca(senha: str) -> bool:
        if not senha.strip():
            return False
        usuario_admin = UsuarioModel.autenticar_admin_por_senha(senha.strip())
        return usuario_admin is not None

    @staticmethod
    def fechar_caixa(
        valor_contado: float,
        observacoes: str,
        *,
        admin_password: str = "",
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        usuario = CaixaSession.current()
        operador = UsuarioModel.buscar_sessao_por_id(int(usuario["usuario_id"])) if usuario and usuario.get("usuario_id") else None
        if not usuario or not usuario.get("id"):
            return False, "Nao ha caixa aberto para fechar.", None
        if not operador or operador.get("id") is None:
            return False, "Nao foi possivel identificar o operador para registrar o fechamento.", None

        resumo = CaixaService.obter_resumo_fechamento()
        total_esperado = float(resumo["total_esperado"])
        diferenca = round(valor_contado - total_esperado, 2)

        if abs(diferenca) > 0.009 and not CaixaService.validar_admin_para_diferenca(admin_password):
            return False, "Diferenca identificada. Informe a senha de um administrador para concluir o fechamento.", None

        try:
            CaixaModel.fechar_caixa(
                caixa_id=int(usuario["id"]),
                usuario_fechamento_id=int(operador["id"]),
                valor_fechamento=valor_contado,
                diferenca=diferenca,
                observacoes=observacoes,
            )
        except Exception as exc:
            return False, f"Erro ao registrar o fechamento do caixa: {exc}", None

        caixa_fechado = {
            "caixa_id": int(usuario["id"]),
            "valor_contado": valor_contado,
            "total_esperado": total_esperado,
            "diferenca": diferenca,
        }
        CaixaSession.close()
        return True, "Caixa fechado com sucesso.", caixa_fechado
