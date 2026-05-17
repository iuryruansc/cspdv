from __future__ import annotations

from typing import Dict, Optional

from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.auditoria.services.auditoria_service import AuditoriaService
from modules.auth.models.usuario_model import UsuarioModel
from utils.app_logger import log_info
from utils.ui_messages import mostrar_aviso


class TrocaOperadorDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._novo_operador: Optional[Dict[str, object]] = None
        self._caixa_atual = CaixaSession.current() or {}

        self.setWindowTitle("Troca de Operador")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.resize(520, 420)

        self._construir_ui()
        self._preencher_contexto()

    @property
    def novo_operador(self) -> Optional[Dict[str, object]]:
        return self._novo_operador

    def _construir_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #122c46;
            }
            QLabel {
                color: #f4f8fc;
            }
            QLineEdit, QComboBox {
                min-height: 30px;
                padding: 4px 8px;
                border: 1px solid #5c86ad;
                border-radius: 4px;
                background-color: #0e2236;
                color: #ffffff;
                selection-background-color: #3b84cf;
            }
            QLineEdit::placeholder {
                color: #b8c9d8;
            }
            QComboBox QAbstractItemView {
                background-color: #16324f;
                color: #ffffff;
                selection-background-color: #2f72b4;
            }
            QPushButton {
                min-width: 120px;
                min-height: 34px;
                padding: 6px 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            """
        )

        titulo = QLabel("Troca Segura de Operador")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffffff;")
        layout.addWidget(titulo)

        subtitulo = QLabel(
            "O caixa permanecerá aberto. Informe o novo operador para continuar a operação com segurança."
        )
        subtitulo.setWordWrap(True)
        subtitulo.setStyleSheet("font-size: 13px; color: #d3e2f0;")
        layout.addWidget(subtitulo)

        card_contexto = QFrame()
        card_contexto.setStyleSheet(
            "QFrame { background: #f4f8fc; border: 1px solid #d4e0ec; border-radius: 8px; }"
            "QLabel { color: #16324f; }"
        )
        contexto_layout = QGridLayout(card_contexto)
        contexto_layout.setContentsMargins(14, 14, 14, 14)
        contexto_layout.setHorizontalSpacing(18)
        contexto_layout.setVerticalSpacing(8)

        self.lblOperadorAtual = QLabel("-")
        self.lblCaixaAtual = QLabel("-")
        self.lblHorarioTroca = QLabel("-")
        self.lblFundoAtual = QLabel("-")

        contexto_layout.addWidget(QLabel("Operador atual"), 0, 0)
        contexto_layout.addWidget(self.lblOperadorAtual, 0, 1)
        contexto_layout.addWidget(QLabel("Caixa / PDV"), 1, 0)
        contexto_layout.addWidget(self.lblCaixaAtual, 1, 1)
        contexto_layout.addWidget(QLabel("Horário da troca"), 2, 0)
        contexto_layout.addWidget(self.lblHorarioTroca, 2, 1)
        contexto_layout.addWidget(QLabel("Fundo inicial"), 3, 0)
        contexto_layout.addWidget(self.lblFundoAtual, 3, 1)
        layout.addWidget(card_contexto)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setSpacing(10)

        self.lineEditLogin = QLineEdit()
        self.lineEditLogin.setPlaceholderText("Login ou e-mail do novo operador")
        form.addRow("Novo operador", self.lineEditLogin)

        self.lineEditSenha = QLineEdit()
        self.lineEditSenha.setEchoMode(QLineEdit.Password)
        self.lineEditSenha.setPlaceholderText("Senha do novo operador")
        form.addRow("Senha", self.lineEditSenha)

        self.comboMotivo = QComboBox()
        self.comboMotivo.addItems(
            [
                "Intervalo",
                "Troca de turno",
                "Supervisor assumindo",
                "Outro motivo",
            ]
        )
        form.addRow("Motivo da troca", self.comboMotivo)

        self.lineEditMotivoLivre = QLineEdit()
        self.lineEditMotivoLivre.setPlaceholderText("Detalhe o motivo, se necessário")
        form.addRow("Observação", self.lineEditMotivoLivre)
        layout.addLayout(form)

        self.lblErro = QLabel("")
        self.lblErro.setWordWrap(True)
        self.lblErro.setStyleSheet("color: #b42318; font-size: 12px;")
        self.lblErro.hide()
        layout.addWidget(self.lblErro)

        botoes = QHBoxLayout()
        botoes.addStretch(1)

        self.btnCancelar = QPushButton("Cancelar")
        self.btnConfirmar = QPushButton("Confirmar troca")
        self.btnConfirmar.setDefault(True)
        self.btnCancelar.setStyleSheet(
            "QPushButton { background-color: #eef3f8; color: #16324f; border: 1px solid #90a9c1; }"
            "QPushButton:hover { background-color: #dbe6f0; }"
        )
        self.btnConfirmar.setStyleSheet(
            "QPushButton { background-color: #3b84cf; color: white; border: 1px solid #2d6ca8; }"
            "QPushButton:hover { background-color: #2f72b4; }"
        )

        botoes.addWidget(self.btnCancelar)
        botoes.addWidget(self.btnConfirmar)
        layout.addLayout(botoes)

        self.btnCancelar.clicked.connect(self.reject)
        self.btnConfirmar.clicked.connect(self._confirmar_troca)
        self.lineEditSenha.returnPressed.connect(self._confirmar_troca)

    def _preencher_contexto(self) -> None:
        usuario = SessionManager.current_user() or {}
        operador = str(usuario.get("nome") or "Operador atual")
        pdv_label = str(self._caixa_atual.get("pdv_label") or "Caixa em operação")
        valor_abertura = self._caixa_atual.get("valor_abertura")
        fundo = f"{valor_abertura:.2f}" if isinstance(valor_abertura, (int, float)) else str(valor_abertura or "0,00")

        self.lblOperadorAtual.setText(operador)
        self.lblCaixaAtual.setText(pdv_label)
        self.lblHorarioTroca.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss"))
        self.lblFundoAtual.setText(str(fundo).replace(".", ","))

    def _confirmar_troca(self) -> None:
        login = self.lineEditLogin.text().strip()
        senha = self.lineEditSenha.text().strip()
        motivo = self._motivo_troca()

        if not login or not senha:
            self._mostrar_erro("Informe login e senha do novo operador.")
            return

        try:
            usuario = UsuarioModel.autenticar(login, senha)
        except ValueError as exc:
            self._mostrar_erro(str(exc))
            return
        except Exception as exc:
            mostrar_aviso(self, "Troca não concluída", f"Não foi possível autenticar o novo operador.\n\nDetalhes: {exc}")
            return

        if usuario is None:
            self._mostrar_erro("Login ou senha inválidos para a troca de operador.")
            return

        usuario_atual = SessionManager.current_user() or {}
        if usuario.get("id") == usuario_atual.get("id"):
            self._mostrar_erro("Informe um operador diferente do operador atual.")
            return

        permissoes = {str(permissao).strip() for permissao in usuario.get("permissoes", [])}
        if "vendas.pdv" not in permissoes and "sistema.master" not in permissoes:
            self._mostrar_erro("O operador informado não possui permissão para operar o caixa.")
            return

        SessionManager.login(usuario, persist=SessionManager.session_persistence_enabled())
        from modules.auth.views.login_view import LoginView

        LoginView.usuario_logado = SessionManager.current_user()
        self._novo_operador = usuario
        AuditoriaService.registrar_evento(
            evento="troca_operador",
            categoria="acesso",
            entidade="caixa",
            entidade_id=int(self._caixa_atual.get("id") or 0) or None,
            usuario_id=int(usuario.get("id") or 0),
            caixa_id=int(self._caixa_atual.get("id") or 0) or None,
            detalhes={
                "operador_anterior_id": int(usuario_atual.get("id") or 0),
                "operador_anterior_nome": str(usuario_atual.get("nome") or ""),
                "novo_operador_id": int(usuario.get("id") or 0),
                "novo_operador_nome": str(usuario.get("nome") or ""),
                "motivo": motivo,
                "pdv_label": str(self._caixa_atual.get("pdv_label") or ""),
            },
        )
        log_info(
            "Troca de operador realizada no caixa "
            f"{self._caixa_atual.get('pdv_label', 'atual')}: "
            f"{usuario_atual.get('nome', 'Operador atual')} -> {usuario.get('nome', 'Novo operador')} "
            f"| Motivo: {motivo}"
        )
        self.accept()

    def _motivo_troca(self) -> str:
        motivo = self.comboMotivo.currentText().strip()
        detalhe = self.lineEditMotivoLivre.text().strip()
        if detalhe:
            return f"{motivo}: {detalhe}"
        return motivo

    def _mostrar_erro(self, mensagem: str) -> None:
        self.lblErro.setText(mensagem)
        self.lblErro.show()
        self.lineEditSenha.clear()
        self.lineEditSenha.setFocus()
