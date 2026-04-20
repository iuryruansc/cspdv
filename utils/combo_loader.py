from PyQt5.QtWidgets import QComboBox

# Funções para carregar combos com dados do banco e obter o ID selecionado
def popular_combo(
    combo: QComboBox,
    itens: list[dict],
    placeholder: str = 'Selecione...',
    id_key: str = 'id',
    nome_key: str = 'nome',
) -> None:
    combo.blockSignals(True)
    combo.clear()
    combo.addItem(placeholder, None)

    for item in itens:
        combo.addItem(str(item[nome_key]), item[id_key])

    combo.setCurrentIndex(0)
    combo.blockSignals(False)


def combo_id(combo: QComboBox):
    return combo.currentData()