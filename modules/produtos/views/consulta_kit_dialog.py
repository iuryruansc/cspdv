from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
)

from modules.produtos.services.kit_service import KitService
from utils.format_utils import formatar_moeda
from utils.table_widget_utils import set_table_item


class ConsultaKitDialog(QDialog):
    def __init__(self, kit_id: int, parent=None):
        super().__init__(parent)
        self._kit_id = kit_id
        self._kit: dict[str, Any] = {}
        self._itens: list[dict[str, Any]] = []
        self._montar_interface()
        self._carregar_dados()

    def _montar_interface(self) -> None:
        self.setWindowTitle("Detalhes do Kit")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        titulo = QLabel("Detalhes do Kit", self)
        titulo.setStyleSheet("font-size:18px;font-weight:bold;color:#14324c;")
        layout.addWidget(titulo)

        self.frameInfo = QFrame(self)
        self.frameInfo.setStyleSheet(
            "QFrame { background: #f8fafc; border: 1px solid #d1d9e6; border-radius: 6px; padding: 12px; }"
        )
        infoLayout = QHBoxLayout(self.frameInfo)
        infoLayout.setSpacing(30)

        col1 = QVBoxLayout()
        col1.setSpacing(6)

        self.lblNomeTitulo = QLabel("Kit:", self.frameInfo)
        self.lblNomeTitulo.setStyleSheet("font-weight:bold;color:#46627d;")
        col1.addWidget(self.lblNomeTitulo)

        self.lblNomeValor = QLabel("-", self.frameInfo)
        self.lblNomeValor.setStyleSheet("font-size:14px;color:#1a3a5c;font-weight:bold;")
        col1.addWidget(self.lblNomeValor)

        self.lblDescricaoTitulo = QLabel("Descricao:", self.frameInfo)
        self.lblDescricaoTitulo.setStyleSheet("font-weight:bold;color:#46627d;")
        col1.addWidget(self.lblDescricaoTitulo)

        self.lblDescricaoValor = QLabel("-", self.frameInfo)
        self.lblDescricaoValor.setStyleSheet("color:#1a3a5c;")
        self.lblDescricaoValor.setWordWrap(True)
        col1.addWidget(self.lblDescricaoValor)

        infoLayout.addLayout(col1, 2)

        col2 = QVBoxLayout()
        col2.setSpacing(6)

        self.lblPrecoTitulo = QLabel("Preco do Kit:", self.frameInfo)
        self.lblPrecoTitulo.setStyleSheet("font-weight:bold;color:#46627d;")
        col2.addWidget(self.lblPrecoTitulo)

        self.lblPrecoValor = QLabel("R$ 0,00", self.frameInfo)
        self.lblPrecoValor.setStyleSheet("font-size:16px;color:#27ae60;font-weight:bold;")
        col2.addWidget(self.lblPrecoValor)

        self.lblEstoqueTitulo = QLabel("Estoque:", self.frameInfo)
        self.lblEstoqueTitulo.setStyleSheet("font-weight:bold;color:#46627d;")
        col2.addWidget(self.lblEstoqueTitulo)

        self.lblEstoqueValor = QLabel("0", self.frameInfo)
        self.lblEstoqueValor.setStyleSheet("font-size:14px;color:#1a3a5c;font-weight:bold;")
        col2.addWidget(self.lblEstoqueValor)

        self.lblStatusTitulo = QLabel("Status:", self.frameInfo)
        self.lblStatusTitulo.setStyleSheet("font-weight:bold;color:#46627d;")
        col2.addWidget(self.lblStatusTitulo)

        self.lblStatusValor = QLabel("-", self.frameInfo)
        self.lblStatusValor.setStyleSheet("font-size:12px;font-weight:bold;")
        col2.addWidget(self.lblStatusValor)

        infoLayout.addLayout(col2, 1)

        layout.addWidget(self.frameInfo)

        lblItensTitulo = QLabel("Itens do Kit", self)
        lblItensTitulo.setStyleSheet("font-size:14px;font-weight:bold;color:#14324c;")
        layout.addWidget(lblItensTitulo)

        self.tableItens = QTableWidget(self)
        self.tableItens.setColumnCount(5)
        self.tableItens.setHorizontalHeaderLabels(["Produto", "Codigo", "Preco Unit.", "Qtd.", "Subtotal"])
        self.tableItens.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableItens.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableItens.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tableItens.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tableItens.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tableItens.verticalHeader().setVisible(False)
        self.tableItens.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableItens.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableItens.setStyleSheet(
            "QTableWidget { border: 1px solid #c8d9ea; gridline-color: #dce8f0; }"
            "QHeaderView::section { background: #f0f6fc; color: #1a3a5c; font-weight: bold; border: none; border-right: 1px solid #dce8f0; border-bottom: 2px solid #3585c8; padding: 5px; }"
        )
        layout.addWidget(self.tableItens, 1)

        self.lblTotalComponentes = QLabel("Total dos componentes: R$ 0,00", self)
        self.lblTotalComponentes.setStyleSheet("font-size:12px;font-weight:bold;color:#1a3a5c;")
        layout.addWidget(self.lblTotalComponentes)

        botoesLayout = QHBoxLayout()
        botoesLayout.addStretch()
        self.btnFechar = QPushButton("Fechar", self)
        self.btnFechar.setStyleSheet(
            "QPushButton { background-color: #e8eef5; color: #274764; border: 1px solid #c5d6e4; border-radius: 6px; padding: 8px 20px; font-weight: bold; }"
            "QPushButton:hover { background: #dce8f4; }"
        )
        self.btnFechar.clicked.connect(self.accept)
        botoesLayout.addWidget(self.btnFechar)
        layout.addLayout(botoesLayout)

    def _carregar_dados(self) -> None:
        kit = KitService.buscar_por_id(self._kit_id)
        if not kit:
            return
        self._kit = kit

        self.lblNomeValor.setText(str(kit.get("nome") or "-"))
        self.lblDescricaoValor.setText(str(kit.get("descricao") or "Sem descricao"))
        self.lblPrecoValor.setText(formatar_moeda(kit.get("preco_kit")))
        self.lblEstoqueValor.setText(str(int(kit.get("quantidade_estoque") or 0)))

        ativo = str(kit.get("ativo") or "S").upper() == "S"
        self.lblStatusValor.setText("Ativo" if ativo else "Inativo")
        if ativo:
            self.lblStatusValor.setStyleSheet("font-size:12px;font-weight:bold;color:#27ae60;")
        else:
            self.lblStatusValor.setStyleSheet("font-size:12px;font-weight:bold;color:#e74c3c;")

        itens = KitService.listar_itens(self._kit_id)
        self._itens = itens
        self._preencher_tabela(itens)

    def _preencher_tabela(self, itens: list[dict[str, Any]]) -> None:
        self.tableItens.setRowCount(len(itens))
        total = 0.0
        for row, item in enumerate(itens):
            subtotal = float(item.get("subtotal") or 0)
            total += subtotal
            set_table_item(self.tableItens, row, 0, str(item.get("produto") or "-"))
            set_table_item(self.tableItens, row, 1, str(item.get("codigo_barras") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 2, formatar_moeda(item.get("preco_venda")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tableItens, row, 3, str(int(item.get("quantidade") or 0)), alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 4, formatar_moeda(subtotal), alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.lblTotalComponentes.setText(f"Total dos componentes: {formatar_moeda(total)}")
