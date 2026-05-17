from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.admin.services.configuracoes_service import ConfiguracoesService
from modules.auditoria.services.auditoria_service import AuditoriaService
from modules.auth.models.usuario_model import UsuarioModel
from modules.venda.models.caixa_model import CaixaModel
from utils.app_logger import log_warning
from utils.format_utils import formatar_moeda

class CaixaService:
    @staticmethod
    def _parametros_caixa_padrao() -> Dict[str, Any]:
        return {
            "fundo_inicial_sugerido": 0.0,
            "exigir_admin_sangria": True,
            "exigir_admin_reembolso": True,
            "exigir_admin_diferenca_fechamento": True,
        }

    @staticmethod
    def _carregar_parametros_caixa() -> Dict[str, Any]:
        try:
            return ConfiguracoesService.carregar_parametros_caixa()
        except Exception as exc:
            log_warning(f"Falha ao carregar parâmetros de caixa. Usando defaults: {exc}")
            return CaixaService._parametros_caixa_padrao()

    @staticmethod
    def _formatar_data_hora(valor: Any) -> str:
        if isinstance(valor, datetime):
            return valor.strftime("%d/%m/%Y %H:%M")
        if isinstance(valor, str):
            for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%d/%m/%Y %H:%M"):
                try:
                    return datetime.strptime(valor, formato).strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    continue
            return valor
        return "-"

    @staticmethod
    def listar_pdvs_ativos() -> List[Dict[str, Any]]:
        return CaixaModel.listar_pdvs_ativos()

    @staticmethod
    def listar_ultimas_aberturas(limit: int = 10) -> List[Dict[str, Any]]:
        return CaixaModel.listar_ultimas_aberturas(limit)

    @staticmethod
    def listar_caixas_admin(limit: int = 120) -> List[Dict[str, Any]]:
        caixas = CaixaModel.listar_caixas_admin(limit)
        rows: List[Dict[str, Any]] = []

        for caixa in caixas:
            identificacao = str(caixa.get("identificacao") or "PDV")
            descricao = str(caixa.get("descricao") or "").strip()
            pdv_label = identificacao if not descricao else f"{identificacao} - {descricao}"
            data_fechamento = caixa.get("data_fechamento")
            valor_fechamento = caixa.get("valor_fechamento")
            diferenca = caixa.get("diferenca_fechamento")

            rows.append(
                {
                    "id": int(caixa.get("id") or 0),
                    "pdv": pdv_label,
                    "operador": str(caixa.get("operador_abertura") or "-"),
                    "abertura": CaixaService._formatar_data_hora(caixa.get("data_abertura")),
                    "fechamento": CaixaService._formatar_data_hora(data_fechamento) if data_fechamento else "-",
                    "fundo": formatar_moeda(float(caixa.get("valor_abertura") or 0.0)),
                    "valor_fechamento": formatar_moeda(float(valor_fechamento or 0.0))
                    if valor_fechamento not in (None, "")
                    else "-",
                    "diferenca": formatar_moeda(float(diferenca or 0.0)) if diferenca not in (None, "") else "-",
                    "status": str(caixa.get("status") or "-").capitalize(),
                    "ativo": "Sim" if str(caixa.get("ativo") or "N").upper() == "S" else "Nao",
                }
            )

        return rows

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
            return False, "Não foi possível identificar o operador logado.", None

        if pdv_id is None:
            return False, "Selecione um PDV válido para a abertura.", None

        if valor_abertura < 0:
            return False, "O valor de abertura não pode ser negativo.", None

        caixa_existente = CaixaModel.buscar_caixa_aberto_por_pdv(int(pdv_id))
        if caixa_existente:
            return False, "Já existe um caixa aberto para este PDV.", None

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
        AuditoriaService.registrar_evento(
            evento="abertura_caixa",
            categoria="caixa",
            entidade="caixa",
            entidade_id=int(caixa_id),
            usuario_id=int(usuario_id),
            caixa_id=int(caixa_id),
            detalhes={
                "pdv_id": int(pdv_id),
                "pdv_label": pdv_label,
                "valor_abertura": float(valor_abertura),
                "observacoes": observacoes.strip(),
            },
        )
        return True, "Caixa aberto com sucesso.", caixa_data

    @staticmethod
    def obter_resumo_fechamento() -> Dict[str, Any]:
        caixa = CaixaSession.current() or {}
        fundo_inicial = float(caixa.get("valor_abertura") or 0.0)
        total_sangrias = 0.0
        total_suprimentos = 0.0
        total_reembolsos = 0.0
        faturamento_dinheiro = 0.0
        vendas_dia = 0
        faturamento_total = 0.0
        totais_forma_pagamento: List[Dict[str, Any]] = []

        caixa_id = caixa.get("id")
        if caixa_id:
            try:
                resumo_operacional = CaixaModel.obter_resumo_operacional(int(caixa_id))
                resumo_movimentacoes = CaixaModel.obter_resumo_movimentacoes(int(caixa_id))
                faturamento_dinheiro = float(resumo_operacional.get("faturamento_dinheiro") or 0.0)
                vendas_dia = int(resumo_operacional.get("vendas_dia") or 0)
                faturamento_total = float(resumo_operacional.get("faturamento_total") or 0.0)
                totais_forma_pagamento = list(resumo_operacional.get("totais_forma_pagamento") or [])
                total_sangrias = float(resumo_movimentacoes.get("total_sangrias") or 0.0)
                total_suprimentos = float(resumo_movimentacoes.get("total_entradas_manuais") or 0.0)
                total_reembolsos = float(CaixaModel.obter_total_reembolsos(int(caixa_id)) or 0.0)
            except Exception as exc:
                log_warning(f"Falha ao montar resumo de fechamento do caixa {caixa_id}: {exc}")

        total_esperado = (
            fundo_inicial
            - total_sangrias
            + total_suprimentos
            + faturamento_dinheiro
            - total_reembolsos
        )

        return {
            "caixa_id": caixa.get("id"),
            "fundo_inicial": fundo_inicial,
            "total_sangrias": total_sangrias,
            "total_suprimentos": total_suprimentos,
            "total_reembolsos": total_reembolsos,
            "faturamento_dinheiro": faturamento_dinheiro,
            "vendas_dia": vendas_dia,
            "faturamento_total": faturamento_total,
            "total_esperado": total_esperado,
            "totais_forma_pagamento": totais_forma_pagamento,
        }

    @staticmethod
    def obter_resumo_caixa_atual() -> Optional[Dict[str, Any]]:
        caixa = CaixaSession.current() or {}
        caixa_id = caixa.get("id")
        if not caixa_id:
            return None

        return CaixaService.obter_resumo_por_caixa_id(int(caixa_id), caixa_sessao=caixa)

    @staticmethod
    def obter_resumo_por_caixa_id(
        caixa_id: int,
        *,
        caixa_sessao: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        detalhes = CaixaModel.buscar_caixa_por_id(int(caixa_id))
        if not detalhes:
            return None

        fundo_inicial = float(detalhes.get("valor_abertura") or (caixa_sessao or {}).get("valor_abertura") or 0.0)
        total_sangrias = 0.0
        total_suprimentos = 0.0
        total_troco = 0.0
        total_reembolsos = 0.0
        faturamento_dinheiro = 0.0
        vendas_dia = 0
        faturamento_total = 0.0
        totais_forma_pagamento: List[Dict[str, Any]] = []

        try:
            resumo_operacional = CaixaModel.obter_resumo_operacional(int(caixa_id))
            resumo_movimentacoes = CaixaModel.obter_resumo_movimentacoes(int(caixa_id))
            total_reembolsos = float(CaixaModel.obter_total_reembolsos(int(caixa_id)) or 0.0)
            faturamento_dinheiro = float(resumo_operacional.get("faturamento_dinheiro") or 0.0)
            vendas_dia = int(resumo_operacional.get("vendas_dia") or 0)
            faturamento_total = float(resumo_operacional.get("faturamento_total") or 0.0)
            totais_forma_pagamento = list(resumo_operacional.get("totais_forma_pagamento") or [])
            total_sangrias = float(resumo_movimentacoes.get("total_sangrias") or 0.0)
            total_suprimentos = float(
                resumo_movimentacoes.get("total_suprimentos")
                or resumo_movimentacoes.get("total_entradas_manuais")
                or 0.0
            )
            total_troco = float(resumo_movimentacoes.get("total_troco") or 0.0)
        except Exception as exc:
            log_warning(f"Falha ao montar resumo do caixa {caixa_id}: {exc}")

        total_esperado = (
            fundo_inicial
            - total_sangrias
            + total_suprimentos
            + faturamento_dinheiro
            - total_reembolsos
        )
        saldo_atual = (
            fundo_inicial
            + faturamento_dinheiro
            + total_suprimentos
            + total_troco
            - total_sangrias
            - total_reembolsos
        )

        return {
            "caixa_id": int(detalhes["id"]),
            "pdv_label": f"{detalhes['identificacao']} - {detalhes['descricao']}",
            "operador": str(detalhes.get("usuario_nome") or (caixa_sessao or {}).get("usuario_nome") or "Operador"),
            "data_abertura": CaixaService._formatar_data_hora(detalhes.get("data_abertura")),
            "status": str(detalhes.get("status") or "aberto").capitalize(),
            "fundo_inicial": fundo_inicial,
            "vendas_dia": vendas_dia,
            "faturamento_total": faturamento_total,
            "faturamento_dinheiro": faturamento_dinheiro,
            "total_sangrias": total_sangrias,
            "total_suprimentos": total_suprimentos,
            "total_troco": total_troco,
            "saldo_atual": saldo_atual,
            "total_esperado": total_esperado,
            "totais_forma_pagamento": totais_forma_pagamento,
        }

    @staticmethod
    def listar_movimentacoes(tipo: str = "todas") -> List[Dict[str, Any]]:
        caixa = CaixaSession.current() or {}
        caixa_id = caixa.get("id")
        if not caixa_id:
            return []
        return CaixaModel.listar_movimentacoes(int(caixa_id), tipo)

    @staticmethod
    def obter_resumo_movimentacoes() -> Dict[str, Any]:
        caixa = CaixaSession.current() or {}
        caixa_id = caixa.get("id")
        fundo_inicial = float(caixa.get("valor_abertura") or 0.0)
        faturamento_dinheiro = 0.0
        total_reembolsos = 0.0
        resumo: Dict[str, Any] = {}

        if caixa_id:
            try:
                faturamento_dinheiro = float(
                    CaixaModel.obter_resumo_operacional(int(caixa_id)).get("faturamento_dinheiro") or 0.0
                )
                resumo = CaixaModel.obter_resumo_movimentacoes(int(caixa_id))
                total_reembolsos = float(CaixaModel.obter_total_reembolsos(int(caixa_id)) or 0.0)
            except Exception as exc:
                log_warning(f"Falha ao montar resumo de movimentações do caixa {caixa_id}: {exc}")

        total_sangrias = float(resumo.get("total_sangrias") or 0.0)
        total_suprimentos = float(resumo.get("total_suprimentos") or 0.0)
        total_troco = float(resumo.get("total_troco") or 0.0)
        saldo_atual = (
            fundo_inicial
            + faturamento_dinheiro
            + total_suprimentos
            + total_troco
            - total_sangrias
            - total_reembolsos
        )
        return {
            "fundo_inicial": fundo_inicial,
            "faturamento_dinheiro": faturamento_dinheiro,
            "total_sangrias": total_sangrias,
            "total_suprimentos": total_suprimentos,
            "total_troco": total_troco,
            "total_reembolsos": total_reembolsos,
            "saldo_atual": saldo_atual,
        }

    @staticmethod
    def registrar_movimentacao(
        *,
        tipo: str,
        valor: float,
        observacao: str,
        admin_password: str,
    ) -> Tuple[bool, str]:
        caixa = CaixaSession.current() or {}
        usuario = SessionManager.current_user() or {}
        caixa_id = int(caixa.get("id") or 0)
        usuario_id = int(usuario.get("id") or 0)
        tipo_normalizado = str(tipo or "").strip().lower()

        if caixa_id <= 0:
            return False, "Não há caixa aberto para registrar a movimentação."
        if usuario_id <= 0:
            return False, "Não foi possível identificar o operador logado."
        if tipo_normalizado not in {"sangria", "suprimento", "troco"}:
            return False, "Selecione um tipo de movimentação válido."
        if valor <= 0:
            return False, "Informe um valor maior que zero."
        if not observacao.strip():
            return False, "Descreva o motivo da movimentação."

        parametros_caixa = CaixaService._carregar_parametros_caixa()
        exigir_admin = tipo_normalizado == "sangria" and bool(
            parametros_caixa.get("exigir_admin_sangria", True)
        )
        if exigir_admin and not admin_password.strip():
            return False, "Informe a senha de um administrador para continuar."
        if exigir_admin and not CaixaService.validar_admin_para_diferenca(admin_password):
            return False, "Informe uma senha de administrador válida."

        resumo = CaixaService.obter_resumo_movimentacoes()
        saldo_atual = float(resumo.get("saldo_atual") or 0.0)
        if tipo_normalizado == "sangria" and valor > saldo_atual:
            return False, "A sangria não pode ser maior que o saldo atual disponível no caixa."

        try:
            CaixaModel.registrar_movimentacao(
                caixa_id=caixa_id,
                usuario_id=usuario_id,
                tipo=tipo_normalizado,
                valor=valor,
                observacao=observacao.strip(),
            )
            AuditoriaService.registrar_evento(
                evento="movimentacao_caixa",
                categoria="caixa",
                entidade="caixa",
                entidade_id=caixa_id,
                usuario_id=usuario_id,
                caixa_id=caixa_id,
                detalhes={
                    "tipo": tipo_normalizado,
                    "valor": float(valor),
                    "observacao": observacao.strip(),
                },
            )
            return True, "Movimentação registrada com sucesso."
        except Exception as exc:
            return False, f"Erro ao registrar movimentação: {exc}"

    @staticmethod
    def validar_admin_para_diferenca(senha: str) -> bool:
        if not senha.strip():
            return False
        try:
            usuario_admin = UsuarioModel.autenticar_admin_por_senha(senha.strip())
        except Exception as exc:
            log_warning(f"Falha ao validar senha administrativa no caixa: {exc}")
            return False
        return usuario_admin is not None

    @staticmethod
    def fechar_caixa(
        valor_contado: float,
        observacoes: str,
        *,
        admin_password: str = "",
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        usuario = CaixaSession.current()
        operador = (
            UsuarioModel.buscar_sessao_por_id(int(usuario["usuario_id"]))
            if usuario and usuario.get("usuario_id")
            else None
        )
        if not usuario or not usuario.get("id"):
            return False, "Não há caixa aberto para fechar.", None
        if not operador or operador.get("id") is None:
            return False, "Não foi possível identificar o operador para registrar o fechamento.", None
        if valor_contado < 0:
            return False, "O valor contado não pode ser negativo.", None

        resumo = CaixaService.obter_resumo_fechamento()
        total_esperado = float(resumo["total_esperado"])
        diferenca = round(valor_contado - total_esperado, 2)

        parametros_caixa = CaixaService._carregar_parametros_caixa()
        exigir_admin_diferenca = bool(parametros_caixa.get("exigir_admin_diferenca_fechamento", True))
        if exigir_admin_diferenca and abs(diferenca) > 0.009 and not admin_password.strip():
            return False, "Diferença identificada. Informe a senha de um administrador para concluir o fechamento.", None
        if (
            exigir_admin_diferenca
            and abs(diferenca) > 0.009
            and not CaixaService.validar_admin_para_diferenca(admin_password)
        ):
            return False, "Diferença identificada. Informe uma senha de administrador válida para concluir o fechamento.", None

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
        AuditoriaService.registrar_evento(
            evento="fechamento_caixa",
            categoria="caixa",
            entidade="caixa",
            entidade_id=int(usuario["id"]),
            usuario_id=int(operador["id"]),
            caixa_id=int(usuario["id"]),
            detalhes={
                "valor_contado": float(valor_contado),
                "total_esperado": float(total_esperado),
                "diferenca": float(diferenca),
                "observacoes": observacoes.strip(),
            },
        )
        CaixaSession.close()
        return True, "Caixa fechado com sucesso.", caixa_fechado
