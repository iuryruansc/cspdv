from __future__ import annotations

from typing import Any, Dict, List

from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QTableWidget, QTableWidgetItem

from core.session_manager import SessionManager
from ui.venda.modal_confirmacao_venda import Ui_ModalConfirmacaoVenda
from utils.format_utils import formatar_decimal, formatar_inteiro, formatar_moeda


class ConfirmarVendaDialog(QDialog, Ui_ModalConfirmacaoVenda):
    lblTitulo: QLabel
    lblNumVendaLabel: QLabel
    lblNumVendaValor: QLabel
    lblClienteLabel: QLabel
    lblClienteValor: QLabel
    lblOperadorLabel: QLabel
    lblOperadorValor: QLabel
    lblDataHoraLabel: QLabel
    lblDataHoraValor: QLabel
    lblItensHeader: QLabel
    lblQtdItensLabel: QLabel
    lblQtdItensValor: QLabel
    lblSubtotalLabel: QLabel
    lblSubtotalValor: QLabel
    lblDescontoLabel: QLabel
    lblDescontoValor: QLabel
    lblTotalLabel: QLabel
    lblTotalValor: QLabel
    lblAvisoVazio: QLabel
    btnFechar: QPushButton
    btnVoltarCorrigir: QPushButton
    btnConfirmarPagamento: QPushButton
    tableResumoItens: QTableWidget

    def __init__(
        self,
        *,
        numero_venda: int,
        cliente_nome: str,
        itens_venda: List[Dict[str, Any]],
        subtotal: float,
        desconto_total: float,
        total: float,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self._numero_venda = numero_venda
        self._cliente_nome = cliente_nome
        self._itens_venda = itens_venda
        self._subtotal = subtotal
        self._desconto_total = desconto_total
        self._total = total
        self._configurar_interface()
        self._popular_dados()

    def _configurar_interface(self) -> None:
        self.setWindowTitle("CSPdv - Confirmar Venda")
        self.setStyleSheet(
            """
            QDialog {
                background-color: #eef4f8;
            }
            QLabel#lblTitulo {
                color: #ffffff;
                font-weight: 800;
            }
            QFrame#frameHeader {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #153552, stop:0.55 #1d4c74, stop:1 #2f75b0);
                border-radius: 10px;
            }
            QFrame#frameDadosVenda,
            QFrame#frameResumo,
            QFrame#frameRodape {
                background-color: #ffffff;
                border: 1px solid #d6e2ec;
                border-radius: 10px;
            }
            QFrame#frameTotal {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1d5b95, stop:1 #2f75b0);
                border: none;
                border-radius: 12px;
            }
            QLabel {
                color: #16324f;
            }
            QLabel#lblTotalLabel,
            QLabel#lblTotalValor {
                color: white;
                font-weight: 800;
            }
            QLabel#lblAvisoVazio {
                color: #946200;
                background-color: #fff4d6;
                border: 1px solid #f1d48b;
                border-radius: 8px;
                padding: 8px 10px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dbe7f0;
                border-radius: 10px;
                gridline-color: #e6eef5;
                color: #16324f;
            }
            QHeaderView::section {
                background-color: #f2f7fb;
                color: #315676;
                font-size: 11px;
                font-weight: 700;
                border: none;
                border-right: 1px solid #dce7ef;
                border-bottom: 1px solid #dce7ef;
                padding: 8px;
            }
            QPushButton#btnVoltarCorrigir {
                background-color: #edf3f8;
                color: #16324f;
                border: 1px solid #c8d8e8;
                border-radius: 8px;
                font-weight: 700;
                padding: 8px 14px;
            }
            QPushButton#btnVoltarCorrigir:hover {
                background-color: #e3edf6;
            }
            QPushButton#btnConfirmarPagamento {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #53b45b, stop:1 #389643);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 800;
                padding: 8px 14px;
            }
            QPushButton#btnConfirmarPagamento:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #62c26a, stop:1 #40a24c);
            }
            """
        )
        self.lblTitulo.setText("Confirmar Venda  -  F4")
        self.btnFechar.setText("x")
        self.lblNumVendaLabel.setText("Venda n°")
        self.lblClienteLabel.setText("Cliente")
        self.lblOperadorLabel.setText("Operador")
        self.lblDataHoraLabel.setText("Data / Hora")
        self.lblItensHeader.setText("Itens da Venda")
        self.lblQtdItensLabel.setText("Qtd. de itens:")
        self.lblSubtotalLabel.setText("Subtotal:")
        self.lblDescontoLabel.setText("Desconto:")
        self.lblTotalLabel.setText("TOTAL A PAGAR")
        self.lblAvisoVazio.setText("Nenhum item adicionado. Adicione produtos antes de confirmar.")
        self.btnVoltarCorrigir.setText("Voltar e Corrigir")
        self.btnConfirmarPagamento.setText("Confirmar e Pagar  (Enter)")

        self.tableResumoItens.verticalHeader().setVisible(False)
        self.tableResumoItens.horizontalHeader().setStretchLastSection(True)
        self.tableResumoItens.setAlternatingRowColors(True)
        self.tableResumoItens.setHorizontalHeaderLabels(
            ["Código", "Descrição", "Qtd.", "Vl. Unit.", "Subtotal"]
        )

    def _popular_dados(self) -> None:
        self.lblNumVendaValor.setText(str(self._numero_venda))
        self.lblClienteValor.setText(self._cliente_nome or "Consumidor Final")
        self.lblOperadorValor.setText(self._nome_operador())
        self.lblDataHoraValor.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm"))
        self.lblQtdItensValor.setText(
            formatar_inteiro(sum(int(item.get("quantidade") or 0) for item in self._itens_venda))
        )
        self.lblSubtotalValor.setText(formatar_moeda(self._subtotal))
        self.lblDescontoValor.setText(formatar_moeda(self._desconto_total))
        self.lblTotalValor.setText(formatar_moeda(self._total))
        self.btnConfirmarPagamento.setEnabled(bool(self._itens_venda))
        self.lblAvisoVazio.setVisible(not self._itens_venda)
        self._popular_itens()

    def _popular_itens(self) -> None:
        self.tableResumoItens.setRowCount(len(self._itens_venda))
        for row, item in enumerate(self._itens_venda):
            valores = (
                str(item.get("codigo_barras") or ""),
                str(item.get("nome") or ""),
                formatar_inteiro(item.get("quantidade") or 0),
                formatar_decimal(item.get("preco_venda") or 0.0),
                formatar_decimal(item.get("total") or 0.0),
            )
            for col, valor in enumerate(valores):
                table_item = QTableWidgetItem(valor)
                if col in (2, 3, 4):
                    table_item.setTextAlignment(int(Qt.AlignRight | Qt.AlignVCenter))
                self.tableResumoItens.setItem(row, col, table_item)

    @staticmethod
    def _nome_operador() -> str:
        user = SessionManager.current_user() or {}
        return str(user.get("nome") or user.get("login") or user.get("username") or "OPERADOR")
