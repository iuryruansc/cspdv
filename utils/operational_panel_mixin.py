from typing import Protocol, cast

from PyQt5.QtCore import QDateTime, QTimer
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget

from core.session_manager import SessionManager
from utils.window_size_utils import aplicar_tamanho_proporcional_tela


class _PainelOperacionalHost(Protocol):
    lblOperadorInfo: QLabel
    btnVoltarSelecao: QPushButton

    def hide(self) -> None: ...


class PainelOperacionalMixin:
    def _configurar_tamanho_responsivo(self) -> None:
        aplicar_tamanho_proporcional_tela(cast(QWidget, self))

    def _configurar_operador(self) -> None:
        host = cast(_PainelOperacionalHost, self)
        usuario = SessionManager.current_user()
        if usuario:
            nome = str(usuario.get("nome", "Operador")).upper()
            host.lblOperadorInfo.setText(f"Operador: {nome}")
            return
        host.lblOperadorInfo.setText("Operador: Nao logado")

    def _configurar_relogio(self) -> None:
        if not isinstance(getattr(self, "lblDataHora", None), QLabel):
            return
        self._atualizar_data_hora()
        self.timer = QTimer(cast(QWidget, self))
        self.timer.timeout.connect(self._atualizar_data_hora)
        self.timer.start(1000)

    def _atualizar_data_hora(self) -> None:
        label = getattr(self, "lblDataHora", None)
        if isinstance(label, QLabel):
            current = QDateTime.currentDateTime()
            label.setText(current.toString("dd/MM/yyyy  hh:mm:ss"))

    def _conectar_retorno_selecao(self) -> None:
        host = cast(_PainelOperacionalHost, self)
        host.btnVoltarSelecao.clicked.connect(self._voltar_para_selecao)

    def _voltar_para_selecao(self) -> None:
        from modules.auth.views.selecao_modo_view import SelecaoModoView

        host = cast(_PainelOperacionalHost, self)
        host.hide()
        self.selecao = SelecaoModoView()
        self.selecao.show()
