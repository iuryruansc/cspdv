import os
import sys
import traceback
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

root_dir = str(Path(__file__).parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from dotenv import find_dotenv, load_dotenv
from PyQt5.QtWidgets import QApplication, QMessageBox

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from database.connection import close_connection
from modules.venda.views.frente_loja_view import FrenteLojaView

load_dotenv(find_dotenv())


def _excepthook(tipo, valor, tb):
    erro_msg = "".join(traceback.format_exception(tipo, valor, tb))
    print("\n" + "!" * 60)
    print("ERRO NO AMBIENTE DE TESTE DE VENDAS:")
    print(erro_msg)
    print("!" * 60 + "\n")

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Erro de Execucao")
    msg.setText("Ocorreu um erro nao tratado no teste da area de vendas.")
    msg.setInformativeText(str(valor))
    msg.setDetailedText(erro_msg)
    msg.exec_()


sys.excepthook = _excepthook


def _mock_usuario() -> dict:
    return {
        "id": 1,
        "nome": "Desenvolvedor Teste",
        "login": "admin",
        "cargo": "Administrador",
        "email": "teste@cspdv.com",
        "permissoes": ["vendas.pdv", "sistema.master"],
    }


def _mock_caixa_aberto() -> dict:
    return {
        "id": 999,
        "pdv_id": 1,
        "pdv_label": "PDV 01 - Loja Teste",
        "usuario_id": 1,
        "usuario_nome": "Desenvolvedor Teste",
        "valor_abertura": 150.0,
        "status": "ABERTO",
        "opened_at": "22/04/2026 14:00",
    }


def run_test_frente_loja():
    app = QApplication(sys.argv)
    app.setApplicationName("CSPdv - Teste da Area de Vendas")
    os.environ["CSPDV_ALLOW_TEST_CAIXA_EXIT"] = "true"

    print("\n" + "=" * 50)
    print("MODO DE TESTE: FRENTE DE LOJA COM CAIXA ABERTO")
    print("=" * 50)

    usuario_mock = _mock_usuario()
    caixa_mock = _mock_caixa_aberto()

    SessionManager.login(usuario_mock)
    CaixaSession.open(caixa_mock)

    print(f"[BYPASS] Usuario '{usuario_mock['nome']}' injetado com sucesso.")
    print(f"[BYPASS] Sessao do usuario: {SessionManager.diagnostics()}")
    print(f"[BYPASS] Caixa aberto simulado: {CaixaSession.current()}")
    print("Abrindo FrenteLojaView...")

    try:
        frente_loja = FrenteLojaView()
        frente_loja.show()

        sys.exit(app.exec_())
    except Exception as exc:
        print(f"[ERRO] Falha ao abrir a area de vendas: {exc}")


if __name__ == "__main__":
    try:
        run_test_frente_loja()
    except Exception as exc:
        print(f"Falha ao iniciar o teste da area de vendas: {exc}")
    finally:
        os.environ.pop("CSPDV_ALLOW_TEST_CAIXA_EXIT", None)
        CaixaSession.close()
        SessionManager.logout()
        close_connection()
        print("Sessao de vendas encerrada e conexao com o banco finalizada.")
