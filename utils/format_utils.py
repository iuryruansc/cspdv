from PyQt5.QtCore import QEvent, QObject, QSignalBlocker, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QLineEdit

from utils.currency_runtime import simbolo_moeda_padrao
from utils.string_utils import somente_digitos, texto_limpo

def numero_decimal(valor: object) -> float:
    if valor in (None, ""):
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)

    texto = texto_limpo(str(valor))
    if not texto:
        return 0.0

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except (TypeError, ValueError):
        return 0.0

def formatar_decimal(valor: object, casas: int = 2) -> str:
    return f"{numero_decimal(valor):.{casas}f}".replace(".", ",")

def formatar_moeda(valor: object) -> str:
    texto = f"{numero_decimal(valor):,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{simbolo_moeda_padrao()} {texto}"

def formatar_inteiro(valor: object) -> str:
    return str(int(numero_decimal(valor)))

def formatar_cpf_cnpj(valor: str) -> str:
    digits = somente_digitos(valor)
    if len(digits) == 11:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    if len(digits) == 14:
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
    return digits

def formatar_telefone(valor: str) -> str:
    digits = somente_digitos(valor)
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    return texto_limpo(valor)

def formatar_cep(valor: str) -> str:
    digits = somente_digitos(valor)
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    return digits

def formatar_moeda_input(valor: object) -> str:
    digits = somente_digitos("" if valor is None else str(valor))
    if not digits:
        digits = "0"

    inteiro = int(digits)
    return f"{inteiro / 100:.2f}".replace(".", ",")

class _MoneyInputFilter(QObject):
    def eventFilter(self, a0, a1) -> bool:
        if not isinstance(a0, QLineEdit):
            return False

        if a1.type() in (QEvent.FocusIn, QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
            a0.setCursorPosition(len(a0.text()))

        if a1.type() == QEvent.KeyPress and isinstance(a1, QKeyEvent):
            if a1.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Home):
                a0.setCursorPosition(len(a0.text()))
                return True

        return False

def aplicar_mascara_monetaria(line_edit: QLineEdit) -> None:
    def _ao_editar(texto: str) -> None:
        formatado = formatar_moeda_input(texto)
        if line_edit.text() == formatado:
            return

        with QSignalBlocker(line_edit):
            line_edit.setText(formatado)
        line_edit.setCursorPosition(len(formatado))

    filtro = _MoneyInputFilter(line_edit)
    line_edit.installEventFilter(filtro)
    setattr(line_edit, "_money_input_filter", filtro)
    line_edit.textEdited.connect(_ao_editar)
