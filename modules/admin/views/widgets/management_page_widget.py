from __future__ import annotations
from typing import Any, Callable, Iterable

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QFrame, QHeaderView, QLabel, QPushButton, QWidget

from ui.admin.management_page_widget import Ui_ManagementPageWidget
from utils.table_widget_utils import set_table_item

class ManagementPageWidget(QFrame, Ui_ManagementPageWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._rows: list[dict[str, Any]] = []
        self._columns: list[tuple[str, str]] = []
        self._displayed_rows: list[dict[str, Any]] = []
        self._details_allowed = False
        self._client_accounts_allowed = False
        self._edit_allowed = False
        self._toggle_allowed = False
        self._quantity_adjustment_allowed = False
        self._ignore_search = False
        self._remote_search_callback: Callable[[str], None] | None = None
        self._pagination_callback: Callable[[int], None] | None = None
        self._pagination_page = 0
        self._pagination_total = 0
        self._pagination_size = 100

        self.setupUi(self)
        self._remote_search_timer = QTimer(self)
        self._remote_search_timer.setSingleShot(True)
        self._remote_search_timer.setInterval(250)
        self._remote_search_timer.timeout.connect(self._emit_remote_search)
        self.lineEditBusca.textChanged.connect(self._on_search_changed)
        self.tableResultados.itemSelectionChanged.connect(self._update_action_states)

        self.btnPaginaAnterior = QPushButton("Anterior", self)
        self.btnPaginaAnterior.setProperty("toolbarButton", True)
        self.btnPaginaAnterior.clicked.connect(self._pagina_anterior)
        self.footerLayout.insertWidget(1, self.btnPaginaAnterior)
        self.lblPagina = QLabel("", self)
        self.lblPagina.setProperty("sectionHint", True)
        self.footerLayout.insertWidget(2, self.lblPagina)
        self.btnPaginaProxima = QPushButton("Próxima", self)
        self.btnPaginaProxima.setProperty("toolbarButton", True)
        self.btnPaginaProxima.clicked.connect(self._pagina_proxima)
        self.footerLayout.insertWidget(3, self.btnPaginaProxima)
        self._atualizar_controles_paginacao()

    def configure(self, title: str, hint: str, columns: Iterable[tuple[str, str]], rows: list[dict[str, Any]]) -> None:
        self.lblTitle.setText(title)
        self.lblHint.setText(hint)
        self._columns = list(columns)
        self._rows = rows
        self._ignore_search = True
        self.lineEditBusca.clear()
        self._ignore_search = False
        self._pagination_callback = None
        self._pagination_total = 0
        self._atualizar_controles_paginacao()
        self._populate_table(rows)

    def replace_rows(self, rows: list[dict[str, Any]]) -> None:
        self._populate_table(rows)

    def set_remote_search_callback(self, callback: Callable[[str], None] | None) -> None:
        self._remote_search_callback = callback

    def search_text(self) -> str:
        return self.lineEditBusca.text().strip()

    def set_loading(self, loading: bool) -> None:
        if loading:
            self.lblResumo.setText("Carregando produtos...")
        elif not self._pagination_callback:
            self.lblResumo.setText("Nenhum registro carregado.")

    def set_pagination(
        self,
        *,
        page: int,
        total: int,
        page_size: int,
        callback: Callable[[int], None],
    ) -> None:
        self._pagination_page = max(0, int(page))
        self._pagination_total = max(0, int(total))
        self._pagination_size = max(1, int(page_size))
        self._pagination_callback = callback
        self._atualizar_controles_paginacao()
        self._atualizar_resumo_paginacao()

    def set_quantity_adjustment_enabled(self, visible: bool) -> None:
        self._quantity_adjustment_allowed = visible
        self.btnAjustarQuantidade.setVisible(visible)
        self._update_action_states()

    def set_details_enabled(self, enabled: bool) -> None:
        self._details_allowed = enabled
        self.btnDetalhes.setVisible(enabled)
        self._update_action_states()

    def set_client_accounts_enabled(self, enabled: bool) -> None:
        self._client_accounts_allowed = enabled
        self.btnContasCliente.setVisible(enabled)
        self._update_action_states()

    def set_edit_enabled(self, enabled: bool) -> None:
        self._edit_allowed = enabled
        self.btnEditar.setVisible(enabled)
        self._update_action_states()

    def set_toggle_enabled(self, enabled: bool) -> None:
        self._toggle_allowed = enabled
        self.btnToggleAtivo.setVisible(enabled)
        self._update_action_states()

    def selected_row(self) -> dict[str, Any] | None:
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

    def _on_search_changed(self, text: str) -> None:
        if self._ignore_search:
            return
        if self._remote_search_callback is not None:
            self._remote_search_timer.start()
            return
        self._apply_filter(text)

    def _emit_remote_search(self) -> None:
        if self._remote_search_callback is not None:
            self._remote_search_callback(self.search_text())

    def _pagina_anterior(self) -> None:
        if self._pagination_callback and self._pagination_page > 0:
            self._pagination_callback(self._pagination_page - 1)

    def _pagina_proxima(self) -> None:
        ultima_pagina = max(0, (self._pagination_total - 1) // self._pagination_size)
        if self._pagination_callback and self._pagination_page < ultima_pagina:
            self._pagination_callback(self._pagination_page + 1)

    def _atualizar_controles_paginacao(self) -> None:
        visivel = self._pagination_callback is not None and self._pagination_total > self._pagination_size
        self.btnPaginaAnterior.setVisible(visivel)
        self.lblPagina.setVisible(visivel)
        self.btnPaginaProxima.setVisible(visivel)
        self.btnPaginaAnterior.setEnabled(visivel and self._pagination_page > 0)
        ultima_pagina = max(0, (self._pagination_total - 1) // self._pagination_size)
        self.btnPaginaProxima.setEnabled(visivel and self._pagination_page < ultima_pagina)
        if visivel:
            self.lblPagina.setText(f"Página {self._pagination_page + 1} de {ultima_pagina + 1}")
        else:
            self.lblPagina.clear()

    def _atualizar_resumo_paginacao(self) -> None:
        if self._pagination_callback is None:
            return
        inicio = self._pagination_page * self._pagination_size + 1 if self._pagination_total else 0
        fim = min((self._pagination_page + 1) * self._pagination_size, self._pagination_total)
        self.lblResumo.setText(f"{inicio}-{fim} de {self._pagination_total} registro(s).")

    def _populate_table(self, rows: list[dict[str, Any]]) -> None:
        self._displayed_rows = list(rows)
        self.tableResultados.setColumnCount(len(self._columns))
        self.tableResultados.setHorizontalHeaderLabels([label for _, label in self._columns])
        self.tableResultados.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for col_index, (field, _) in enumerate(self._columns):
                value = row.get(field, "")
                item = set_table_item(self.tableResultados, row_index, col_index, value)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)

        self._apply_column_resize_policy()
        if self._pagination_callback:
            self._atualizar_resumo_paginacao()
        else:
            self.lblResumo.setText(f"{len(rows)} registro(s) exibido(s).")
        self.tableResultados.clearSelection()
        self._update_action_states()

    def _update_action_states(self) -> None:
        has_selection = self.selected_row() is not None
        self.btnDetalhes.setEnabled(self._details_allowed and has_selection)
        self.btnContasCliente.setEnabled(self._client_accounts_allowed and has_selection)
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
