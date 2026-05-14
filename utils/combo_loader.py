from collections.abc import Mapping, Sequence
from typing import Any

from PyQt5.QtWidgets import QComboBox

ComboItem = Mapping[str, Any]

def popular_combo(
    combo: QComboBox,
    itens: Sequence[ComboItem],
    placeholder: str = "Selecione...",
    id_key: str = "id",
    nome_key: str = "nome",
) -> None:
    combo.blockSignals(True)
    combo.clear()
    combo.addItem(placeholder, None)

    for item in itens:
        combo.addItem(str(item[nome_key]), item[id_key])

    combo.setCurrentIndex(0)
    combo.blockSignals(False)

def combo_id(combo: QComboBox) -> Any:
    return combo.currentData()

def combo_int(combo: QComboBox) -> int | None:
    value = combo.currentData()
    if value in (None, "", 0, "0"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
