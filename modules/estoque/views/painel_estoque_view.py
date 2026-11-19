from __future__ import annotations

from typing import Any

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.produtos.views.ajuste_quantidade_dialog import AjusteQuantidadeDialog
from modules.produtos.views.cadastro_produto_view import CadastroProdutoView
from modules.estoque.services.estoque_service import EstoqueService
from modules.estoque.views.detalhes_movimentacao_dialog import DetalhesMovimentacaoDialog
from modules.estoque.views.fornecimento_dialog import FornecimentoDialog
from modules.shared.constants import (
    TIPO_MOVIMENTACAO_AJUSTE_MANUAL,
    TIPO_MOVIMENTACAO_ENTRADA_MANUAL,
    TIPO_MOVIMENTACAO_SAIDA_FORNECIMENTO,
    TIPO_MOVIMENTACAO_SAIDA_MANUAL,
    TIPO_MOVIMENTACAO_SAIDA_VENDA,
)
from ui.estoque.painel_estoque import Ui_PainelEstoque
from utils.combo_loader import combo_int
from utils.format_utils import formatar_data, formatar_data_hora, formatar_inteiro, formatar_moeda
from utils.operational_panel_mixin import PainelOperacionalMixin
from utils.table_widget_utils import set_table_item
from utils.ui_messages import mostrar_aviso, mostrar_info


class _PainelEstoqueSignals(QObject):
    concluido = pyqtSignal(object, object, object, int)
    falhou = pyqtSignal(str, int)


class _PainelEstoqueRunnable(QRunnable):
    def __init__(self, filtros: dict[str, Any], geracao: int):
        super().__init__()
        self._filtros = filtros
        self._geracao = geracao
        self.signals = _PainelEstoqueSignals()

    def run(self) -> None:
        try:
            metricas = EstoqueService.obter_metricas()
            produtos = EstoqueService.listar_produtos_lotes(**self._filtros)
            movimentacoes = {
                "ultimas": EstoqueService.listar_movimentacoes_recentes(),
                "entradas": EstoqueService.listar_movimentacoes_recentes(
                    tipos=["entrada_manual", "entrada_reembolso", "entrada_reembolso_kit"]
                ),
                "saidas": EstoqueService.listar_movimentacoes_recentes(
                    tipos=["saida_venda", "saida_venda_kit", "saida_manual", "ajuste_manual"]
                ),
                "fornecimentos": EstoqueService.listar_movimentacoes_recentes(
                    tipos=[TIPO_MOVIMENTACAO_SAIDA_FORNECIMENTO]
                ),
            }
            self.signals.concluido.emit(metricas, produtos, movimentacoes, self._geracao)
        except Exception as exc:
            self.signals.falhou.emit(str(exc), self._geracao)


