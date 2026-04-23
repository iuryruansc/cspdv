from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt
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

    def _conectar_sinais(self) -> None:
        self.btnFechar.clicked.connect(self.reject)
        self.btnCancelar.clicked.connect(self.reject)
        self.btnBuscar.clicked.connect(self._buscar_produtos)
        self.btnConfirmar.clicked.connect(self._confirmar_selecao)
        self.lineEditBusca.returnPressed.connect(self._buscar_produtos)
        self.tableResultados.itemSelectionChanged.connect(self._atualizar_detalhes_selecao)
        self.tableResultados.itemDoubleClicked.connect(lambda _: self._confirmar_selecao())

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
