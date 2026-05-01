# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_SelecionarClienteDialog(object):
    def setupUi(self, SelecionarClienteDialog):
        SelecionarClienteDialog.setObjectName("SelecionarClienteDialog")
        SelecionarClienteDialog.resize(460, 420)
        SelecionarClienteDialog.setMinimumSize(QtCore.QSize(460, 420))
        SelecionarClienteDialog.setStyleSheet(
            """
            QDialog { background-color: #eef4fa; }
            QLabel { color: #17324d; font-size: 12px; background: transparent; }
            QLineEdit {
                background: white;
                color: #17324d;
                border: 1px solid #b8cee0;
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #3585c8; }
            QListWidget {
                background: white;
                color: #17324d;
                border: 1px solid #d5e2ee;
                border-radius: 10px;
                padding: 4px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #e6f1fb;
                color: #17324d;
            }
            QPushButton {
                min-width: 110px;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#btnConsumidorFinal, QPushButton#btnCancelar {
                background-color: #e8eef5;
                color: #274764;
                border: 1px solid #c5d6e4;
            }
            QPushButton#btnSelecionar {
                background-color: #2f78bd;
                color: white;
                border: 1px solid #2869a5;
            }
            """
        )

        self.verticalLayout = QtWidgets.QVBoxLayout(SelecionarClienteDialog)
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")

        self.lblTitulo = QtWidgets.QLabel(SelecionarClienteDialog)
        self.lblTitulo.setObjectName("lblTitulo")
        self.lblTitulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #163a59;")
        self.verticalLayout.addWidget(self.lblTitulo)

        self.lineBusca = QtWidgets.QLineEdit(SelecionarClienteDialog)
        self.lineBusca.setObjectName("lineBusca")
        self.verticalLayout.addWidget(self.lineBusca)

        self.listaClientes = QtWidgets.QListWidget(SelecionarClienteDialog)
        self.listaClientes.setObjectName("listaClientes")
        self.verticalLayout.addWidget(self.listaClientes)

        self.lblStatus = QtWidgets.QLabel(SelecionarClienteDialog)
        self.lblStatus.setObjectName("lblStatus")
        self.lblStatus.setStyleSheet("color: #5f7891;")
        self.verticalLayout.addWidget(self.lblStatus)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem)
        self.btnConsumidorFinal = QtWidgets.QPushButton(SelecionarClienteDialog)
        self.btnConsumidorFinal.setObjectName("btnConsumidorFinal")
        self.buttonLayout.addWidget(self.btnConsumidorFinal)
        self.btnCancelar = QtWidgets.QPushButton(SelecionarClienteDialog)
        self.btnCancelar.setObjectName("btnCancelar")
        self.buttonLayout.addWidget(self.btnCancelar)
        self.btnSelecionar = QtWidgets.QPushButton(SelecionarClienteDialog)
        self.btnSelecionar.setObjectName("btnSelecionar")
        self.buttonLayout.addWidget(self.btnSelecionar)
        self.verticalLayout.addLayout(self.buttonLayout)

        self.retranslateUi(SelecionarClienteDialog)
        QtCore.QMetaObject.connectSlotsByName(SelecionarClienteDialog)

    def retranslateUi(self, SelecionarClienteDialog):
        _translate = QtCore.QCoreApplication.translate
        SelecionarClienteDialog.setWindowTitle(_translate("SelecionarClienteDialog", "Selecionar cliente"))
        self.lblTitulo.setText(_translate("SelecionarClienteDialog", "Localize o cliente por nome ou CPF"))
        self.lineBusca.setPlaceholderText(_translate("SelecionarClienteDialog", "Digite ao menos 2 caracteres..."))
        self.lblStatus.setText(_translate("SelecionarClienteDialog", "Consumidor Final sera usado se nenhum cliente for selecionado."))
        self.btnConsumidorFinal.setText(_translate("SelecionarClienteDialog", "Consumidor Final"))
        self.btnCancelar.setText(_translate("SelecionarClienteDialog", "Cancelar"))
        self.btnSelecionar.setText(_translate("SelecionarClienteDialog", "Selecionar"))
