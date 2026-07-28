from __future__ import annotations
from typing import Any

from modules.shared.constants import FLAG_NAO, FLAG_SIM, ResultadoOperacao, alternar_flag, bool_para_flag
from modules.unidades.models.unidade_model import UnidadeModel

class UnidadeService:
    @staticmethod
    def _normalizar_dados(dados: dict[str, Any]) -> dict[str, Any]:
        sigla = str(dados.get("sigla") or "").strip().upper()
        descricao = str(dados.get("descricao") or "").strip()
        codigo_sefaz = str(dados.get("codigo_sefaz") or "").strip().upper()
        fracionavel = 1 if bool(dados.get("fracionavel")) else 0
        ativo = bool_para_flag(dados.get("ativo"))
        return {
            "sigla": sigla,
            "descricao": descricao,
            "codigo_sefaz": codigo_sefaz,
            "fracionavel": fracionavel,
            "ativo": ativo,
        }

    @staticmethod
    def _validar_dados(dados: dict[str, Any], *, unidade_id: int | None = None) -> ResultadoOperacao:
        normalizados = UnidadeService._normalizar_dados(dados)
        if len(normalizados["sigla"]) < 2:
            return False, "A sigla da unidade deve ter pelo menos 2 caracteres."
        if len(normalizados["sigla"]) > 6:
            return False, "A sigla da unidade deve ter no máximo 6 caracteres."
        if len(normalizados["descricao"]) < 3:
            return False, "A descrição da unidade deve ter pelo menos 3 caracteres."
        if normalizados["codigo_sefaz"] and len(normalizados["codigo_sefaz"]) > 6:
            return False, "O código SEFAZ da unidade deve ter no máximo 6 caracteres."

        existente = UnidadeModel.buscar_por_sigla(normalizados["sigla"])
        if existente and int(existente.get("id") or 0) != int(unidade_id or 0):
            return False, "Já existe uma unidade cadastrada com esta sigla."

        return True, ""

    @staticmethod
    def cadastrar_unidade(dados: dict[str, Any]) -> ResultadoOperacao:
        normalizados = UnidadeService._normalizar_dados(dados)
        valido, mensagem = UnidadeService._validar_dados(normalizados)
        if not valido:
            return False, mensagem

        try:
            registro_id = UnidadeModel.inserir(normalizados)
        except Exception as exc:
            return False, f"Erro ao salvar unidade:\n{exc}"

        if not registro_id:
            return False, "Não foi possível cadastrar a unidade."
        return True, "Unidade cadastrada com sucesso!"

    @staticmethod
    def atualizar_unidade(unidade_id: int, dados: dict[str, Any]) -> ResultadoOperacao:
        normalizados = UnidadeService._normalizar_dados(dados)
        valido, mensagem = UnidadeService._validar_dados(normalizados, unidade_id=int(unidade_id))
        if not valido:
            return False, mensagem

        try:
            atualizado = UnidadeModel.atualizar(int(unidade_id), normalizados)
        except Exception as exc:
            return False, f"Erro ao atualizar unidade:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar a unidade."
        return True, "Unidade atualizada com sucesso!"

    @staticmethod
    def alternar_status(unidade_id: int) -> ResultadoOperacao:
        registro = UnidadeModel.buscar_por_id(int(unidade_id))
        if not registro:
            return False, "Unidade não encontrada."

        ativo_atual = str(registro.get("ativo") or FLAG_NAO).strip().upper()
        novo_status = alternar_flag(ativo_atual)

        if novo_status == FLAG_NAO:
            vinculados = UnidadeModel.contar_produtos_vinculados(int(unidade_id))
            if vinculados > 0:
                return False, "Não é possível desativar uma unidade vinculada a produtos."

        try:
            atualizado = UnidadeModel.atualizar_status(int(unidade_id), novo_status)
        except Exception as exc:
            return False, f"Erro ao atualizar status da unidade:\n{exc}"

        if not atualizado:
            return False, "Não foi possível atualizar o status da unidade."
        acao = "ativada" if novo_status == FLAG_SIM else "desativada"
        return True, f"Unidade {acao} com sucesso!"
