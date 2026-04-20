import sys
import traceback

from dotenv import find_dotenv, load_dotenv
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox

from database.connection import close_connection, get_connection_diagnostics
from models.setup_model import SetupModel
from views.login.login_view import LoginView
from views.login.selecao_modo_view import SelecaoModoView
from views.setup_wizard_view import SetupWizardView

load_dotenv(find_dotenv())

def _excepthook(tipo, valor, tb):
    print("\n" + "=" * 60)
    print("ERRO NAO TRATADO:")
    traceback.print_exception(tipo, valor, tb)
    print("=" * 60 + "\n")

sys.excepthook = _excepthook

def _mostrar_dialog(dialog):
    frame = dialog.frameGeometry()
    screen = QApplication.primaryScreen()

    if screen is not None:
        frame.moveCenter(screen.availableGeometry().center())
        dialog.move(frame.topLeft())

    dialog.show()
    dialog.raise_()
    dialog.activateWindow()

def _mostrar_erro_conexao(mensagem):
    diagnostics = get_connection_diagnostics()
    detalhes = [
        f"Modo: {diagnostics['mode']}",
        f"Host: {diagnostics['host']}:{diagnostics['port']}",
        f"Banco: {diagnostics['database']}",
        f"Pool habilitado: {'sim' if diagnostics['pool_enabled'] else 'nao'}",
        f"Pool inicializado: {'sim' if diagnostics['pool_initialized'] else 'nao'}",
        f"Timeout: {diagnostics['connection_timeout']}s",
    ]

    if diagnostics["pool_enabled"]:
        detalhes.append(f"Pool name: {diagnostics.get('pool_name', '-')}")
        detalhes.append(f"Pool size: {diagnostics.get('pool_size', '-')}")

    QMessageBox.critical(
        None,
        "Falha na conexao com o banco",
        (
            "Nao foi possivel iniciar o sistema porque a conexao com o banco falhou.\n\n"
            f"{mensagem}\n\n"
            + "\n".join(detalhes)
        ),
    )

def main():
    app = QApplication(sys.argv)

    try:
        if SetupModel.is_first_run():
            wizard = SetupWizardView()
            QTimer.singleShot(0, lambda: _mostrar_dialog(wizard))
            if wizard.exec_() != SetupWizardView.Accepted or not wizard.foi_concluido():
                return 0
    except ConnectionError as exc:
        _mostrar_erro_conexao(str(exc))
        return 1

    login = LoginView()
    QTimer.singleShot(0, lambda: _mostrar_dialog(login))
    if login.exec_() != LoginView.Accepted:
        return 0

    selecao = SelecaoModoView()
    _mostrar_dialog(selecao)
    return app.exec_()

if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        close_connection()
