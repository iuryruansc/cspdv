from typing import Iterable

from PyQt5.QtWidgets import QMessageBox, QWidget


def _criar_message_box(
    parent: QWidget,
    *,
    icon: QMessageBox.Icon,
    titulo: str,
    mensagem: str,
) -> QMessageBox:
    box = QMessageBox(parent)
    box.setIcon(icon)
    box.setWindowTitle(titulo)
    box.setText(mensagem)
    box.setStandardButtons(QMessageBox.Ok)
    box.setStyleSheet(
        """
        QMessageBox {
            background-color: #f4f8fc;
        }
        QMessageBox QLabel {
            color: #16324f;
            font-size: 13px;
            min-width: 240px;
        }
        QMessageBox QPushButton {
            min-width: 88px;
            min-height: 30px;
            padding: 4px 12px;
            border-radius: 6px;
            border: 1px solid #2d6ca8;
            background-color: #3b84cf;
            color: white;
            font-weight: bold;
        }
        QMessageBox QPushButton:hover {
            background-color: #2f72b4;
        }
        """
    )
    return box


def mostrar_aviso(parent: QWidget, titulo: str, mensagem: str) -> None:
    _criar_message_box(parent, icon=QMessageBox.Warning, titulo=titulo, mensagem=mensagem).exec_()


def mostrar_info(parent: QWidget, titulo: str, mensagem: str) -> None:
    _criar_message_box(parent, icon=QMessageBox.Information, titulo=titulo, mensagem=mensagem).exec_()


def mostrar_erro(parent: QWidget, titulo: str, mensagem: str) -> None:
    _criar_message_box(parent, icon=QMessageBox.Critical, titulo=titulo, mensagem=mensagem).exec_()


def confirmar_acao(
    parent: QWidget,
    titulo: str,
    mensagem: str,
    *,
    texto_confirmar: QMessageBox.StandardButton = QMessageBox.Yes,
    texto_cancelar: QMessageBox.StandardButton = QMessageBox.No,
    padrao: QMessageBox.StandardButton = QMessageBox.No,
) -> bool:
    botoes = QMessageBox.StandardButtons(texto_confirmar | texto_cancelar)
    resposta = QMessageBox.question(
        parent,
        titulo,
        mensagem,
        botoes,
        padrao,
    )
    return resposta == texto_confirmar


def mostrar_campos_invalidos(
    parent: QWidget,
    mensagens: Iterable[str],
    *,
    titulo: str = "Revise os campos",
    cabecalho: str = "Corrija os seguintes pontos:",
) -> None:
    itens = [mensagem for mensagem in mensagens if mensagem]
    if not itens:
        return
    QMessageBox.warning(parent, titulo, cabecalho + "\n" + "\n".join(itens))
