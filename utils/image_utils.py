from pathlib import Path
from typing import Any, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

from utils.runtime_paths import resolve_existing_path

def resolver_caminho_arquivo(caminho_relativo: Any) -> Optional[Path]:
    if not caminho_relativo:
        return None

    caminho = Path(str(caminho_relativo))
    if caminho.is_absolute():
        return caminho if caminho.exists() else None

    return resolve_existing_path(caminho)

def atualizar_preview_label(
    label: QLabel,
    imagem_path: Any,
    *,
    texto_padrao: str = "Sem imagem",
) -> Optional[Path]:
    caminho = resolver_caminho_arquivo(imagem_path)
    if not caminho or not caminho.exists():
        label.setPixmap(QPixmap())
        label.setText(texto_padrao)
        return None

    pixmap = QPixmap(str(caminho))
    if pixmap.isNull():
        label.setPixmap(QPixmap())
        label.setText(texto_padrao)
        return None

    label.setText("")
    label.setPixmap(
        pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
    )
    return caminho
