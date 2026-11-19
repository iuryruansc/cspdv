from PyQt5.QtWidgets import QHeaderView, QLabel, QPushButton

from modules.promocoes.views.painel_promocoes_view import PainelPromocoesView


class VisaoGeralPromocoesView(PainelPromocoesView):
    """Painel de consulta das promoções, sem ações administrativas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSPdv - Visão geral de promoções")
        self.btnGerenciarPromocoes = QPushButton("Gerenciar promoções", self.frameHeader)
        self.btnGerenciarPromocoes.setObjectName("btnGerenciarPromocoes")
        self.btnGerenciarPromocoes.setToolTip(
            "Abrir filtros, criação, edição e vinculação de produtos."
        )
        self.btnGerenciarPromocoes.setStyleSheet(
            "QPushButton { background:#2f80c9; color:white; border:none; border-radius:8px; "
            "padding:8px 12px; font-weight:700; } "
            "QPushButton:hover { background:#276faa; }"
        )
        self.btnGerenciarPromocoes.setFixedWidth(160)
        self.headerHLayout.insertWidget(5, self.btnGerenciarPromocoes)
        self.btnGerenciarPromocoes.clicked.connect(self._abrir_gerenciamento)

        self.lblVisaoGeralBanner = QLabel(self.contentWrap)
        self.lblVisaoGeralBanner.setWordWrap(True)
        self.lblVisaoGeralBanner.setStyleSheet(
            "background:#ffffff; color:#174d78; border:1px solid #c9ddeb; "
            "border-left:5px solid #2f80c9; border-radius:10px; "
            "padding:12px 16px; font-size:12px; font-weight:600;"
        )
        self.contentWrapLayout.insertWidget(0, self.lblVisaoGeralBanner)
        self._mostrar_visao_geral()

    def _abrir_gerenciamento(self) -> None:
        self._mostrar_gerenciamento()

    def _abrir_visao_geral(self) -> None:
        self._mostrar_visao_geral()

    def _mostrar_visao_geral(self) -> None:
        self.setWindowTitle("CSPdv - Visão geral de promoções")
        self.lblModulo.setText("VISÃO GERAL DE PROMOÇÕES")
        self.lblPromocoesSection.setText("Resumo das promoções")
        self.lblPromocoesHint.setText(
            "Consulte campanhas, vigências e produtos vinculados em uma visão rápida."
        )
        self.lblAgendaSection.setText("Produtos em destaque")
        self.lblAgendaHint.setText(
            "Selecione uma promoção para consultar seus preços e descontos."
        )
        self.lblVisaoGeralBanner.setText(
            "Acompanhe o cenário promocional atual. "
            "Selecione uma campanha para consultar seus produtos, preços e descontos."
        )
        self.lblVisaoGeralBanner.show()
        self.toolbarCard.hide()
        self.btnVisaoGeral.show()
        self.btnGerenciarPromocoes.show()
        self._configurar_tabela_visao_geral()
        self._aplicar_estado_navegacao(visao_geral=True)
        self.lblStatusBar.setText(
            f"CSPdv - Visão geral | {len(self._promocoes_filtradas)} promoção(ões)"
        )

    def _mostrar_gerenciamento(self) -> None:
        self.setWindowTitle("CSPdv - Gerenciar promoções")
        self.lblModulo.setText("PROMOÇÕES E CAMPANHAS")
        self.lblPromocoesSection.setText("Promoções cadastradas")
        self.lblPromocoesHint.setText(
            "Gerencie campanhas, vigências e regras promocionais em um painel único."
        )
        self.lblAgendaSection.setText("Itens vinculados")
        self.lblAgendaHint.setText(
            "Visualize rapidamente os produtos ou grupos afetados pela promoção selecionada."
        )
        self.lblVisaoGeralBanner.hide()
        self.toolbarCard.show()
        self.btnVisaoGeral.show()
        self.btnGerenciarPromocoes.show()
        self._configurar_tabela_gerenciamento()
        self._aplicar_estado_navegacao(visao_geral=False)
        self.lblStatusBar.setText(
            "CSPdv - Módulo de Promoções | "
            f"{len(self._promocoes_filtradas)} promoção(ões) listada(s) com os filtros atuais"
        )

    def _configurar_tabela_visao_geral(self) -> None:
        self.frameAgenda.setMinimumWidth(580)
        self.frameAgenda.setMaximumWidth(620)
        header_itens = self.tableItensPromocao.horizontalHeader()
        for coluna in range(self.tableItensPromocao.columnCount()):
            header_itens.setSectionResizeMode(coluna, QHeaderView.Interactive)
        for coluna, largura in ((0, 185), (1, 84), (2, 84), (3, 76), (4, 82), (5, 82)):
            self.tableItensPromocao.setColumnWidth(coluna, largura)
        for coluna in (0, 5):
            self.tablePromocoes.setColumnHidden(coluna, True)
        self.tablePromocoes.verticalHeader().setDefaultSectionSize(42)
        self.tablePromocoes.setStyleSheet(
            "QTableWidget { background:#ffffff; border:1px solid #c9ddeb; "
            "border-radius:10px; gridline-color:#e5eef5; font-size:12px; } "
            "QTableWidget::item { padding:8px; } "
            "QTableWidget::item:selected { background:#d9ecfa; color:#174d78; }"
        )

    def _configurar_tabela_gerenciamento(self) -> None:
        for coluna in range(self.tablePromocoes.columnCount()):
            self.tablePromocoes.setColumnHidden(coluna, False)
        self.tablePromocoes.verticalHeader().setDefaultSectionSize(30)
        self.tablePromocoes.setStyleSheet("")

    def _aplicar_estado_navegacao(self, *, visao_geral: bool) -> None:
        estilo_ativo = (
            "QPushButton { background:#f1f7fc; color:#174d78; border:1px solid #b8d3e8; "
            "border-radius:8px; padding:8px 12px; font-weight:700; }"
        )
        estilo_inativo = (
            "QPushButton { background:transparent; color:#dbeaf7; border:1px solid transparent; "
            "border-radius:8px; padding:8px 12px; font-weight:700; } "
            "QPushButton:hover { background:rgba(255,255,255,0.12); }"
        )
        self.btnVisaoGeral.setStyleSheet(estilo_ativo if visao_geral else estilo_inativo)
        self.btnGerenciarPromocoes.setStyleSheet(estilo_inativo if visao_geral else estilo_ativo)
