import os
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from models.Usuario import UsuarioModel

UI_DIR = os.path.join(os.path.dirname(__file__), '..', 'ui')

class LoginView(QDialog):

    # Guarda o usuário logado para usar posteriormente
    usuario_logado = None

    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(os.path.join(UI_DIR, 'login', 'TelaDeLogin.ui'), self)
        
        # Conecta os botões e a tecla Enter à função de login
        self.btnLogar.clicked.connect(self._login)
        self.btnCancelar.clicked.connect(self.reject)
        self.lineEditSenha.returnPressed.connect(self._login)

    # Função de login
    def _login(self):
        login = self.lineEditLogin.text().strip()
        senha = self.lineEditSenha.text().strip()

        if not login or not senha:
            self._show_error("Por favor, preencha os campos corretamente.")
            return

        self._set_loading(True)

        try:
            usuario = UsuarioModel.autenticar(login, senha)

            if usuario is None:
                self._show_error("Login ou senha inválidos.")
                return
            
            LoginView.usuario_logado = usuario
            print("Usuário logado:", usuario['nome'])
            self.accept()

        except ValueError as e:
            self._show_error(str(e))

        except ConnectionError as e: 
            self._show_error(f"Erro de conexão: {str(e)}")

        except Exception as e:
            self._show_error(f"Erro inesperado: {str(e)}")

        finally: 
            self._set_loading(False)

    # Exibe uma mensagem de erro para o usuário
    def _show_error(self, message: str):
        self.labelErro.setText(message)
        self.labelErro.setVisible(True)
        self.lineEditSenha.clear()
        self.lineEditSenha.setFocus()

    # Atualiza o estado de carregamento da interface
    def _set_loading(self, is_loading: bool):
        self.btnLogar.setEnabled(not is_loading)
        self.labelCarregando.setText('Verificando...' if is_loading else 'Pronto.')

        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()