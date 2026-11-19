from __future__ import annotations

from typing import Any

from modules.produtos.models.produto_model import ProdutoModel
from modules.produtos.models.kit_model import KitModel
from modules.shared.constants import (
    FLAG_NAO,
    FLAG_SIM,
    ResultadoOperacao,
    TIPO_MOVIMENTACAO_AJUSTE_MANUAL,
    TIPO_MOVIMENTACAO_ENTRADA_MANUAL,
    TIPO_MOVIMENTACAO_SAIDA_MANUAL,
    alternar_flag,
)
from utils.app_logger import log_error

class ProdutoService:
    @staticmethod
    def buscar_para_venda(termo: str) -> list[dict[str, Any]]:
        termo_limpo = str(termo or "").strip()
        if len(termo_limpo) < 2:
            return []
        try:
            produtos = ProdutoModel.buscar_para_venda(termo_limpo)
        except Exception as e:
            log_error("Erro ao buscar produtos para venda no serviço.", e)
            produtos = []

        try:
            kits = KitModel.buscar_para_venda(termo_limpo)
        except Exception as e:
            log_error("Erro ao buscar kits para venda no serviço.", e)
            kits = []

        return produtos + kits

    @staticmethod
    def _validar_dados_produto(dados: dict[str, Any], produto_id: int | None = None) -> ResultadoOperacao:
        nome = str(dados.get("nome", "")).strip()
        cod_produto = str(dados.get("cod_produto", "")).strip()
        codigo_barras = str(dados.get("codigo_barras", "")).strip()
        ativo = str(dados.get("ativo", "")).strip().upper()
        categoria_id = dados.get("categoria_id")
        marca_id = dados.get("marca_id")
        fornecedor_id = dados.get("fornecedor_id")

        if len(nome) < 3:
            return False, "O nome do produto deve ter pelo menos 3 caracteres."

        if not codigo_barras:
            return False, "O código de barras é obrigatório."

        if categoria_id is None:
            return False, "A categoria do produto é obrigatória."

        if marca_id is None:
            return False, "A marca do produto é obrigatória."

        if fornecedor_id is None:
            return False, "O fornecedor do produto é obrigatório."

        if ativo not in {FLAG_SIM, FLAG_NAO}:
            return False, "O status ativo do produto é obrigatório."

        if float(dados.get("preco_venda", 0)) <= 0:
            return False, "O preço de venda deve ser maior que zero."

        if cod_produto:
            produto_existente = ProdutoModel.buscar_por_codigo(cod_produto)
            produto_existente_id = int((produto_existente or {}).get("id") or 0)
            if produto_existente and produto_existente_id != int(produto_id or 0):
                return False, "Este código do produto já está em uso."

        produto_existente_barras = ProdutoModel.buscar_por_codigo_barras(codigo_barras)
        produto_existente_barras_id = int((produto_existente_barras or {}).get("id") or 0)
        if produto_existente_barras and produto_existente_barras_id != int(produto_id or 0):
            return False, "Este código de barras já está em uso."

        return True, ""

    @staticmethod
    def validar_e_buscar_por_codigo(codigo_bruto: str) -> tuple[dict[str, Any] | None, str, bool]:
        codigo = str(codigo_bruto).strip()

        if not codigo:
            return None, "O campo de código está vazio.", False

        if len(codigo) < 3:
            return None, "Código muito curto para ser válido.", False

        try:
            produto = ProdutoModel.buscar_por_codigo(codigo)

            if produto:
                return produto, "Produto encontrado com sucesso!", True
            return None, "Produto não localizado no sistema.", False

        except Exception as e:
            log_error("Erro ao validar e buscar produto por código.", e)
            return None, "Erro técnico ao consultar o banco de dados.", False

    @staticmethod
    def _normalizar_dados(dados: dict[str, Any]) -> dict[str, Any]:
        resultado = dict(dados)
        cod_produto = str(resultado.get("cod_produto") or "").strip()
        resultado["cod_produto"] = cod_produto if cod_produto else None
        return resultado

    @staticmethod
    def cadastrar_produto(dados: dict[str, Any]) -> ResultadoOperacao:
        dados_norm = ProdutoService._normalizar_dados(dados)
        valido, mensagem = ProdutoService._validar_dados_produto(dados_norm)
        if not valido:
            return False, mensagem

        try:
            ProdutoModel.inserir(dados_norm)
            return True, "Produto cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar produto:\n{e}"

    @staticmethod
    def atualizar_produto(produto_id: int, dados: dict[str, Any]) -> ResultadoOperacao:
        produto = ProdutoModel.buscar_por_id(int(produto_id))
        if not produto:
            return False, "Produto não localizado para edição."

        dados_norm = ProdutoService._normalizar_dados(dados)
        valido, mensagem = ProdutoService._validar_dados_produto(dados_norm, produto_id=produto_id)
        if not valido:
            return False, mensagem

        try:
            ProdutoModel.atualizar(int(produto_id), dados_norm)
            return True, "Produto atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar produto:\n{e}"

    @staticmethod
    def ajustar_quantidade(
        produto_id: int,
        modo: str,
        quantidade: float,
        observacao: str,
        usuario_id: int,
    ) -> ResultadoOperacao:
        if not usuario_id:
            return False, "Não foi possível identificar o usuário logado para registrar o ajuste."

        if quantidade <= 0:
            return False, "Informe uma quantidade maior que zero para o ajuste."

        observacao_limpa = str(observacao or "").strip()
        if not observacao_limpa:
            return False, "Informe o motivo da entrada ou saída de produto."

        produto = ProdutoModel.buscar_por_id(int(produto_id))
        if not produto:
            return False, "Produto não localizado para ajuste."

        quantidade_atual = float(produto.get("quantidade_estoque") or 0)
        modo_normalizado = str(modo).strip().lower()

        if modo_normalizado in {"entrada", "entrada de produto", "somar"}:
            nova_quantidade = quantidade_atual + quantidade
            tipo_movimentacao = TIPO_MOVIMENTACAO_ENTRADA_MANUAL
            descricao_modo = "entrada de produto"
        elif modo_normalizado in {"saida", "saída", "saida de produto", "saída de produto", "subtrair"}:
            nova_quantidade = quantidade_atual - quantidade
            tipo_movimentacao = TIPO_MOVIMENTACAO_SAIDA_MANUAL
            descricao_modo = "saída de produto"
        elif modo_normalizado == "definir":
            # Compatibilidade com chamadas antigas; a interface atual não oferece
            # mais esse modo porque ele não representa uma movimentação explícita.
            nova_quantidade = quantidade
            tipo_movimentacao = TIPO_MOVIMENTACAO_AJUSTE_MANUAL
            descricao_modo = "definir"
        else:
            return False, "Modo de ajuste inválido."

        if nova_quantidade < 0:
            return False, "O ajuste resultaria em estoque negativo."

        if nova_quantidade == quantidade_atual:
            return False, "Nenhuma alteração foi realizada, pois o estoque final seria igual ao atual."

        quantidade_ajuste = nova_quantidade - quantidade_atual
        observacao_final = (
            f"{descricao_modo.title()} - {observacao_limpa}"
        )

        try:
            ProdutoModel.ajustar_quantidade(
                produto_id=int(produto_id),
                nova_quantidade=nova_quantidade,
                quantidade_anterior=quantidade_atual,
                quantidade_ajuste=quantidade_ajuste,
                usuario_id=int(usuario_id),
                observacoes=observacao_final,
                tipo_movimentacao=tipo_movimentacao,
            )
            return True, "Movimentação de estoque registrada com sucesso."
        except Exception as e:
            return False, f"Erro ao registrar ajuste de estoque:\n{e}"

    @staticmethod
    def alternar_status(produto_id: int) -> ResultadoOperacao:
        produto = ProdutoModel.buscar_por_id(int(produto_id))
        if not produto:
            return False, "Produto não localizado."

        ativo_atual = str(produto.get("ativo") or FLAG_NAO).strip().upper()
        novo_status = alternar_flag(ativo_atual)

        try:
            ProdutoModel.atualizar_status(int(produto_id), novo_status)
            acao = "ativado" if novo_status == FLAG_SIM else "desativado"
            return True, f"Produto {acao} com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar status do produto:\n{e}"
