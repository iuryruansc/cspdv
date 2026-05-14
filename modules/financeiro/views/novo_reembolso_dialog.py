from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QButtonGroup, QDialog, QSpinBox

from ui.financeiro.novo_reembolso_dialog import Ui_NovoReembolsoDialog
from utils.format_utils import formatar_data_hora, formatar_moeda
from utils.table_widget_utils import set_table_item
from utils.ui_messages import mostrar_aviso

class NovoReembolsoDialog(QDialog, Ui_NovoReembolsoDialog):
    def __init__(self, detalhes_venda: Dict[str, Any], parent=None):
        super().__init__(parent)
        self._detalhes = detalhes_venda
        self._venda = detalhes_venda.get("venda") or {}
        self._itens = detalhes_venda.get("itens") or []
        self.resultado: Dict[str, Any] | None = None

        self.setupUi(self)
        self.setWindowTitle(f"Novo Reembolso - Venda #{self._venda.get('id') or '-'}")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.groupTipo = QButtonGroup(self)
        self.groupTipo.addButton(self.radioTotal)
        self.groupTipo.addButton(self.radioParcial)
        self.radioTotal.toggled.connect(self._atualizar_modo)
        self.radioParcial.toggled.connect(self._atualizar_modo)
        self.btnCancelar.clicked.connect(self.reject)
        self.btnConfirmar.clicked.connect(self._confirmar)

        self._populate()
        self._atualizar_modo()
        self._recalcular_total()

    def _populate(self) -> None:
        self.lblHeaderTitulo.setText(f"Reembolso da Venda #{self._venda.get('id') or '-'}")
        self.lblCliente.setText(str(self._venda.get("cliente") or "Consumidor Final"))
        self.lblDataHora.setText(formatar_data_hora(self._venda.get("data_hora")))
        self.lblTotalVenda.setText(formatar_moeda(self._venda.get("valor_total")))
        self.lblStatus.setText(str(self._venda.get("status") or "-"))

        self.tableItens.setRowCount(len(self._itens))
        for row, item in enumerate(self._itens):
            quantidade_disponivel = int(item.get("quantidade_disponivel") or 0)
            total_item = Decimal(str(item.get("total_item") or 0))

            set_table_item(self.tableItens, row, 0, str(item.get("codigo_barras") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 1, str(item.get("produto") or "-"))
            set_table_item(self.tableItens, row, 2, str(quantidade_disponivel), alignment=Qt.AlignCenter)

            spin = QSpinBox(self.tableItens)
            spin.setMinimum(0)
            spin.setMaximum(quantidade_disponivel)
            spin.setValue(quantidade_disponivel if self.radioTotal.isChecked() else 0)
            spin.valueChanged.connect(self._recalcular_total)
            self.tableItens.setCellWidget(row, 3, spin)

            set_table_item(self.tableItens, row, 4, formatar_moeda(item.get("preco_unitario")), alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tableItens, row, 5, formatar_moeda(total_item), alignment=Qt.AlignRight | Qt.AlignVCenter)

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

