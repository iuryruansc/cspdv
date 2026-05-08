from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QColor, QBrush, QKeyEvent
from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem

from modules.produtos.services.produto_service import ProdutoService
from utils.format_utils import formatar_moeda

from ui.venda.modal_consulta_produto import Ui_ModalConsultaProduto

class ModalConsultaProdutoView(QDialog, Ui_ModalConsultaProduto):
    lineEditBusca: QLineEdit
    btnBuscar: QPushButton
    btnCancelar: QPushButton
    btnConfirmar: QPushButton
    tableResultados: QTableWidget
    lblInfoCodValor: QLabel
    lblInfoDescValor: QLabel
    lblInfoEstoqueValor: QLabel
    lblInfoPrecoValor: QLabel

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.produto_selecionado: Optional[Dict[str, Any]] = None
        self._resultados: List[Dict[str, Any]] = []
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self._normalizar_estilos()
        self._conectar_sinais()
        self.lineEditBusca.installEventFilter(self)
        self.tableResultados.installEventFilter(self)
        self.lineEditBusca.setFocus()

    def _normalizar_estilos(self) -> None:
        widgets = (
            self,
            self.frameTitleBar,
            self.frameConteudo,
            self.lineEditBusca,
            self.btnBuscar,
            self.lblResultadosHeader,
            self.tableResultados,
            self.frameInfoProduto,
            self.btnCancelar,
            self.btnConfirmar,
        )
        for widget in widgets:
            widget.setStyleSheet(widget.styleSheet().replace("{{", "{").replace("}}", "}"))
        self.tableResultados.horizontalHeader().setStyleSheet(
            "QHeaderView::section {"
            "background-color: #ffffff;"
            "color: #0f2740;"
            "font-size: 12px;"
            "font-weight: 700;"
            "border: none;"
            "border-right: 1px solid #d7e4ef;"
            "border-bottom: 2px solid #2f79c8;"
            "padding: 4px 6px;"
            "}"
        )
        self.tableResultados.verticalHeader().setStyleSheet(
            "QHeaderView::section {"
            "background-color: #ffffff;"
            "color: #0f2740;"
            "font-size: 11px;"
            "font-weight: 700;"
            "border: none;"
            "border-bottom: 1px solid #d7e4ef;"
            "border-right: 1px solid #d7e4ef;"
            "}"
        )
        self.tableResultados.horizontalHeader().setHighlightSections(False)
        self.tableResultados.verticalHeader().setHighlightSections(False)
        self._aplicar_cores_headers()
        self.btnBuscar.setDefault(False)
        self.btnBuscar.setAutoDefault(False)
        self.btnCancelar.setDefault(False)
        self.btnCancelar.setAutoDefault(False)
        self.btnConfirmar.setDefault(False)
        self.btnConfirmar.setAutoDefault(False)

    def _conectar_sinais(self) -> None:
        self.btnFechar.clicked.connect(self.reject)
        self.btnCancelar.clicked.connect(self.reject)
        self.btnBuscar.clicked.connect(self._buscar_produtos)
        self.btnConfirmar.clicked.connect(self._confirmar_selecao)
        self.tableResultados.itemSelectionChanged.connect(self._atualizar_detalhes_selecao)
        self.tableResultados.itemDoubleClicked.connect(lambda _: self._confirmar_selecao())

    def eventFilter(self, a0, a1) -> bool:
        if a1.type() == QEvent.KeyPress and isinstance(a1, QKeyEvent):
            key_event = a1
            if a0 is self.lineEditBusca and key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self._buscar_produtos()
                return True
            if a0 is self.tableResultados and key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self._confirmar_selecao()
                return True
        return super().eventFilter(a0, a1)

    def _buscar_produtos(self) -> None:
        termo = self.lineEditBusca.text().strip()
        self._resultados = ProdutoService.buscar_para_venda(termo)
        self.tableResultados.setRowCount(len(self._resultados))
        self.produto_selecionado = None

        for row, produto in enumerate(self._resultados):
            valores = (
                str(produto.get("codigo_barras") or ""),
                str(produto.get("nome") or ""),
                str(produto.get("unidade") or "-"),
                str(int(float(produto.get("quantidade_estoque") or 0))),
                formatar_moeda(float(produto.get("preco_venda") or 0)),
            )
            for col, valor in enumerate(valores):
                item = QTableWidgetItem(valor)
                if col in (3, 4):
                    item.setTextAlignment(int(Qt.AlignRight | Qt.AlignVCenter))
                self.tableResultados.setItem(row, col, item)

        if self._resultados:
            self.tableResultados.selectRow(0)
            self._atualizar_detalhes_selecao()
        else:
            self._limpar_detalhes()

        self._aplicar_cores_headers()

    def _atualizar_detalhes_selecao(self) -> None:
        row = self.tableResultados.currentRow()
        if row < 0 or row >= len(self._resultados):
            self.produto_selecionado = None
            self._limpar_detalhes()
            return

        produto = self._resultados[row]
        self.produto_selecionado = produto
        self.lblInfoCodValor.setText(str(produto.get("codigo_barras") or "-"))
        self.lblInfoDescValor.setText(str(produto.get("nome") or "-"))
        self.lblInfoEstoqueValor.setText(str(int(float(produto.get("quantidade_estoque") or 0))))
        self.lblInfoPrecoValor.setText(formatar_moeda(float(produto.get("preco_venda") or 0)))

    def _confirmar_selecao(self) -> None:
        self._atualizar_detalhes_selecao()
        if self.produto_selecionado is None:
            return
        self.accept()

    def _limpar_detalhes(self) -> None:
        self.lblInfoCodValor.setText("-")
        self.lblInfoDescValor.setText("-")
        self.lblInfoEstoqueValor.setText("-")
        self.lblInfoPrecoValor.setText("R$ -")

    def _aplicar_cores_headers(self) -> None:
        cor_header = QBrush(QColor("#0f2740"))
        for coluna in range(self.tableResultados.columnCount()):
            item = self.tableResultados.horizontalHeaderItem(coluna)
            if item is not None:
                item.setForeground(cor_header)
