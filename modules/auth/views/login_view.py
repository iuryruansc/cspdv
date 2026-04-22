from PyQt5.QtWidgets import QApplication, QDialog

from core.session_manager import SessionManager
from modules.auth.models.usuario_model import UsuarioModel
from ui.login.tela_de_login import Ui_TelaDeLogin

class LoginView(QDialog, Ui_TelaDeLogin):
    usuario_logado = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.btnLogar.clicked.connect(self._login)
        self.btnCancelar.clicked.connect(self.reject)
        self.lineEditSenha.returnPressed.connect(self._login)

        self.labelErro.setVisible(False)
        self.progressBarCarregando.setVisible(False)

    def _login(self):
        login = self.lineEditLogin.text().strip()
        senha = self.lineEditSenha.text().strip()

        if not login or not senha:
            self._show_error("Por favor, preencha os campos corretamente.")
            return

        self._set_loading(True)

        try:
            usuario = UsuarioModel.autenticar(login, senha)

            if usuario:
                perfil_id = usuario.get("perfil_acesso_id")

                if perfil_id is not None:
                    usuario["permissoes"] = UsuarioModel.buscar_permissoes(perfil_id)
                else:
                    usuario["permissoes"] = []

            if usuario is None:
                self._show_error("Login ou senha invalidos.")
                return

            SessionManager.login(usuario)
            LoginView.usuario_logado = SessionManager.current_user()
            print(f"Bem-vindo, {usuario['nome']}!")
            self.accept()

        except Exception as e:
            self._show_error(f"Erro: {str(e)}")
        finally:
            self._set_loading(False)

    def _show_error(self, message: str):
        self.labelErro.setText(f"* {message}")
        self.labelErro.setVisible(True)
        self.lineEditSenha.clear()
        self.lineEditSenha.setFocus()

    def _set_loading(self, is_loading: bool):
        self.btnLogar.setEnabled(not is_loading)
        self.labelCarregando.setText("Verificando..." if is_loading else "Pronto.")
        self.progressBarCarregando.setVisible(is_loading)

        if is_loading:
            self.progressBarCarregando.setRange(0, 0)

        QApplication.processEvents()
