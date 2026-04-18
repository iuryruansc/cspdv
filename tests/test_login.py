import sys
import os
import traceback
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))

root_dir = os.path.abspath(os.path.join(current_dir, ".."))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

root_dir = str(Path(__file__).parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from PyQt5.QtWidgets import QApplication, QMessageBox
from views.login.login_view import LoginView
from views.login.selecao_modo_view import SelecaoModoView
from database.connection import close_connection

def _excepthook(tipo, valor, tb):
    """Captura erros fatais e exibe no console e em uma caixa de mensagem."""
    erro_msg = "".join(traceback.format_exception(tipo, valor, tb))
    print("\n" + "!"*60)
    print("ERRO NO AMBIENTE DE TESTE:")
    print(erro_msg)
    print("!"*60 + "\n")
    
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Erro de Execução")
    msg.setText("Ocorreu um erro não tratado no teste.")
    msg.setInformativeText(str(valor))
    msg.setDetailedText(erro_msg)
    msg.exec_()

sys.excepthook = _excepthook

def run_test():
    app = QApplication(sys.argv)
    app.setApplicationName("CSPdv - Teste de Login")

    print("\n" + "="*50)
    print("INICIANDO TESTE DIRETO DE LOGIN")
    print("="*50)

    login_window = LoginView()
    
    if login_window.exec_() == LoginView.Accepted:
        usuario = LoginView.usuario_logado
        
        print(f"\n[SUCESSO] Login aceito!")
        if usuario:
            print(f"ID: {usuario.get('id')}")
            print(f"Nome: {usuario.get('nome')}")
            print(f"Cargo: {usuario.get('cargo')}")
        
        print("\nAbrindo Seleção de Modo...")
        selecao = SelecaoModoView()
        selecao.show()
        
        sys.exit(app.exec_())
    else:
        print("\n[INFO] O login foi cancelado ou a janela foi fechada.")

def run_test_bypass():
    app = QApplication(sys.argv)
    
    print("\n" + "="*50)
    print("MODO DE TESTE: BYPASS DE LOGIN ATIVADO")
    print("="*50)

    usuario_mock = {
        'id': 1,
        'nome': 'Desenvolvedor Teste',
        'login': 'admin',
        'cargo': 'Administrador',
        'email': 'teste@cspdv.com'
    }

    LoginView.usuario_logado = usuario_mock
    print(f"[BYPASS] Usuário '{usuario_mock['nome']}' injetado com sucesso.")

    print("Encaminhando para SelecaoModoView...")
    
    try:
        selecao = SelecaoModoView()
        selecao.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"[ERRO] Falha ao abrir a próxima tela: {e}")


if __name__ == '__main__':
    try:
        #run_test()
        run_test_bypass()
    except Exception as e:
        print(f"Falha ao iniciar o teste: {e}")
    finally:
        # Garante que a conexão com o banco seja encerrada ao fechar o teste
        close_connection()
        print("Conexão com o banco de dados encerrada.")