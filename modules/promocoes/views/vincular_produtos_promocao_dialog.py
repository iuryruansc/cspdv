from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem

from modules.promocoes.services.promocao_service import PromocaoService
from ui.promocoes.vincular_produtos_promocao import Ui_VincularProdutosPromocao
from utils.ui_messages import mostrar_aviso, mostrar_info

class VincularProdutosPromocaoDialog(QDialog, Ui_VincularProdutosPromocao):
    def __init__(self, promocao_id: int, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)

        self.promocao_id = int(promocao_id)
        self._promocao: dict[str, Any] = {}
        self._produtos_encontrados: list[dict[str, Any]] = []
        self._itens_vinculados: list[dict[str, Any]] = []

        self._configurar_tabelas()
        self._conectar_sinais()
        self._carregar_contexto()

    def _configurar_tabelas(self) -> None:
        self.tableProdutos: QTableWidget
        self.tableItensVinculados: QTableWidget
        self.tableProdutos.setColumnWidth(0, 120)
        self.tableProdutos.setColumnWidth(1, 250)
        self.tableProdutos.setColumnWidth(2, 100)
        self.tableProdutos.setColumnWidth(3, 80)
        self.tableItensVinculados.setColumnWidth(0, 220)
        self.tableItensVinculados.setColumnWidth(1, 90)
        self.tableItensVinculados.setColumnWidth(2, 95)
        self.tableItensVinculados.setColumnWidth(3, 85)

    def _conectar_sinais(self) -> None:
        self.btnAtualizar.clicked.connect(self._carregar_contexto)
        self.btnFechar.clicked.connect(self.reject)
        self.btnVincularProduto.clicked.connect(self._vincular_produto)
        self.btnRemoverProduto.clicked.connect(self._remover_produto)
        self.txtBuscaProduto.returnPressed.connect(self._carregar_produtos)
        self.txtBuscaProduto.textChanged.connect(self._carregar_produtos)

    def _carregar_contexto(self) -> None:
        promocao = PromocaoService.buscar_promocao(self.promocao_id)
        if not promocao:
            mostrar_aviso(self, "Promoções", "Promoção não localizada.")
            self.reject()
            return
        self._promocao = promocao
        self._popular_resumo_promocao()
        self._carregar_produtos()
        self._carregar_itens_vinculados()

    def _popular_resumo_promocao(self) -> None:
        nome = str(self._promocao.get("nome") or "-")
        codigo = str(self._promocao.get("codigo") or "-")
        tipo = self._label_tipo(str(self._promocao.get("tipo_desconto") or "-"))
        data_inicio = self._formatar_data(self._promocao.get("data_inicio"))
        data_fim = self._formatar_data(self._promocao.get("data_fim"))

        self.lblCodigoPromocao.setText(f"Código: {codigo}")
        self.lblTipoPromocao.setText(f"Tipo: {tipo}")
        self.lblResumoNomeValor.setText(nome)
        self.lblResumoVigenciaValor.setText(f"{data_inicio} até {data_fim}")
        self.lblResumoRegraValor.setText(self._formatar_regra_promocao(self._promocao))

    def _carregar_produtos(self) -> None:
        self._produtos_encontrados = PromocaoService.buscar_produtos_disponiveis(
            self.promocao_id,
            self.txtBuscaProduto.text().strip(),
        )
        self.tableProdutos.setRowCount(len(self._produtos_encontrados))
        for row, produto in enumerate(self._produtos_encontrados):
            valores = [
                str(produto.get("codigo_barras") or "-"),
                str(produto.get("nome") or "-"),
                self._formatar_moeda(produto.get("preco_venda")),
                str(int(float(produto.get("quantidade_estoque") or 0))),
                "Já vinculado" if str(produto.get("vinculado") or "N").upper() == "S" else "Disponível",
            ]
            for column, valor in enumerate(valores):
                self.tableProdutos.setItem(row, column, QTableWidgetItem(valor))

        if self.tableProdutos.rowCount() > 0:
            self.tableProdutos.selectRow(0)

    def _carregar_itens_vinculados(self) -> None:
        self._itens_vinculados = PromocaoService.listar_itens_promocao(self.promocao_id)
        self.tableItensVinculados.setRowCount(len(self._itens_vinculados))
        for row, item in enumerate(self._itens_vinculados):
            valores = [
                str(item.get("produto") or "-"),
                self._formatar_moeda(item.get("preco_original")),
                self._formatar_moeda(item.get("preco_promocional")),
                self._formatar_moeda(item.get("desconto_aplicado")),
                str(item.get("observacao") or "-"),
            ]
            for column, valor in enumerate(valores):
                self.tableItensVinculados.setItem(row, column, QTableWidgetItem(valor))

        if self.tableItensVinculados.rowCount() > 0:
            self.tableItensVinculados.selectRow(0)

    def _vincular_produto(self) -> None:
        row = self.tableProdutos.currentRow()
        if row < 0 or row >= len(self._produtos_encontrados):
            mostrar_aviso(self, "Promoções", "Selecione um produto para vincular.")
            return

        produto = self._produtos_encontrados[row]
        sucesso, mensagem = PromocaoService.vincular_produto(
            promocao_id=self.promocao_id,
            produto_id=int(produto.get("id") or 0),
            observacao="",
        )
        if not sucesso:
            mostrar_aviso(self, "Promoções", mensagem)
            return

        mostrar_info(self, "Promoções", mensagem)
        self._carregar_produtos()
        self._carregar_itens_vinculados()

    def _remover_produto(self) -> None:
        row = self.tableItensVinculados.currentRow()
        if row < 0 or row >= len(self._itens_vinculados):
            mostrar_aviso(self, "Promoções", "Selecione um vínculo para remover.")
            return

        item = self._itens_vinculados[row]
        produto_nome = str(item.get("produto") or "produto")
        produto_id = int(item.get("produto_id") or 0)
        if produto_id <= 0:
            mostrar_aviso(self, "Promoções", "Não foi possível identificar o produto selecionado.")
            return

        sucesso, mensagem = PromocaoService.remover_vinculo_produto(self.promocao_id, produto_id)
        if not sucesso:
            mostrar_aviso(self, "Promoções", mensagem)
            return

        mostrar_info(self, "Promoções", f"{produto_nome}: {mensagem}")
        self._carregar_produtos()
        self._carregar_itens_vinculados()

    @staticmethod
    def _formatar_moeda(valor: Any) -> str:
        try:
            return f"R$ {float(valor or 0):.2f}".replace(".", ",")
        except (TypeError, ValueError):
            return "R$ 0,00"

    @staticmethod
    def _formatar_data(valor: Any) -> str:
        if hasattr(valor, "strftime"):
            return valor.strftime("%d/%m/%Y %H:%M")
        return str(valor or "-")

    @staticmethod
    def _label_tipo(tipo: str) -> str:
        mapa = {
            "PERCENTUAL": "Desconto por percentual",
            "VALOR": "Desconto por valor",
            "PRECO_FIXO": "Preço promocional",
        }
        return mapa.get(tipo.strip().upper(), tipo)

    @staticmethod
    def _formatar_regra_promocao(promocao: dict[str, Any]) -> str:
        tipo = str(promocao.get("tipo_desconto") or "").strip().upper()
        try:
            percentual = float(promocao.get("desconto_percentual") or 0)
            valor = float(promocao.get("desconto_valor") or 0)
            preco_fixo = float(promocao.get("preco_fixo") or 0)
        except (TypeError, ValueError):
            percentual = valor = preco_fixo = 0.0

        if tipo == "PERCENTUAL":
            return f"{percentual:.2f}%".replace(".", ",")
        if tipo == "VALOR":
            return f"R$ {valor:.2f}".replace(".", ",")
        if tipo == "PRECO_FIXO":
            return f"Preço final R$ {preco_fixo:.2f}".replace(".", ",")
        return "-"
