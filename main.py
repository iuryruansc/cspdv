import sys
import traceback
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv()) 

from PyQt5.QtWidgets import QApplication
from views.login_view import LoginView
from views.selecao_modo_view import SelecaoModoView
from views.setup_wizard_view import SetupWizardView
from models.setup_model import SetupModel
from database.connection import close_connection


def _excepthook(tipo, valor, tb):
    print("\n" + "="*60)
    print("ERRO NÃO TRATADO:")
    traceback.print_exception(tipo, valor, tb)
    print("="*60 + "\n")

sys.excepthook = _excepthook


def main():
    app = QApplication(sys.argv)

    # ── Primeiro uso: exibe o wizard antes do login ──────────────────────
    try:
        if SetupModel.is_first_run():
            wizard = SetupWizardView()
            if wizard.exec_() != SetupWizardView.Accepted or not wizard.foi_concluido():
                return  # usuário cancelou sem concluir
    except ConnectionError:
        # Se não conseguiu conectar, o LoginView vai mostrar o erro
        pass

    # ── Login normal ─────────────────────────────────────────────────────
    login = LoginView()
    if login.exec_() == LoginView.Accepted:
        selecao = SelecaoModoView()
        selecao.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main()
    finally:
        close_connection()