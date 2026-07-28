from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any

from core.session_manager import SessionManager
from modules.admin.services.configuracoes_service import ConfiguracoesService
from modules.produtos.models.produto_model import ProdutoModel
from modules.promocoes.models.promocao_model import PromocaoModel
from modules.shared.constants import ResultadoOperacao
from modules.shared.constants import FLAG_NAO, FLAG_SIM

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
    def buscar_promocao(promocao_id: int) -> dict[str, Any] | None:
        return PromocaoModel.buscar_por_id(int(promocao_id))

    @staticmethod
    def buscar_produtos_disponiveis(promocao_id: int, busca: str = "") -> list[dict[str, Any]]:
        return PromocaoModel.buscar_produtos_disponiveis(int(promocao_id), busca)

    @staticmethod
    def cadastrar_promocao(dados: dict[str, Any]) -> ResultadoOperacao:
        payload, erro = PromocaoService._montar_payload_promocao(dados)
        if erro:
            return False, erro
        if payload is None:
            return False, "Não foi possível montar os dados da promoção."

        try:
            promocao_id = PromocaoModel.inserir(payload)
        except Exception as exc:
            return False, f"Erro ao salvar a promoção: {exc}"

        if not promocao_id:
            return False, "Não foi possível concluir o cadastro da promoção."
        return True, "Promoção cadastrada com sucesso."

    @staticmethod
    def atualizar_promocao(promocao_id: int, dados: dict[str, Any]) -> ResultadoOperacao:
        if int(promocao_id) <= 0:
            return False, "Selecione uma promoção válida para editar."

        payload, erro = PromocaoService._montar_payload_promocao(dados)
        if erro:
            return False, erro
        if payload is None:
            return False, "Não foi possível montar os dados da promoção."

        try:
            atualizado = PromocaoModel.atualizar(int(promocao_id), payload)
        except Exception as exc:
            return False, f"Erro ao atualizar a promoção: {exc}"

        if not atualizado:
            return False, "Não foi possível atualizar a promoção selecionada."
        return True, "Promoção atualizada com sucesso."

    @staticmethod
    def duplicar_promocao(promocao_id: int) -> tuple[bool, str, int | None]:
        promocao = PromocaoModel.buscar_por_id(int(promocao_id))
        if not promocao:
            return False, "Promoção não localizada para duplicação.", None

        try:
            novo_id = PromocaoModel.duplicar(int(promocao_id), PromocaoModel.gerar_proximo_codigo())
        except Exception as exc:
            return False, f"Erro ao duplicar a promoção: {exc}", None

        if not novo_id:
            return False, "Não foi possível concluir a duplicação da promoção.", None
        return True, "Promoção duplicada com sucesso em status Rascunho.", int(novo_id)

    @staticmethod
    def encerrar_promocao(promocao_id: int) -> ResultadoOperacao:
        promocao = PromocaoModel.buscar_por_id(int(promocao_id))
        if not promocao:
            return False, "Promoção não localizada para encerramento."

        status_atual = str(promocao.get("status") or "").strip().upper()
        if status_atual == "ENCERRADA":
            return False, "A promoção selecionada já está encerrada."
        if status_atual == "CANCELADA":
            return False, "Promoções canceladas não podem ser encerradas."

        try:
            atualizado = PromocaoModel.atualizar_status(int(promocao_id), "ENCERRADA")
        except Exception as exc:
            return False, f"Erro ao encerrar a promoção: {exc}"
        if not atualizado:
            return False, "Não foi possível encerrar a promoção selecionada."
        return True, "Promoção encerrada com sucesso."

    @staticmethod
    def cancelar_promocao(promocao_id: int) -> ResultadoOperacao:
        promocao = PromocaoModel.buscar_por_id(int(promocao_id))
        if not promocao:
            return False, "Promoção não localizada para cancelamento."

        status_atual = str(promocao.get("status") or "").strip().upper()
        if status_atual == "CANCELADA":
            return False, "A promoção selecionada já está cancelada."
        if status_atual == "ENCERRADA":
            return False, "Promoções encerradas não podem ser canceladas."

        try:
            atualizado = PromocaoModel.atualizar_status(int(promocao_id), "CANCELADA")
        except Exception as exc:
            return False, f"Erro ao cancelar a promoção: {exc}"
        if not atualizado:
            return False, "Não foi possível cancelar a promoção selecionada."
        return True, "Promoção cancelada com sucesso."

    @staticmethod
    def vincular_produto(promocao_id: int, produto_id: int, observacao: str = "") -> ResultadoOperacao:
        promocao = PromocaoModel.buscar_por_id(int(promocao_id))
        if not promocao:
            return False, "Promoção não localizada para vincular produtos."

        if str(promocao.get("ativo") or FLAG_NAO).strip().upper() != FLAG_SIM:
            return False, "A promoção selecionada está inativa."

        produto = ProdutoModel.buscar_por_id(int(produto_id))
        if not produto:
            return False, "Produto não localizado."

        if str(produto.get("ativo") or FLAG_NAO).strip().upper() != FLAG_SIM:
            return False, "O produto selecionado está inativo."

        parametros_promocoes = ConfiguracoesService.carregar_parametros_promocoes()
        if bool(parametros_promocoes.get("bloquear_promocoes_simultaneas", True)):
            conflito = PromocaoModel.buscar_conflito_produto_ativo(int(promocao_id), int(produto_id))
            if conflito:
                nome_promocao = str(conflito.get("nome") or conflito.get("codigo") or "outra promoção")
                status_conflito = str(conflito.get("status") or "").strip().capitalize()
                data_inicio = str(conflito.get("data_inicio_fmt") or "-")
                data_fim = str(conflito.get("data_fim_fmt") or "-")
                return (
                    False,
                    f"Este produto já participa da promoção '{nome_promocao}' "
                    f"({status_conflito}) no período de {data_inicio} até {data_fim}.",
                )

        preco_original = PromocaoService._decimal(produto.get("preco_venda"))
        if preco_original <= Decimal("0"):
            return False, "O produto selecionado não possui preço de venda válido."

        tipo = str(promocao.get("tipo_desconto") or "").strip().upper()
        percentual = PromocaoService._decimal(promocao.get("desconto_percentual"))
        valor = PromocaoService._decimal(promocao.get("desconto_valor"))
        preco_fixo = PromocaoService._decimal(promocao.get("preco_fixo"))

        if tipo == "PERCENTUAL":
            if percentual <= Decimal("0"):
                return False, "A promoção não possui percentual configurado."
            desconto_aplicado = (preco_original * percentual / Decimal("100")).quantize(Decimal("0.01"))
            preco_promocional = (preco_original - desconto_aplicado).quantize(Decimal("0.01"))
        elif tipo == "VALOR":
            if valor <= Decimal("0"):
                return False, "A promoção não possui desconto em valor configurado."
            desconto_aplicado = min(valor, preco_original)
            preco_promocional = (preco_original - desconto_aplicado).quantize(Decimal("0.01"))
        elif tipo == "PRECO_FIXO":
            if preco_fixo <= Decimal("0"):
                return False, "A promoção não possui preço fixo configurado."
            if preco_fixo >= preco_original:
                return False, "O preço fixo promocional deve ser menor que o preço atual do produto."
            preco_promocional = preco_fixo.quantize(Decimal("0.01"))
            desconto_aplicado = (preco_original - preco_promocional).quantize(Decimal("0.01"))
        else:
            return False, "Tipo de desconto da promoção inválido."

        if preco_promocional <= Decimal("0"):
            return False, "O preço promocional calculado precisa ser maior que zero."

        try:
            PromocaoModel.salvar_vinculo_produto(
                promocao_id=int(promocao_id),
                produto_id=int(produto_id),
                preco_original=float(preco_original),
                preco_promocional=float(preco_promocional),
                desconto_aplicado=float(desconto_aplicado),
                observacao=str(observacao or "").strip(),
            )
        except Exception as exc:
            return False, f"Erro ao vincular produto à promoção: {exc}"

        return True, "Produto vinculado à promoção com sucesso."

    @staticmethod
    def remover_vinculo_produto(promocao_id: int, produto_id: int) -> ResultadoOperacao:
        try:
            PromocaoModel.desativar_vinculo_produto(int(promocao_id), int(produto_id))
        except Exception as exc:
            return False, f"Erro ao remover produto da promoção: {exc}"
        return True, "Produto removido da promoção com sucesso."

    @staticmethod
    def _montar_payload_promocao(dados: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
        nome = str(dados.get("nome") or "").strip()
        if not nome:
            return None, "Informe o nome da promoção."

        data_inicio = dados.get("data_inicio")
        data_fim = dados.get("data_fim")
        if not data_inicio or not data_fim:
            return None, "Informe o período de vigência da promoção."
        if data_fim <= data_inicio:
            return None, "A data final da promoção deve ser maior que a data inicial."

        tipo = str(dados.get("tipo_desconto") or "").strip().upper()
        percentual = PromocaoService._decimal(dados.get("desconto_percentual"))
        valor = PromocaoService._decimal(dados.get("desconto_valor"))
        preco_fixo = PromocaoService._decimal(dados.get("preco_fixo"))
        leve_x = dados.get("leve_x")
        pague_y = dados.get("pague_y")
        aplicacao_xpy = str(dados.get("aplicacao_desconto_xpy") or "MAIS_BARATO").strip().upper()
        regras_progressivas = dados.get("regras_progressivas")
        combo_qtd = dados.get("combo_qtd")
        combo_preco = PromocaoService._decimal(dados.get("combo_preco"))

        if tipo == "PERCENTUAL" and percentual <= Decimal("0"):
            return None, "Informe um desconto percentual maior que zero."
        if tipo == "VALOR" and valor <= Decimal("0"):
            return None, "Informe um desconto em valor maior que zero."
        if tipo == "PRECO_FIXO" and preco_fixo <= Decimal("0"):
            return None, "Informe um preço fixo promocional maior que zero."
        if tipo == "LEVE_X_PAGUE_Y":
            if not leve_x or int(leve_x) <= 0:
                return None, "Informe a quantidade 'Leve' maior que zero."
            if not pague_y or int(pague_y) <= 0:
                return None, "Informe a quantidade 'Pague' maior que zero."
            if int(pague_y) >= int(leve_x):
                return None, "'Pague' deve ser menor que 'Leve'."
            if aplicacao_xpy not in ("MAIS_BARATO", "PROPORCIONAL"):
                return None, "Selecione a forma de aplicação do desconto."
        if tipo == "DESCONTO_PROGRESSIVO":
            if not regras_progressivas:
                return None, "Adicione pelo menos uma faixa de desconto progressivo."
        if tipo == "COMBO":
            if not combo_qtd or int(combo_qtd) <= 0:
                return None, "Informe a quantidade do combo maior que zero."
            if combo_preco <= Decimal("0"):
                return None, "Informe o preço do combo maior que zero."

        usuario = SessionManager.current_user() or {}
        usuario_id = int(usuario.get("id") or 0)
        if usuario_id <= 0:
            return None, "Não foi possível identificar o usuário responsável pelo cadastro."

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
            "leve_x": int(leve_x) if leve_x else None,
            "pague_y": int(pague_y) if pague_y else None,
            "aplicacao_desconto_xpy": aplicacao_xpy,
            "regras_progressivas": json.dumps(regras_progressivas) if regras_progressivas else None,
            "combo_qtd": int(combo_qtd) if combo_qtd else None,
            "combo_preco": float(combo_preco),
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "cumulativa": FLAG_SIM if bool(dados.get("cumulativa")) else FLAG_NAO,
            "ativo": FLAG_SIM if bool(dados.get("ativo", True)) else FLAG_NAO,
            "usuario_id": usuario_id,
        }
        return payload, ""

    @staticmethod
    def salvar_regra_e_vincular(promocao_id: int, regra_dados: dict[str, Any]) -> tuple[bool, str, int]:
        promocao = PromocaoModel.buscar_por_id(int(promocao_id))
        if not promocao:
            return False, "Promoção não localizada.", 0

        model_dados = {
            "tipo_regra": str(regra_dados.get("tipo") or "").strip().upper(),
            "alvo_id": None,
            "alvo_ids": str(regra_dados.get("alvo_ids") or "").strip(),
            "alvo_texto": str(regra_dados.get("alvo_ids") or "").strip(),
            "faixa_min": regra_dados.get("faixa_min"),
            "faixa_max": regra_dados.get("faixa_max"),
        }

        try:
            regra_id = PromocaoModel.salvar_regra(int(promocao_id), model_dados)
        except Exception as exc:
            return False, f"Erro ao salvar regra: {exc}", 0

        if not regra_id:
            return False, "Não foi possível salvar a regra.", 0

        try:
            return PromocaoService._aplicar_regra(int(promocao_id), model_dados)
        except Exception as exc:
            return False, f"Erro ao vincular produtos: {exc}", 0

    @staticmethod
    def _aplicar_regra(promocao_id: int, regra_dados: dict[str, Any]) -> tuple[bool, str, int]:
        promocao = PromocaoModel.buscar_por_id(int(promocao_id))
        if not promocao:
            return False, "Promoção não localizada.", 0

        tipo_desconto = str(promocao.get("tipo_desconto") or "").upper()

        try:
            produtos = PromocaoModel.buscar_produtos_por_regra(regra_dados)
        except Exception as exc:
            return False, f"Erro ao buscar produtos: {exc}", 0

        if not produtos:
            return False, "Nenhum produto encontrado para os critérios da regra.", 0

        def calcular(preco_original: float) -> tuple[float, float]:
            return PromocaoService._calcular_preco_promocional(
                preco_original, tipo_desconto, promocao
            )

        try:
            PromocaoModel.limpar_vinculos_automaticos(int(promocao_id))
            vinculados = PromocaoModel.vincular_produtos_automaticamente(
                int(promocao_id), produtos, calcular
            )
        except Exception as exc:
            return False, f"Erro ao vincular produtos: {exc}", 0

        return True, f"{vinculados} produto(s) vinculado(s) com sucesso.", vinculados

    @staticmethod
    def _calcular_preco_promocional(
        preco_original: float,
        tipo_desconto: str,
        promocao: dict[str, Any],
    ) -> tuple[float, float]:
        preco_dec = Decimal(str(preco_original))

        if tipo_desconto == "PERCENTUAL":
            perc = Decimal(str(promocao.get("desconto_percentual") or 0))
            desconto = (preco_dec * perc / Decimal("100")).quantize(Decimal("0.01"))
            return float(preco_dec - desconto), float(desconto)

        if tipo_desconto == "VALOR":
            val = Decimal(str(promocao.get("desconto_valor") or 0))
            desconto = min(val, preco_dec)
            return float(preco_dec - desconto), float(desconto)

        if tipo_desconto == "PRECO_FIXO":
            fixo = Decimal(str(promocao.get("preco_fixo") or 0))
            if fixo >= preco_dec:
                return float(preco_dec), 0.0
            desconto = preco_dec - fixo
            return float(fixo), float(desconto)

        if tipo_desconto == "LEVE_X_PAGUE_Y":
            return float(preco_dec), 0.0

        if tipo_desconto == "DESCONTO_PROGRESSIVO":
            return float(preco_dec), 0.0

        if tipo_desconto == "COMBO":
            return float(preco_dec), 0.0

        return float(preco_dec), 0.0

    @staticmethod
    def excluir_regra(regra_id: int) -> ResultadoOperacao:
        try:
            PromocaoModel.excluir_regra(int(regra_id))
        except Exception as exc:
            return False, f"Erro ao excluir regra: {exc}"
        return True, "Regra excluída com sucesso."

    @staticmethod
    def listar_regras(promocao_id: int) -> list[dict[str, Any]]:
        return PromocaoModel.listar_regras(int(promocao_id))

    @staticmethod
    def _decimal(valor: Any) -> Decimal:
        if valor is None or valor == "":
            return Decimal("0")

        if isinstance(valor, Decimal):
            return valor

        if isinstance(valor, (int, float)):
            try:
                return Decimal(str(valor))
            except (InvalidOperation, ValueError):
                return Decimal("0")

        texto = str(valor).strip()
        if not texto:
            return Decimal("0")

        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")

        try:
            return Decimal(texto)
        except (InvalidOperation, ValueError):
            return Decimal("0")
