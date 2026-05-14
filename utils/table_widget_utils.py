from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


def set_table_item(
    table: QTableWidget,
    row: int,
    column: int,
    value: Any,
    *,
    alignment: Any = Qt.AlignLeft | Qt.AlignVCenter,
) -> QTableWidgetItem:
    item = QTableWidgetItem("" if value is None else str(value))
    item.setTextAlignment(int(alignment))
    table.setItem(row, column, item)
    return item
