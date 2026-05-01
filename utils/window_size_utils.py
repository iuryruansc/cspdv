from PyQt5.QtCore import QSize
from PyQt5.QtGui import QCursor, QGuiApplication
from PyQt5.QtWidgets import QWidget


def aplicar_tamanho_proporcional_tela(
    widget: QWidget,
    *,
    proporcao_largura: float = 0.9,
    proporcao_altura: float = 0.88,
    margem: int = 40,
) -> None:
    screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
    if screen is None:
        return

    area = screen.availableGeometry()
    largura_alvo = max(640, int(area.width() * proporcao_largura))
    altura_alvo = max(480, int(area.height() * proporcao_altura))
    largura_alvo = min(largura_alvo, max(640, area.width() - margem))
    altura_alvo = min(altura_alvo, max(480, area.height() - margem))

    minimo_atual = widget.minimumSize()
    largura_minima = min(minimo_atual.width(), largura_alvo) if minimo_atual.width() > 0 else 0
    altura_minima = min(minimo_atual.height(), altura_alvo) if minimo_atual.height() > 0 else 0

    if largura_minima > 0 or altura_minima > 0:
        widget.setMinimumSize(QSize(max(0, largura_minima), max(0, altura_minima)))

    widget.resize(max(largura_alvo, largura_minima), max(altura_alvo, altura_minima))
