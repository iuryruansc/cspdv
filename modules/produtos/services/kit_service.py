from __future__ import annotations

from typing import Any

from database.connection import db_transaction
from modules.produtos.models.kit_model import KitModel


class KitService:
    @staticmethod
    def listar_resumo() -> list[dict[str, Any]]:
        return KitModel.listar_resumo()

    @staticmethod
    def listar_todas() -> list[dict[str, Any]]:
        return KitModel.listar_todas()

    @staticmethod
    def buscar_por_id(kit_id: int) -> dict[str, Any] | None:
        return KitModel.buscar_por_id(kit_id)

    @staticmethod
    def listar_itens(kit_id: int) -> list[dict[str, Any]]:
        return KitModel.listar_itens(kit_id)

    @staticmethod
    def _verificar_estoque_componentes(itens: list[dict[str, Any]], kit_quantidade: int) -> tuple[bool, str]:
        with db_transaction() as cur:
            for item in itens:
                produto_id = int(item["produto_id"])
                qtd_por_kit = int(item["quantidade"])
                total_necessario = qtd_por_kit * kit_quantidade
                cur.execute(
                    "SELECT nome, quantidade_estoque FROM produtos WHERE id = %s LIMIT 1",
                    (produto_id,),
                )
                row = cur.fetchone()
                if not row:
                    return False, f"Produto ID {produto_id} nao encontrado."
                estoque_atual = int(row.get("quantidade_estoque") or 0)
                if estoque_atual < total_necessario:
                    return False, (
                        f"Estoque insuficiente para '{row.get('nome')}': "
                        f"disponivel {estoque_atual}, necessario {total_necessario}."
                    )
            return True, ""

    @staticmethod
    def _reduzir_estoque_componentes(itens: list[dict[str, Any]], kit_quantidade: int) -> None:
        with db_transaction() as cur:
            for item in itens:
                produto_id = int(item["produto_id"])
                qtd_por_kit = int(item["quantidade"])
                total_reduzir = qtd_por_kit * kit_quantidade
                cur.execute(
                    "UPDATE produtos SET quantidade_estoque = quantidade_estoque - %s WHERE id = %s",
                    (total_reduzir, produto_id),
                )

    @staticmethod
    def cadastrar_kit(
        *,
        cod_produto: str | None,
        nome: str,
        descricao: str,
        preco_kit: float,
        quantidade_estoque: int,
        itens: list[dict[str, Any]],
    ) -> tuple[bool, str]:
        if not nome.strip():
            return False, "Nome do kit e obrigatorio."
        if float(preco_kit or 0) <= 0:
            return False, "Informe um preco para o kit."
        if not itens:
            return False, "Adicione ao menos um item ao kit."
        if int(quantidade_estoque or 0) < 0:
            return False, "A quantidade em estoque nao pode ser negativa."

        cod_produto_limpo = str(cod_produto or "").strip() or None

        ok, msg = KitService._verificar_estoque_componentes(itens, kit_quantidade=int(quantidade_estoque))
        if not ok:
            return False, msg

        KitService._reduzir_estoque_componentes(itens, kit_quantidade=int(quantidade_estoque))

        kit_id = KitModel.criar_kit(
            cod_produto=cod_produto_limpo,
            nome=str(nome).strip(),
            descricao=str(descricao).strip(),
            preco_kit=float(preco_kit),
            quantidade_estoque=int(quantidade_estoque),
            itens=itens,
        )
        return True, f"Kit #{kit_id} cadastrado com sucesso. Estoque dos componentes reduzido."

    @staticmethod
    def atualizar_kit(
        *,
        kit_id: int,
        cod_produto: str | None,
        nome: str,
        descricao: str,
        preco_kit: float,
        quantidade_estoque: int,
        itens: list[dict[str, Any]],
    ) -> tuple[bool, str]:
        if int(kit_id or 0) <= 0:
            return False, "Kit invalido."
        if not nome.strip():
            return False, "Nome do kit e obrigatorio."
        if float(preco_kit or 0) <= 0:
            return False, "Informe um preco para o kit."
        if not itens:
            return False, "Adicione ao menos um item ao kit."
        if int(quantidade_estoque or 0) < 0:
            return False, "A quantidade em estoque nao pode ser negativa."

        cod_produto_limpo = str(cod_produto or "").strip() or None

        KitModel.atualizar_kit(
            kit_id=int(kit_id),
            cod_produto=cod_produto_limpo,
            nome=str(nome).strip(),
            descricao=str(descricao).strip(),
            preco_kit=float(preco_kit),
            quantidade_estoque=int(quantidade_estoque),
            itens=itens,
        )
        return True, f"Kit #{kit_id} atualizado com sucesso."

    @staticmethod
    def alternar_status(kit_id: int) -> tuple[bool, str]:
        from modules.shared.constants import FLAG_SIM

        kit = KitModel.buscar_por_id(kit_id)
        if not kit:
            return False, "Kit nao encontrado."
        sucesso = KitModel.alternar_status(kit_id)
        if sucesso:
            novo = "ativado" if str(kit.get("ativo") or FLAG_SIM).upper() != FLAG_SIM else "desativado"
            return True, f"Kit '{kit.get('nome')}' {novo} com sucesso."
        return False, "Nao foi possivel alterar o status do kit."

    @staticmethod
    def excluir_kit(kit_id: int) -> tuple[bool, str]:
        kit = KitModel.buscar_por_id(kit_id)
        if not kit:
            return False, "Kit nao encontrado."
        if KitModel.excluir_kit(kit_id):
            return True, f"Kit '{kit.get('nome')}' excluido com sucesso."
        return False, "Nao foi possivel excluir o kit."

    @staticmethod
    def ajustar_estoque(
        *,
        kit_id: int,
        quantidade_atual: int,
        nova_quantidade: int,
        observacao: str,
    ) -> tuple[bool, str]:
        kit = KitModel.buscar_por_id(kit_id)
        if not kit:
            return False, "Kit nao encontrado."

        diferenca = nova_quantidade - quantidade_atual

        if diferenca == 0:
            return False, "Nenhuma alteracao realizada."

        KitModel.ajustar_estoque_e_componentes(
            kit_id=kit_id,
            nova_quantidade_kit=nova_quantidade,
            diferenca=diferenca,
        )

        if diferenca > 0:
            return True, (
                f"Estoque do kit ajustado de {quantidade_atual} para {nova_quantidade}. "
                f"Estoque dos componentes reduzido em {diferenca} unidade(s) cada."
            )
        return True, (
            f"Estoque do kit ajustado de {quantidade_atual} para {nova_quantidade}. "
            f"Estoque dos componentes aumentado em {abs(diferenca)} unidade(s) cada."
        )
