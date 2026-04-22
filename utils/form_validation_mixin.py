from __future__ import annotations

from typing import Protocol, TypeVar

from PyQt5.QtWidgets import QComboBox, QLineEdit

FieldWidget = QLineEdit | QComboBox
TWidget = TypeVar("TWidget", QLineEdit, QComboBox)

class _WidgetHost(Protocol):
    def findChildren(self, widget_type: type[TWidget]) -> list[TWidget]:
        ...

    def findChild(self, widget_type: type[TWidget], name: str) -> TWidget | None:
        ...

class ValidacaoFormMixin:
    def _host(self) -> _WidgetHost:
        return self  # type: ignore[return-value]

    def _inicializar_validacao(self) -> None:
        if not hasattr(self, "_estilos_originais"):
            self._estilos_originais: dict[str, str] = {}

    def registrar_estilos(self, widgets: list[FieldWidget]) -> None:
        self._inicializar_validacao()
        for widget in widgets:
            self._estilos_originais[widget.objectName()] = widget.styleSheet()

    def conectar_limpeza_em_tempo_real(
        self, widgets: list[FieldWidget] | None = None
    ) -> None:
        self._inicializar_validacao()
        host = self._host()

        if widgets is None:
            widgets = [
                widget
                for widget in host.findChildren(QLineEdit)
                if widget.objectName() != "lineEditCodigo"
            ] + list(host.findChildren(QComboBox))

        for widget in widgets:
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(
                    lambda _=None, current_widget=widget: self.limpar_erro_widget(current_widget)
                )
            else:
                widget.currentIndexChanged.connect(
                    lambda _=None, current_widget=widget: self.limpar_erro_widget(current_widget)
                )

    def marcar_invalido(self, widget: FieldWidget) -> None:
        self._inicializar_validacao()
        estilo_base = self._estilos_originais.get(widget.objectName()) or widget.styleSheet()
        sufixo_erro = "border:2px solid #d64545;background-color:#fff2f2;"

        if isinstance(widget, QLineEdit):
            widget.setStyleSheet(estilo_base + f"QLineEdit{{{sufixo_erro}}}")
        else:
            widget.setStyleSheet(estilo_base + f"QComboBox{{{sufixo_erro}}}")

    def limpar_erro_widget(self, widget: FieldWidget) -> None:
        self._inicializar_validacao()
        estilo_base = self._estilos_originais.get(widget.objectName())
        if estilo_base is not None:
            widget.setStyleSheet(estilo_base)

    def limpar_erros(self) -> None:
        self._inicializar_validacao()
        host = self._host()
        for nome, estilo in self._estilos_originais.items():
            widget = host.findChild(QLineEdit, nome)
            if widget is None:
                widget = host.findChild(QComboBox, nome)
            if widget is not None:
                widget.setStyleSheet(estilo)