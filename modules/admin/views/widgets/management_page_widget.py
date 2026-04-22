from typing import Any, Dict, Iterable, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ManagementPageWidget(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._rows: List[Dict[str, Any]] = []
        self._columns: List[tuple[str, str]] = []
        self._displayed_rows: List[Dict[str, Any]] = []

        self.setObjectName("frameManagementPage")
        self.setStyleSheet(
            """
            QFrame#frameManagementPage {
                background-color: white;
                border: 1px solid #a8c4d8;
                border-radius: 6px;
            }
            QLabel[sectionTitle="true"] {
                color: #1a3a5c;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel[sectionHint="true"] {
                color: #5d7f99;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #f7fbff;
                border: 1px solid #c5d8e6;
                border-radius: 4px;
                padding: 7px 10px;
                font-size: 12px;
            }
            QPushButton[toolbarButton="true"] {
                background-color: #f0f6fc;
                color: #1a3a5c;
                border: 1px solid #c0d8ec;
                border-radius: 4px;
                padding: 7px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton[toolbarButton="true"]:hover {
                background-color: #dceaf4;
                border-color: #3585c8;
                color: #1a5fa0;
            }
            QPushButton[primaryButton="true"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3585c8, stop:1 #1a5fa0);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton[primaryButton="true"]:hover {
                background: #2a74b8;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #d6e3ee;
                border-radius: 4px;
                font-size: 12px;
                gridline-color: #dce8f0;
            }
            QHeaderView::section {
                background-color: #f0f6fc;
                color: #1a3a5c;
                font-size: 11px;
                font-weight: bold;
                padding: 5px 6px;
                border: none;
                border-right: 1px solid #dce8f0;
                border-bottom: 2px solid #3585c8;
            }
            """
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        self.lblTitle = QLabel("Gerenciamento")
        self.lblTitle.setProperty("sectionTitle", True)
        self.lblHint = QLabel("Selecione um cadastro para consultar e abrir acoes rapidas.")
        self.lblHint.setProperty("sectionHint", True)
        self.lblHint.setWordWrap(True)
        header_layout.addWidget(self.lblTitle)
        header_layout.addWidget(self.lblHint)
        root_layout.addLayout(header_layout)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(8)
        self.lineEditBusca = QLineEdit()
        self.lineEditBusca.setPlaceholderText("Buscar por qualquer coluna visivel...")
        self.lineEditBusca.textChanged.connect(self._apply_filter)

        self.btnNovo = QPushButton("Novo cadastro")
        self.btnNovo.setProperty("primaryButton", True)
        self.btnAtualizar = QPushButton("Atualizar")
        self.btnAtualizar.setProperty("toolbarButton", True)
        self.btnEditar = QPushButton("Editar")
        self.btnEditar.setProperty("toolbarButton", True)
        self.btnEditar.setEnabled(False)
        self.btnEditar.setToolTip("A edicao inline sera adicionada na proxima etapa.")
        self.btnAjustarQuantidade = QPushButton("Ajustar Quantidade")
        self.btnAjustarQuantidade.setProperty("toolbarButton", True)
        self.btnAjustarQuantidade.hide()
        self.btnToggleAtivo = QPushButton("Ativar / Desativar")
        self.btnToggleAtivo.setProperty("toolbarButton", True)
        self.btnToggleAtivo.setEnabled(False)
        self.btnToggleAtivo.setToolTip("A alteracao de status sera adicionada na proxima etapa.")

        toolbar_layout.addWidget(self.lineEditBusca, 1)
        toolbar_layout.addWidget(self.btnAtualizar)
        toolbar_layout.addWidget(self.btnEditar)
        toolbar_layout.addWidget(self.btnAjustarQuantidade)
        toolbar_layout.addWidget(self.btnToggleAtivo)
        toolbar_layout.addWidget(self.btnNovo)
        root_layout.addLayout(toolbar_layout)

        self.tableResultados = QTableWidget()
        self.tableResultados.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableResultados.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableResultados.setSelectionMode(QTableWidget.SingleSelection)
        self.tableResultados.verticalHeader().setVisible(False)
        header = self.tableResultados.horizontalHeader()
        header.setStretchLastSection(False)
        root_layout.addWidget(self.tableResultados, 1)

        footer_layout = QHBoxLayout()
        self.lblResumo = QLabel("Nenhum registro carregado.")
        self.lblResumo.setProperty("sectionHint", True)
        footer_layout.addWidget(self.lblResumo)
        footer_layout.addStretch()
        root_layout.addLayout(footer_layout)

    def configure(self, title: str, hint: str, columns: Iterable[tuple[str, str]], rows: List[Dict[str, Any]]) -> None:
        self.lblTitle.setText(title)
        self.lblHint.setText(hint)
        self._columns = list(columns)
        self._rows = rows
        self.lineEditBusca.clear()
        self._populate_table(rows)

    def set_quantity_adjustment_enabled(self, visible: bool) -> None:
        self.btnAjustarQuantidade.setVisible(visible)

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
            row
            for row in self._rows
            if any(filtro in str(value or "").casefold() for value in row.values())
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

    def _apply_column_resize_policy(self) -> None:
        header = self.tableResultados.horizontalHeader()
        compact_fields = {
            "id",
            "id_fornecedor",
            "ativo",
            "estado",
            "uf",
            "quantidade_estoque",
            "preco_venda",
        }
        stretch_fields = {
            "nome",
            "nome_marca",
            "nome_fantasia",
            "categoria",
            "marca",
            "fornecedor",
            "codigo_barras",
            "cnpj_cpf",
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
