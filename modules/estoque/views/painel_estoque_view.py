from __future__ import annotations

from typing import Any, Optional

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QComboBox, QLineEdit, QMainWindow, QTableWidget, QTableWidgetItem

from modules.produtos.views.ajuste_quantidade_dialog import AjusteQuantidadeDialog
from modules.produtos.views.cadastro_produto_view import CadastroProdutoView
from modules.estoque.services.estoque_service import EstoqueService
from ui.estoque.painel_estoque import Ui_PainelEstoque
from utils.format_utils import formatar_inteiro, formatar_moeda
from utils.operational_panel_mixin import PainelOperacionalMixin
from utils.ui_messages import mostrar_aviso, mostrar_info


class PainelEstoqueView(QMainWindow, Ui_PainelEstoque, PainelOperacionalMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.txtBuscaProduto: QLineEdit
        self.cmbCategoriaFiltro: QComboBox
        self.cmbFornecedorFiltro: QComboBox
        self.tableProdutosEstoque: QTableWidget
        self.tableMovimentacoesEstoque: QTableWidget
        self._registros_produtos = []
        self._cadastro_produto_view = None

        self._busca_timer = QTimer(self)
        self._busca_timer.setSingleShot(True)
        self._busca_timer.setInterval(250)
        self._busca_timer.timeout.connect(self._carregar_produtos_lotes)

        self._configurar_tamanho_responsivo()
        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
        self._conectar_eventos()
        self._carregar_filtros()
        self._carregar_painel()

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self._carregar_painel()

    def _conectar_eventos(self) -> None:
        self.btnFiltrar.clicked.connect(self._carregar_painel)
        self.btnNovoProduto.clicked.connect(self._abrir_novo_produto)
        self.btnNovoLote.clicked.connect(self._informar_lotes_indisponiveis)
        self.btnAjusteEstoque.clicked.connect(self._abrir_ajuste_estoque)
        self.txtBuscaProduto.returnPressed.connect(self._carregar_produtos_lotes)
        self.txtBuscaProduto.textChanged.connect(self._agendar_busca)
        self.cmbCategoriaFiltro.currentIndexChanged.connect(self._carregar_produtos_lotes)
        self.cmbFornecedorFiltro.currentIndexChanged.connect(self._carregar_produtos_lotes)

    def _agendar_busca(self) -> None:
        self._busca_timer.start()

    def _carregar_painel(self) -> None:
        self._carregar_metricas()
        self._carregar_produtos_lotes()
        self._carregar_movimentacoes()

    def _carregar_filtros(self) -> None:
        categorias = EstoqueService.listar_categorias()
        fornecedores = EstoqueService.listar_fornecedores()

        self.cmbCategoriaFiltro.blockSignals(True)
        self.cmbFornecedorFiltro.blockSignals(True)
        try:
            self.cmbCategoriaFiltro.clear()
            self.cmbCategoriaFiltro.addItem("Todas as categorias", None)
            for categoria in categorias:
                self.cmbCategoriaFiltro.addItem(
                    str(categoria.get("nome") or "-"),
                    int(categoria.get("id") or 0),
                )

            self.cmbFornecedorFiltro.clear()
            self.cmbFornecedorFiltro.addItem("Todos os fornecedores", None)
            for fornecedor in fornecedores:
                self.cmbFornecedorFiltro.addItem(
                    str(fornecedor.get("nome_fantasia") or "-"),
                    int(fornecedor.get("id_fornecedor") or 0),
                )
        finally:
            self.cmbCategoriaFiltro.blockSignals(False)
            self.cmbFornecedorFiltro.blockSignals(False)

    def _carregar_metricas(self) -> None:
        metricas = EstoqueService.obter_metricas()
        self.lblProdutosAtivosValor.setText(formatar_inteiro(metricas.get("produtos_ativos")))
        self.lblLotesAtivosValor.setText(formatar_inteiro(metricas.get("lotes_ativos")))
        self.lblItensBaixoEstoqueValor.setText(formatar_inteiro(metricas.get("estoque_critico")))
        self.lblMovimentacoesDiaValor.setText(formatar_inteiro(metricas.get("movimentacoes_dia")))

    def _carregar_produtos_lotes(self) -> None:
        registros = EstoqueService.listar_produtos_lotes(
            busca=self.txtBuscaProduto.text().strip(),
            categoria_id=self._combo_data_int(self.cmbCategoriaFiltro),
            fornecedor_id=self._combo_data_int(self.cmbFornecedorFiltro),
        )
        self._registros_produtos = registros

        self.tableProdutosEstoque.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            item_codigo = self._set_table_item(
                self.tableProdutosEstoque,
                row,
                0,
                str(registro.get("codigo_barras") or registro.get("id") or "-"),
            )
            item_codigo.setData(Qt.UserRole, int(registro.get("id") or 0))
            self._set_table_item(self.tableProdutosEstoque, row, 1, str(registro.get("nome") or "-"))
            self._set_table_item(self.tableProdutosEstoque, row, 2, str(registro.get("categoria") or "-"))
            self._set_table_item(self.tableProdutosEstoque, row, 3, str(registro.get("marca") or "-"))
            self._set_table_item(self.tableProdutosEstoque, row, 4, str(registro.get("lote") or "-"))
            self._set_table_item(self.tableProdutosEstoque, row, 5, self._formatar_data(registro.get("data_validade")))
            self._set_table_item(self.tableProdutosEstoque, row, 6, formatar_inteiro(registro.get("quantidade")), alignment=Qt.AlignCenter)
            self._set_table_item(self.tableProdutosEstoque, row, 7, formatar_moeda(registro.get("preco_venda")), alignment=Qt.AlignRight | Qt.AlignVCenter)

        self.lblStatusBar.setText(f"CSPdv - Modulo de Estoque | {len(registros)} registro(s) em Produtos e Lotes")

    def _carregar_movimentacoes(self) -> None:
        registros = EstoqueService.listar_movimentacoes_recentes()
        self.tableMovimentacoesEstoque.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            self._set_table_item(self.tableMovimentacoesEstoque, row, 0, self._formatar_data_hora(registro.get("data_hora")))
            self._set_table_item(self.tableMovimentacoesEstoque, row, 1, str(registro.get("produto") or "-"))
            self._set_table_item(self.tableMovimentacoesEstoque, row, 2, self._formatar_tipo_movimento(registro.get("tipo")))
            self._set_table_item(self.tableMovimentacoesEstoque, row, 3, formatar_inteiro(registro.get("quantidade")), alignment=Qt.AlignCenter)
            self._set_table_item(self.tableMovimentacoesEstoque, row, 4, str(registro.get("usuario") or "-"))

    @staticmethod
    def _set_table_item(
        table: QTableWidget,
        row: int,
        column: int,
        value: str,
        *,
        alignment: int = Qt.AlignLeft | Qt.AlignVCenter,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(value)
        item.setTextAlignment(int(alignment))
        table.setItem(row, column, item)
        return item

    @staticmethod
    def _combo_data_int(combo: QComboBox) -> Optional[int]:
        value = combo.currentData()
        if value in (None, "", 0, "0"):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _formatar_data(value: Any) -> str:
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y")
        return "-"

    @staticmethod
    def _formatar_data_hora(value: Any) -> str:
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y %H:%M")
        return "-"

    @staticmethod
    def _formatar_tipo_movimento(tipo: Any) -> str:
        mapa = {
            "saida_venda": "Saida Venda",
            "entrada_manual": "Entrada Manual",
            "ajuste_manual": "Ajuste Manual",
        }
        chave = str(tipo or "").strip().lower()
        return mapa.get(chave, str(tipo or "-").replace("_", " ").title())

    def _abrir_novo_produto(self) -> None:
        self.hide()
        self._cadastro_produto_view = CadastroProdutoView(parent=self, return_view=self)
        self._cadastro_produto_view.setAttribute(Qt.WA_DeleteOnClose, True)
        self._cadastro_produto_view.destroyed.connect(lambda *_: self._carregar_painel())
        self._cadastro_produto_view.show()
        self._cadastro_produto_view.raise_()
        self._cadastro_produto_view.activateWindow()

    def _informar_lotes_indisponiveis(self) -> None:
        mostrar_info(
            self,
            "Cadastro de lotes",
            "O cadastro manual de lotes ainda nao esta disponivel nesta etapa. Por enquanto, o estoque esta sendo controlado diretamente pelos produtos.",
        )

    def _abrir_ajuste_estoque(self) -> None:
        produto = self._obter_produto_selecionado()
        if not produto:
            mostrar_aviso(
                self,
                "Selecione um produto",
                "Escolha um item na tabela Produtos e Lotes antes de abrir o ajuste de estoque.",
            )
            return

        dialog = AjusteQuantidadeDialog(produto, self)
        if dialog.exec_():
            self._carregar_painel()

    def _obter_produto_selecionado(self) -> Optional[dict]:
        row = self.tableProdutosEstoque.currentRow()
        if row < 0 or row >= len(self._registros_produtos):
            return None
        return self._registros_produtos[row]