class PainelEstoqueView(QMainWindow, Ui_PainelEstoque, PainelOperacionalMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.txtBuscaProduto: QLineEdit
        self.cmbCategoriaFiltro: QComboBox
        self.cmbFornecedorFiltro: QComboBox
        self.tableProdutosEstoque: QTableWidget
        self.tableMovimentacoesEstoque: QTableWidget
        self.lblProdutosAtivosValor: QLabel
        self.lblLotesAtivosValor: QLabel
        self.lblItensBaixoEstoqueValor: QLabel
        self.lblMovimentacoesDiaValor: QLabel
        self._registros_produtos = []
        self._pagina_produtos = 1
        self._por_pagina_produtos = 50
        self._total_produtos = 0
        self._cadastro_produto_view = None
        self._painel_load_generation = 0
        self._painel_pool = QThreadPool(self)
        self._painel_pool.setMaxThreadCount(2)
        self._painel_inicializado = False

        # A tabela é uma visão operacional: alterações de estoque devem passar
        # pelos fluxos de ajuste, fornecimento ou cadastro, nunca por edição direta.
        self.tableProdutosEstoque.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableProdutosEstoque.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableProdutosEstoque.setSelectionMode(QAbstractItemView.SingleSelection)

        self._busca_timer = QTimer(self)
        self._busca_timer.setSingleShot(True)
        self._busca_timer.setInterval(250)
        self._busca_timer.timeout.connect(self._carregar_produtos_lotes)

        self._configurar_tamanho_responsivo()
        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
        self._configurar_abas_movimentacoes()
        self._configurar_paginacao_produtos()
        self._configurar_layout_tabelas()
        self._conectar_eventos()
        self._carregar_filtros()

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        if not self._painel_inicializado:
            self._painel_inicializado = True
            self._carregar_painel()

    def _conectar_eventos(self) -> None:
        self.btnFiltrar.clicked.connect(self._carregar_painel)
        self.btnLimparFiltros.clicked.connect(self._limpar_filtros)
        self.btnNovoProduto.clicked.connect(self._abrir_novo_produto)
        self.btnFornecimento.clicked.connect(self._abrir_fornecimento)
        self.btnAjusteEstoque.clicked.connect(self._abrir_ajuste_estoque)
        self.tableMovimentacoesEstoque.itemDoubleClicked.connect(self._abrir_detalhes_movimentacao)
        self.tableEntradas.itemDoubleClicked.connect(self._abrir_detalhes_movimentacao)
        self.tableSaidas.itemDoubleClicked.connect(self._abrir_detalhes_movimentacao)
        self.tableFornecimentos.itemDoubleClicked.connect(self._abrir_detalhes_movimentacao)
        self.txtBuscaProduto.returnPressed.connect(self._carregar_produtos_lotes)
        self.txtBuscaProduto.textChanged.connect(self._agendar_busca)
        self.cmbCategoriaFiltro.currentIndexChanged.connect(self._carregar_produtos_lotes)
        self.cmbFornecedorFiltro.currentIndexChanged.connect(self._carregar_produtos_lotes)

    def _limpar_filtros(self) -> None:
        self._busca_timer.stop()
        self.txtBuscaProduto.blockSignals(True)
        self.cmbCategoriaFiltro.blockSignals(True)
        self.cmbFornecedorFiltro.blockSignals(True)
        try:
            self.txtBuscaProduto.clear()
            self.cmbCategoriaFiltro.setCurrentIndex(0)
            self.cmbFornecedorFiltro.setCurrentIndex(0)
        finally:
            self.txtBuscaProduto.blockSignals(False)
            self.cmbCategoriaFiltro.blockSignals(False)
            self.cmbFornecedorFiltro.blockSignals(False)
        self._carregar_painel()

    def _configurar_abas_movimentacoes(self) -> None:
        self.frameMovimentacoesLayout.removeWidget(self.tableMovimentacoesEstoque)
        self.tableMovimentacoesEstoque.setParent(None)
        self.abasMovimentacoes = QTabWidget(self.frameMovimentacoes)

        aba_movimentacoes = QWidget(self.abasMovimentacoes)
        layout_movimentacoes = QVBoxLayout(aba_movimentacoes)
        layout_movimentacoes.setContentsMargins(0, 0, 0, 0)
        layout_movimentacoes.addWidget(self.tableMovimentacoesEstoque)
        self.abasMovimentacoes.addTab(aba_movimentacoes, "Últimas Movimentações")

        self.tableEntradas = self._criar_tabela_movimentacao()
        aba_entradas = QWidget(self.abasMovimentacoes)
        layout_entradas = QVBoxLayout(aba_entradas)
        layout_entradas.setContentsMargins(0, 0, 0, 0)
        layout_entradas.addWidget(self.tableEntradas)
        self.abasMovimentacoes.addTab(aba_entradas, "Entradas")

        self.tableSaidas = self._criar_tabela_movimentacao()
        aba_saidas = QWidget(self.abasMovimentacoes)
        layout_saidas = QVBoxLayout(aba_saidas)
        layout_saidas.setContentsMargins(0, 0, 0, 0)
        layout_saidas.addWidget(self.tableSaidas)
        self.abasMovimentacoes.addTab(aba_saidas, "Saídas")

        self.tableFornecimentos = self._criar_tabela_movimentacao(
            ["Data/Hora", "Produto", "Destinatário", "Qtd.", "Usuário"]
        )

        aba_fornecimentos = QWidget(self.abasMovimentacoes)
        layout_fornecimentos = QVBoxLayout(aba_fornecimentos)
        layout_fornecimentos.setContentsMargins(0, 0, 0, 0)
        layout_fornecimentos.addWidget(self.tableFornecimentos)
        self.abasMovimentacoes.addTab(aba_fornecimentos, "Fornecimentos")
        self._tabelas_movimentacoes = {
            "ultimas": self.tableMovimentacoesEstoque,
            "entradas": self.tableEntradas,
            "saidas": self.tableSaidas,
            "fornecimentos": self.tableFornecimentos,
        }
        self.frameMovimentacoesLayout.addWidget(self.abasMovimentacoes)

    def _criar_tabela_movimentacao(self, cabecalhos=None) -> QTableWidget:
        tabela = QTableWidget(self.abasMovimentacoes)
        tabela.setColumnCount(5)
        tabela.setHorizontalHeaderLabels(cabecalhos or ["Data/Hora", "Produto", "Tipo", "Qtd.", "Usuário"])
        tabela.setAlternatingRowColors(True)
        tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabela.setSortingEnabled(True)
        tabela.verticalHeader().setVisible(False)
        header = tabela.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        return tabela

    def _configurar_paginacao_produtos(self) -> None:
        self.lblPaginacaoProdutos = QLabel(self.frameProdutos)
        self.lblPaginacaoProdutos.setStyleSheet("color:#315676; font-size:11px; padding:6px 8px;")
        self.btnPaginaAnterior = QPushButton("Anterior", self.frameProdutos)
        self.btnPaginaProxima = QPushButton("Próxima", self.frameProdutos)
        for botao in (self.btnPaginaAnterior, self.btnPaginaProxima):
            botao.setMinimumHeight(30)
            botao.setMaximumWidth(100)
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 2, 6, 4)
        layout.addWidget(self.lblPaginacaoProdutos)
        layout.addStretch()
        layout.addWidget(self.btnPaginaAnterior)
        layout.addWidget(self.btnPaginaProxima)
        self.frameProdutosLayout.addLayout(layout)
        self.btnPaginaAnterior.clicked.connect(self._pagina_anterior)
        self.btnPaginaProxima.clicked.connect(self._pagina_proxima)

    def _configurar_layout_tabelas(self) -> None:
        self.tablesHLayout.setStretch(0, 7)
        self.tablesHLayout.setStretch(1, 3)
        self.frameMovimentacoes.setMinimumWidth(0)
        self.frameMovimentacoes.setMaximumWidth(560)

        header_produtos = self.tableProdutosEstoque.horizontalHeader()
        for coluna in (0, 2, 3, 4, 5, 6, 7):
            header_produtos.setSectionResizeMode(coluna, QHeaderView.ResizeToContents)
        header_produtos.setSectionResizeMode(1, QHeaderView.Stretch)

    def _agendar_busca(self) -> None:
        self._busca_timer.start()

    def _carregar_painel(self) -> None:
        self._painel_load_generation += 1
        geracao = self._painel_load_generation
        self.lblStatusBar.setText("CSPdv - Modulo de Estoque | Carregando dados...")

        filtros = {
            "busca": self.txtBuscaProduto.text().strip(),
            "categoria_id": combo_int(self.cmbCategoriaFiltro),
            "fornecedor_id": combo_int(self.cmbFornecedorFiltro),
            "pagina": self._pagina_produtos,
            "por_pagina": self._por_pagina_produtos,
        }
        worker = _PainelEstoqueRunnable(filtros, geracao)
        worker.signals.concluido.connect(self._painel_carregado)
        worker.signals.falhou.connect(self._painel_falhou)
        self._painel_pool.start(worker)

    @pyqtSlot(object, object, object, int)
    def _painel_carregado(
        self,
        metricas: dict[str, Any],
        produtos: dict[str, Any],
        movimentacoes: dict[str, list[dict[str, Any]]],
        geracao: int,
    ) -> None:
        if geracao != self._painel_load_generation:
            return
        self._renderizar_metricas(metricas)
        self._renderizar_produtos_lotes(produtos)
        for chave, registros in movimentacoes.items():
            self._renderizar_movimentacoes(chave, registros)

    @pyqtSlot(str, int)
    def _painel_falhou(self, mensagem: str, geracao: int) -> None:
        if geracao != self._painel_load_generation:
            return
        self.lblStatusBar.setText("CSPdv - Modulo de Estoque | Falha ao carregar dados")
        mostrar_aviso(
            self,
            "Falha ao carregar estoque",
            f"Não foi possível consultar os dados do estoque agora.\n\nDetalhes: {mensagem}",
        )

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

    def _renderizar_metricas(self, metricas: dict[str, Any]) -> None:
        self.lblProdutosAtivosValor.setText(formatar_inteiro(metricas.get("produtos_ativos")))
        self.lblLotesAtivosValor.setText(formatar_inteiro(metricas.get("lotes_ativos")))
        self.lblItensBaixoEstoqueValor.setText(formatar_inteiro(metricas.get("estoque_critico")))
        self.lblMovimentacoesDiaValor.setText(formatar_inteiro(metricas.get("movimentacoes_dia")))

    def _carregar_produtos_lotes(self) -> None:
        self._pagina_produtos = 1
        self._carregar_painel()

    def _pagina_anterior(self) -> None:
        if self._pagina_produtos <= 1:
            return
        self._pagina_produtos -= 1
        self._carregar_painel()

    def _pagina_proxima(self) -> None:
        total_paginas = max(1, (self._total_produtos + self._por_pagina_produtos - 1) // self._por_pagina_produtos)
        if self._pagina_produtos >= total_paginas:
            return
        self._pagina_produtos += 1
        self._carregar_painel()

    def _renderizar_produtos_lotes(self, pagina_resultado: dict[str, Any]) -> None:
        registros = list(pagina_resultado.get("registros") or [])
        self._total_produtos = int(pagina_resultado.get("total") or 0)
        self._pagina_produtos = int(pagina_resultado.get("pagina") or self._pagina_produtos)
        self._registros_produtos = registros

        self.tableProdutosEstoque.setUpdatesEnabled(False)
        self.tableProdutosEstoque.setRowCount(len(registros))
        try:
            for row, registro in enumerate(registros):
                item_codigo = set_table_item(
                    self.tableProdutosEstoque,
                    row,
                    0,
                    str(registro.get("codigo_barras") or registro.get("id") or "-"),
                )
                item_codigo.setData(Qt.UserRole, int(registro.get("id") or 0))
                set_table_item(self.tableProdutosEstoque, row, 1, str(registro.get("nome") or "-"))
                set_table_item(self.tableProdutosEstoque, row, 2, str(registro.get("categoria") or "-"))
                set_table_item(self.tableProdutosEstoque, row, 3, str(registro.get("marca") or "-"))
                set_table_item(self.tableProdutosEstoque, row, 4, str(registro.get("lote") or "-"))
                set_table_item(self.tableProdutosEstoque, row, 5, formatar_data(registro.get("data_validade")))
                set_table_item(
                    self.tableProdutosEstoque,
                    row,
                    6,
                    formatar_inteiro(registro.get("quantidade")),
                    alignment=Qt.AlignCenter,
                )
                set_table_item(
                    self.tableProdutosEstoque,
                    row,
                    7,
                    formatar_moeda(registro.get("preco_venda")),
                    alignment=Qt.AlignRight | Qt.AlignVCenter,
                )
        finally:
            self.tableProdutosEstoque.setUpdatesEnabled(True)

        total_paginas = max(1, (self._total_produtos + self._por_pagina_produtos - 1) // self._por_pagina_produtos)
        self.lblPaginacaoProdutos.setText(
            f"Página {self._pagina_produtos} de {total_paginas} • {self._total_produtos} produto(s)"
        )
        self.btnPaginaAnterior.setEnabled(self._pagina_produtos > 1)
        self.btnPaginaProxima.setEnabled(self._pagina_produtos < total_paginas)
        self.lblStatusBar.setText(
            f"CSPdv - Modulo de Estoque | {self._total_produtos} registro(s) em Produtos e Lotes"
        )

    def _renderizar_movimentacoes(self, chave: str, registros: list[dict[str, Any]]) -> None:
        tabela = self._tabelas_movimentacoes[chave]
        indice_aba = {"ultimas": 0, "entradas": 1, "saidas": 2, "fornecimentos": 3}[chave]
        nomes_abas = {
            "ultimas": "Últimas Movimentações",
            "entradas": "Entradas",
            "saidas": "Saídas",
            "fornecimentos": "Fornecimentos",
        }
        self.abasMovimentacoes.setTabText(indice_aba, f"{nomes_abas[chave]} ({len(registros)})")
        tabela.setSortingEnabled(False)
        tabela.setUpdatesEnabled(False)
        tabela.setRowCount(len(registros) or 1)
        try:
            if not registros:
                self._renderizar_tabela_vazia(tabela, "Nenhuma movimentação encontrada.")
                return
            for row, registro in enumerate(registros):
                item_data = set_table_item(tabela, row, 0, formatar_data_hora(registro.get("data_hora")))
                item_data.setData(Qt.UserRole, registro)
                set_table_item(tabela, row, 1, str(registro.get("produto") or "-"))
                valor_coluna_tipo = (
                    str(registro.get("destinatario") or "-")
                    if chave == "fornecimentos"
                    else self._formatar_tipo_movimento(registro.get("tipo"))
                )
                set_table_item(tabela, row, 2, valor_coluna_tipo)
                set_table_item(
                    tabela,
                    row,
                    3,
                    formatar_inteiro(registro.get("quantidade")),
                    alignment=Qt.AlignCenter,
                )
                set_table_item(tabela, row, 4, str(registro.get("usuario") or "-"))
        finally:
            tabela.setUpdatesEnabled(True)
            tabela.setSortingEnabled(True)

    @staticmethod
    def _renderizar_tabela_vazia(tabela: QTableWidget, mensagem: str) -> None:
        tabela.clearContents()
        tabela.setSpan(0, 0, 1, tabela.columnCount())
        item = tabela.item(0, 0) or QTableWidgetItem()
        item.setText(mensagem)
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(Qt.gray)
        item.setFlags(Qt.NoItemFlags)
        tabela.setItem(0, 0, item)

    def _abrir_detalhes_movimentacao(self, item, _coluna: int | None = None) -> None:
        row = int(item.row())
        tabela = item.tableWidget()
        if tabela is None:
            return
        registro = tabela.item(row, 0).data(Qt.UserRole)
        if not isinstance(registro, dict):
            return
        tipo = (
            "Saída Fornecimento"
            if tabela is self.tableFornecimentos
            else self._formatar_tipo_movimento(registro.get("tipo"))
        )
        dialog = DetalhesMovimentacaoDialog(
            registro,
            tipo,
            self,
        )
        dialog.exec_()

    def _abrir_detalhes_fornecimento(self, item, _coluna: int | None = None) -> None:
        row = int(item.row())
        registro = self.tableFornecimentos.item(row, 0).data(Qt.UserRole)
        if not isinstance(registro, dict):
            return
        dialog = DetalhesMovimentacaoDialog(
            registro,
            "Saída Fornecimento",
            self,
        )
        dialog.exec_()

    @staticmethod
    def _formatar_tipo_movimento(tipo: Any) -> str:
        mapa = {
            TIPO_MOVIMENTACAO_SAIDA_VENDA: "Saída Venda",
            TIPO_MOVIMENTACAO_ENTRADA_MANUAL: "Entrada Manual",
            TIPO_MOVIMENTACAO_SAIDA_MANUAL: "Saída Manual",
            TIPO_MOVIMENTACAO_SAIDA_FORNECIMENTO: "Saída Fornecimento",
            TIPO_MOVIMENTACAO_AJUSTE_MANUAL: "Ajuste Manual",
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
            "O cadastro manual de lotes ainda não está disponível nesta etapa. Por enquanto, o estoque está sendo controlado diretamente pelos produtos.",
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

    def _abrir_fornecimento(self) -> None:
        dialog = FornecimentoDialog(self)
        if dialog.exec_():
            self._carregar_painel()

    def _obter_produto_selecionado(self) -> dict | None:
        row = self.tableProdutosEstoque.currentRow()
        if row < 0 or row >= len(self._registros_produtos):
            return None
        return self._registros_produtos[row]
