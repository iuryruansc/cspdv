from typing import Any, Dict, Tuple

from modules.admin.models.configuracoes_model import ConfiguracoesModel
from modules.pdvs.models.pdv_model import PdvModel
from modules.shared.constants import (
    FLAG_NAO,
    FLAG_SIM,
    STATUS_PDV_ATIVO,
    STATUS_PDV_INATIVO,
    alternar_flag,
    flag_ativa,
)
from modules.venda.models.caixa_model import CaixaModel

ResultadoOperacao = Tuple[bool, str]


class PdvService:
    @staticmethod
    def _normalizar_dados(dados: Dict[str, Any]) -> Dict[str, Any]:
        identificacao = str(dados.get("identificacao") or "").strip().upper()
        descricao = str(dados.get("descricao") or "").strip()
        ativo = FLAG_SIM if flag_ativa(dados.get("ativo"), default=FLAG_NAO) else FLAG_NAO
        status = STATUS_PDV_ATIVO if ativo == FLAG_SIM else STATUS_PDV_INATIVO
        return {
            "identificacao": identificacao,
            "descricao": descricao,
            "ativo": ativo,
            "status": status,
        }

    @staticmethod
    def _validar_dados(dados: Dict[str, Any], *, pdv_id: int | None = None) -> ResultadoOperacao:
        normalizados = PdvService._normalizar_dados(dados)
        if len(normalizados["identificacao"]) < 3:
            return False, "A identificação do PDV deve ter pelo menos 3 caracteres."
        if len(normalizados["descricao"]) < 3:
            return False, "A descrição do PDV deve ter pelo menos 3 caracteres."

        existente = PdvModel.buscar_por_identificacao(normalizados["identificacao"])
        if existente and int(existente.get("id") or 0) != int(pdv_id or 0):
            return False, "Já existe um PDV cadastrado com esta identificação."

        return True, ""

    @staticmethod
    def cadastrar_pdv(dados: Dict[str, Any]) -> ResultadoOperacao:
        normalizados = PdvService._normalizar_dados(dados)
        valido, mensagem = PdvService._validar_dados(normalizados)
        if not valido:
            return False, mensagem

        try:
            registro_id = PdvModel.inserir(normalizados)
        except Exception as exc:
            return False, f"Erro ao salvar PDV:\n{exc}"

        if not registro_id:
            return False, "Não foi possível cadastrar o PDV."
        return True, "PDV cadastrado com sucesso!"

    @staticmethod
    def atualizar_pdv(pdv_id: int, dados: Dict[str, Any]) -> ResultadoOperacao:
        normalizados = PdvService._normalizar_dados(dados)
        valido, mensagem = PdvService._validar_dados(normalizados, pdv_id=int(pdv_id))
        if not valido:
            return False, mensagem

        try:
            atualizado = PdvModel.atualizar(int(pdv_id), normalizados)
        except Exception as exc:
            return False, f"Erro ao atualizar PDV:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar o PDV."
        return True, "PDV atualizado com sucesso!"

    @staticmethod
    def alternar_status(pdv_id: int) -> ResultadoOperacao:
        registro = PdvModel.buscar_por_id(int(pdv_id))
        if not registro:
            return False, "PDV não encontrado."

        novo_status_ativo = alternar_flag(registro.get("ativo"))
        novo_status_texto = STATUS_PDV_ATIVO if novo_status_ativo == FLAG_SIM else STATUS_PDV_INATIVO

        if novo_status_ativo == FLAG_NAO:
            caixa_aberto = CaixaModel.buscar_caixa_aberto_por_pdv(int(pdv_id))
            if caixa_aberto:
                return False, "Não é possível desativar um PDV com caixa aberto."

            empresa = ConfiguracoesModel.carregar_empresa_pdv()
            pdv_padrao_id = empresa.get("pdv_padrao_id")
            try:
                if pdv_padrao_id is not None and int(pdv_padrao_id) == int(pdv_id):
                    return False, "Não é possível desativar o PDV padrão configurado no sistema."
            except (TypeError, ValueError):
                pass

        try:
            atualizado = PdvModel.atualizar_status(int(pdv_id), novo_status_ativo, novo_status_texto)
        except Exception as exc:
            return False, f"Erro ao atualizar status do PDV:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar o status do PDV."
        acao = "ativado" if novo_status_ativo == FLAG_SIM else "desativado"
        return True, f"PDV {acao} com sucesso!"
