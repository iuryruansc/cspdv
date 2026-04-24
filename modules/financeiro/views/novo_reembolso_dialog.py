from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from utils.format_utils import formatar_moeda
from utils.ui_messages import mostrar_aviso


class NovoReembolsoDialog(QDialog):
    def __init__(self, detalhes_venda: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._detalhes = detalhes_venda
        self._venda = detalhes_venda.get("venda") or {}
        self._itens = detalhes_venda.get("itens") or []
        self.resultado: Dict[str, Any] | None = None

        self.setWindowTitle(f"Novo Reembolso - Venda #{self._venda.get('id') or '-'}")
        self.setModal(True)
        self.resize(980, 760)
        self.setMinimumSize(940, 720)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet(
            """
QDialog { background: #eef5fb; }
QFrame[card="true"] { background: white; border: 1px solid #c8d8ea; border-radius: 14px; }
QLabel[title="true"] { color: #173a5f; font-size: 16px; font-weight: bold; }
QLabel[caption="true"] { color: #4c6b8b; font-size: 11px; font-weight: bold; }
QLabel[value="true"] { color: #173a5f; font-size: 18px; font-weight: bold; }
QTableWidget { background: white; border: 1px solid #c8d8ea; border-radius: 10px; gridline-color: #d9e6f2; color: #173a5f; }
QHeaderView::section { background: #e7f0f8; color: #1e4e79; padding: 8px; border: none; border-right: 1px solid #d1e0ee; border-bottom: 1px solid #d1e0ee; font-weight: bold; }
QLineEdit, QTextEdit { background: white; border: 1px solid #bcd0e4; border-radius: 10px; padding: 8px 10px; color: #173a5f; }
QRadioButton { color: #173a5f; font-weight: bold; }
QSpinBox { background: white; border: 1px solid #bcd0e4; border-radius: 8px; padding: 4px; color: #173a5f; }
QPushButton#btnConfirmar { background: #d9534f; color: white; border: none; border-radius: 10px; padding: 10px 20px; font-weight: bold; }
QPushButton#btnConfirmar:hover { background: #c64542; }
QPushButton#btnCancelar { background: #dfe9f3; color: #173a5f; border: 1px solid #c2d5e8; border-radius: 10px; padding: 10px 20px; font-weight: bold; }
QPushButton#btnCancelar:hover { background: #d1dfec; }
            """
        )

        self._build_ui()
        self._populate()
        self._atualizar_modo()
        self._recalcular_total()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        header = QFrame(self)
        header.setProperty("card", True)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 18, 18, 18)
        header_layout.setSpacing(12)

        title = QLabel(f"Reembolso da Venda #{self._venda.get('id') or '-'}", header)
        title.setProperty("title", True)
        header_layout.addWidget(title)

        info_row = QHBoxLayout()
        info_row.setSpacing(24)
        header_layout.addLayout(info_row)
        self.lblCliente = self._create_info_block(info_row, "CLIENTE")
        self.lblDataHora = self._create_info_block(info_row, "DATA / HORA")
        self.lblTotalVenda = self._create_info_block(info_row, "TOTAL DA VENDA")
        self.lblStatus = self._create_info_block(info_row, "STATUS")

        root.addWidget(header)

        mode_card = QFrame(self)
        mode_card.setProperty("card", True)
        mode_layout = QVBoxLayout(mode_card)
        mode_layout.setContentsMargins(18, 18, 18, 18)
        mode_layout.setSpacing(12)

        mode_title = QLabel("Tipo de Reembolso", mode_card)
        mode_title.setProperty("title", True)
        mode_layout.addWidget(mode_title)

        mode_row = QHBoxLayout()
        self.radioTotal = QRadioButton("Reembolso total", mode_card)
        self.radioParcial = QRadioButton("Reembolso parcial por item", mode_card)
        self.radioTotal.setChecked(True)
        self.groupTipo = QButtonGroup(self)
        self.groupTipo.addButton(self.radioTotal)
        self.groupTipo.addButton(self.radioParcial)
        self.radioTotal.toggled.connect(self._atualizar_modo)
        self.radioParcial.toggled.connect(self._atualizar_modo)
        mode_row.addWidget(self.radioTotal)
        mode_row.addWidget(self.radioParcial)
        mode_row.addStretch(1)
        mode_layout.addLayout(mode_row)

        self.tableItens = QTableWidget(self)
        self.tableItens.setColumnCount(6)
        self.tableItens.setHorizontalHeaderLabels(["Código", "Descrição", "Disponível", "Selecionada", "Vl. Unit.", "Total"])
        self.tableItens.verticalHeader().setVisible(False)
        self.tableItens.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableItens.horizontalHeader().setStretchLastSection(True)
        self.tableItens.horizontalHeader().setSectionResizeMode(1, self.tableItens.horizontalHeader().Stretch)
        mode_layout.addWidget(self.tableItens)

        root.addWidget(mode_card, 1)

        form_card = QFrame(self)
        form_card.setProperty("card", True)
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(10)

        form_title = QLabel("Justificativa", form_card)
        form_title.setProperty("title", True)
        form_layout.addWidget(form_title)

        self.inputMotivo = QLineEdit(form_card)
        self.inputMotivo.setPlaceholderText("Informe o motivo do reembolso")
        form_layout.addWidget(self.inputMotivo)

        self.inputObservacao = QTextEdit(form_card)
        self.inputObservacao.setPlaceholderText("Observações adicionais sobre o reembolso...")
        self.inputObservacao.setFixedHeight(88)
        form_layout.addWidget(self.inputObservacao)

        summary_row = QHBoxLayout()
        total_caption = QLabel("Valor a reembolsar", form_card)
        total_caption.setProperty("caption", True)
        self.lblTotalReembolso = QLabel("R$ 0,00", form_card)
        self.lblTotalReembolso.setProperty("value", True)
        summary_row.addWidget(total_caption)
        summary_row.addStretch(1)
        summary_row.addWidget(self.lblTotalReembolso)
        form_layout.addLayout(summary_row)

        root.addWidget(form_card)

        footer = QHBoxLayout()
        footer.addStretch(1)
        btn_cancelar = QPushButton("Cancelar", self)
        btn_cancelar.setObjectName("btnCancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_confirmar = QPushButton("Confirmar Reembolso", self)
        btn_confirmar.setObjectName("btnConfirmar")
        btn_confirmar.clicked.connect(self._confirmar)
        footer.addWidget(btn_cancelar)
        footer.addWidget(btn_confirmar)
        root.addLayout(footer)

    def _create_info_block(self, parent_layout: QHBoxLayout, caption: str) -> QLabel:
        block = QVBoxLayout()
        block.setSpacing(4)
        lbl_caption = QLabel(caption, self)
        lbl_caption.setProperty("caption", True)
        lbl_value = QLabel("-", self)
        lbl_value.setProperty("value", True)
        block.addWidget(lbl_caption)
        block.addWidget(lbl_value)
        parent_layout.addLayout(block, 1)
        return lbl_value

    def _populate(self) -> None:
        self.lblCliente.setText(str(self._venda.get("cliente") or "Consumidor Final"))
        self.lblDataHora.setText(self._formatar_data_hora(self._venda.get("data_hora")))
        self.lblTotalVenda.setText(formatar_moeda(self._venda.get("valor_total")))
        self.lblStatus.setText(str(self._venda.get("status") or "-"))

        self.tableItens.setRowCount(len(self._itens))
        for row, item in enumerate(self._itens):
            quantidade_disponivel = int(item.get("quantidade_disponivel") or 0)
            total_item = Decimal(str(item.get("total_item") or 0))

            self._set_item(row, 0, str(item.get("codigo_barras") or "-"), Qt.AlignCenter)
            self._set_item(row, 1, str(item.get("produto") or "-"))
            self._set_item(row, 2, str(quantidade_disponivel), Qt.AlignCenter)

            spin = QSpinBox(self.tableItens)
            spin.setMinimum(0)
            spin.setMaximum(quantidade_disponivel)
            spin.setValue(quantidade_disponivel if self.radioTotal.isChecked() else 0)
            spin.valueChanged.connect(self._recalcular_total)
            self.tableItens.setCellWidget(row, 3, spin)

            self._set_item(row, 4, formatar_moeda(item.get("preco_unitario")), Qt.AlignRight | Qt.AlignVCenter)
            self._set_item(row, 5, formatar_moeda(total_item), Qt.AlignRight | Qt.AlignVCenter)

    def _set_item(self, row: int, column: int, value: str, alignment: int = Qt.AlignLeft | Qt.AlignVCenter) -> None:
        item = QTableWidgetItem(value)
        item.setTextAlignment(int(alignment))
        self.tableItens.setItem(row, column, item)

    def _atualizar_modo(self) -> None:
        total = self.radioTotal.isChecked()
        for row in range(self.tableItens.rowCount()):
            spin = self.tableItens.cellWidget(row, 3)
            if isinstance(spin, QSpinBox):
                disponivel_item = self.tableItens.item(row, 2)
                quantidade_disponivel = int(disponivel_item.text()) if disponivel_item else 0
                spin.blockSignals(True)
                spin.setEnabled(not total)
                spin.setValue(quantidade_disponivel if total else min(spin.value(), quantidade_disponivel))
                if not total and spin.value() == quantidade_disponivel:
                    spin.setValue(0)
                spin.blockSignals(False)
        self._recalcular_total()

    def _recalcular_total(self) -> None:
        total = Decimal("0")
        for row, item in enumerate(self._itens):
            spin = self.tableItens.cellWidget(row, 3)
            if not isinstance(spin, QSpinBox):
                continue
            quantidade = spin.value()
            preco = Decimal(str(item.get("preco_unitario") or 0))
            total += Decimal(quantidade) * preco
        self.lblTotalReembolso.setText(formatar_moeda(total))

    def _itens_selecionados(self) -> List[Dict[str, Any]]:
        itens: List[Dict[str, Any]] = []
        for row, item in enumerate(self._itens):
            spin = self.tableItens.cellWidget(row, 3)
            if not isinstance(spin, QSpinBox):
                continue
            quantidade = spin.value()
            if quantidade <= 0:
                continue
            preco = Decimal(str(item.get("preco_unitario") or 0))
            itens.append(
                {
                    "item_venda_id": int(item.get("item_venda_id") or 0),
                    "produto_id": int(item.get("produto_id") or 0),
                    "lote_id": int(item.get("lote_id") or 0),
                    "codigo_barras": item.get("codigo_barras"),
                    "produto": item.get("produto"),
                    "quantidade": quantidade,
                    "valor_unitario": preco,
                    "valor_total": preco * Decimal(quantidade),
                }
            )
        return itens

    def _confirmar(self) -> None:
        motivo = self.inputMotivo.text().strip()
        if not motivo:
            mostrar_aviso(self, "Motivo obrigatório", "Informe o motivo do reembolso antes de continuar.")
            return

        itens = self._itens_selecionados()
        if not itens:
            mostrar_aviso(self, "Nenhum item selecionado", "Selecione ao menos um item para reembolso.")
            return

        valor_total = sum((item["valor_total"] for item in itens), Decimal("0"))
        self.resultado = {
            "venda_id": int(self._venda.get("id") or 0),
            "tipo": "TOTAL" if self.radioTotal.isChecked() else "PARCIAL",
            "motivo": motivo,
            "observacao": self.inputObservacao.toPlainText().strip(),
            "valor_total": valor_total,
            "itens": itens,
        }
        self.accept()

    @staticmethod
    def _formatar_data_hora(value: Any) -> str:
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y %H:%M")
        return "-"
