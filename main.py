import sys
from PyQt5.QtWidgets import QApplication
from views.login_view import LoginView
from views.selecao_modo_view import SelecaoModoView

def main():
    app = QApplication(sys.argv)

    login = LoginView()

    if login.exec_() == LoginView.Accepted:
        print("Login bem-sucedido!")
        selecao = SelecaoModoView()
        selecao.show()
        sys.exit(app.exec_())
    else: 
        print("Login cancelado ou falhou.")

if __name__ == '__main__':
    main()