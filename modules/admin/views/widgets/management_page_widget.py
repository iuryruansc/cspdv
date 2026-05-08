from typing import Any, Dict, Iterable, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHeaderView, QTableWidgetItem, QWidget

from ui.admin.management_page_widget import Ui_ManagementPageWidget

class ManagementPageWidget(QFrame, Ui_ManagementPageWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._rows: List[Dict[str, Any]] = []
        self._columns: List[tuple[str, str]] = []
        self._displayed_rows: List[Dict[str, Any]] = []
        self._details_allowed = False
        self._edit_allowed = False
        self._toggle_allowed = False
        self._quantity_adjustment_allowed = False

        self.setupUi(self)
        self.lineEditBusca.textChanged.connect(self._apply_filter)
        self.tableResultados.itemSelectionChanged.connect(self._update_action_states)

    def configure(self, title: str, hint: str, columns: Iterable[tuple[str, str]], rows: List[Dict[str, Any]]) -> None:
        self.lblTitle.setText(title)
        self.lblHint.setText(hint)
        self._columns = list(columns)
        self._rows = rows
        self.lineEditBusca.clear()
        self._populate_table(rows)

    def set_quantity_adjustment_enabled(self, visible: bool) -> None:
        self._quantity_adjustment_allowed = visible
        self.btnAjustarQuantidade.setVisible(visible)
        self._update_action_states()

    def set_details_enabled(self, enabled: bool) -> None:
        self._details_allowed = enabled
        self.btnDetalhes.setVisible(enabled)
        self._update_action_states()

    def set_edit_enabled(self, enabled: bool) -> None:
        self._edit_allowed = enabled
        self._update_action_states()

    def set_toggle_enabled(self, enabled: bool) -> None:
        self._toggle_allowed = enabled
        self._update_action_states()

    def selected_row(self) -> Dict[str, Any] | None:
        current_row = self.tableResultados.currentRow()
        if current_row < 0 or current_row >= len(self._displayed_rows):
            return None
        return self._displayed_rows[current_row]

    def _apply_filter(self, text: str) -> None:
        filtro = text.strip().casefold()
        if not filtro:
            self._populate_table(self._rows)
            return

        filtered_rows = [
            row for row in self._rows if any(filtro in str(value or "").casefold() for value in row.values())
        ]
        self._populate_table(filtered_rows)

    def _populate_table(self, rows: List[Dict[str, Any]]) -> None:
        self._displayed_rows = list(rows)
        self.tableResultados.setColumnCount(len(self._columns))
        self.tableResultados.setHorizontalHeaderLabels([label for _, label in self._columns])
        self.tableResultados.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for col_index, (field, _) in enumerate(self._columns):
                value = row.get(field, "")
                item = QTableWidgetItem("" if value is None else str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.tableResultados.setItem(row_index, col_index, item)

        self._apply_column_resize_policy()
        self.lblResumo.setText(f"{len(rows)} registro(s) exibido(s).")
        self.tableResultados.clearSelection()
        self._update_action_states()

    def _update_action_states(self) -> None:
        has_selection = self.selected_row() is not None
        self.btnDetalhes.setEnabled(self._details_allowed and has_selection)
        self.btnEditar.setEnabled(self._edit_allowed and has_selection)
        self.btnToggleAtivo.setEnabled(self._toggle_allowed and has_selection)
        self.btnAjustarQuantidade.setEnabled(self._quantity_adjustment_allowed and has_selection)

    def _apply_column_resize_policy(self) -> None:
        header = self.tableResultados.horizontalHeader()
        compact_fields = {"id", "id_fornecedor", "ativo", "estado", "uf", "quantidade_estoque", "preco_venda"}
        stretch_fields = {
            "nome",
            "nome_marca",
            "nome_fantasia",
            "categoria",
            "marca",
            "fornecedor",
            "codigo_barras",
            "cnpj_cpf",
            "cpf",
            "telefone",
            "cidade",
        }

        for col_index, (field, _) in enumerate(self._columns):
            if field in compact_fields:
                header.setSectionResizeMode(col_index, QHeaderView.ResizeToContents)
                continue
            if field in stretch_fields:
                header.setSectionResizeMode(col_index, QHeaderView.Stretch)
                continue
            header.setSectionResizeMode(col_index, QHeaderView.Interactive)
            self.tableResultados.setColumnWidth(col_index, 140)
