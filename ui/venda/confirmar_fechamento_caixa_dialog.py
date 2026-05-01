# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_ConfirmarFechamentoCaixaDialog(object):
    def setupUi(self, ConfirmarFechamentoCaixaDialog):
        ConfirmarFechamentoCaixaDialog.setObjectName("ConfirmarFechamentoCaixaDialog")
        ConfirmarFechamentoCaixaDialog.resize(460, 260)
        ConfirmarFechamentoCaixaDialog.setStyleSheet(
            """
            QDialog {
                background-color: #eef4fa;
            }
            QLabel {
                background-color: transparent;
                color: #17324d;
                font-size: 12px;
            }
            QLineEdit {
                background-color: white;
                color: #17324d;
                border: 1px solid #b8cee0;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #3585c8;
            }
            QPushButton {
                min-width: 110px;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#btnCancelar {
                background-color: #e8eef5;
                color: #274764;
                border: 1px solid #c5d6e4;
            }
            QPushButton#btnConfirmar {
                background-color: #2f78bd;
                color: white;
                border: 1px solid #2869a5;
            }
            QFrame#summaryCard {
                background-color: #ffffff;
                border: 1px solid #d5e2ee;
                border-radius: 12px;
            }
            """
        )

        self.verticalLayout = QtWidgets.QVBoxLayout(ConfirmarFechamentoCaixaDialog)
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setSpacing(14)

        self.lblTitulo = QtWidgets.QLabel(ConfirmarFechamentoCaixaDialog)
        self.lblTitulo.setObjectName("lblTitulo")
        self.lblTitulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #163a59;")
        self.verticalLayout.addWidget(self.lblTitulo)

        self.summaryCard = QtWidgets.QFrame(ConfirmarFechamentoCaixaDialog)
        self.summaryCard.setObjectName("summaryCard")
        self.summaryLayout = QtWidgets.QVBoxLayout(self.summaryCard)
        self.summaryLayout.setContentsMargins(16, 14, 16, 14)
        self.summaryLayout.setSpacing(10)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setHorizontalSpacing(22)
        self.formLayout.setVerticalSpacing(10)

        self.lblTotal = QtWidgets.QLabel(self.summaryCard)
        self.lblTotal.setStyleSheet("color: #5f7891; font-size: 12px; font-weight: bold;")
        self.valueTotal = QtWidgets.QLabel(self.summaryCard)
        self.valueTotal.setStyleSheet("color: #17324d; font-size: 13px; font-weight: bold;")
        self.formLayout.addRow(self.lblTotal, self.valueTotal)

        self.lblContado = QtWidgets.QLabel(self.summaryCard)
        self.lblContado.setStyleSheet("color: #5f7891; font-size: 12px; font-weight: bold;")
        self.valueContado = QtWidgets.QLabel(self.summaryCard)
        self.valueContado.setStyleSheet("color: #17324d; font-size: 13px; font-weight: bold;")
        self.formLayout.addRow(self.lblContado, self.valueContado)

        self.lblDiferenca = QtWidgets.QLabel(self.summaryCard)
        self.lblDiferenca.setStyleSheet("color: #5f7891; font-size: 12px; font-weight: bold;")
        self.valueDiferenca = QtWidgets.QLabel(self.summaryCard)
        self.formLayout.addRow(self.lblDiferenca, self.valueDiferenca)

        self.summaryLayout.addLayout(self.formLayout)
        self.verticalLayout.addWidget(self.summaryCard)

        self.lblAviso = QtWidgets.QLabel(ConfirmarFechamentoCaixaDialog)
        self.lblAviso.setWordWrap(True)
        self.lblAviso.setObjectName("lblAviso")
        self.verticalLayout.addWidget(self.lblAviso)

        self.lineSenhaAdmin = QtWidgets.QLineEdit(ConfirmarFechamentoCaixaDialog)
        self.lineSenhaAdmin.setObjectName("lineSenhaAdmin")
        self.verticalLayout.addWidget(self.lineSenhaAdmin)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem)
        self.btnCancelar = QtWidgets.QPushButton(ConfirmarFechamentoCaixaDialog)
        self.btnCancelar.setObjectName("btnCancelar")
        self.buttonLayout.addWidget(self.btnCancelar)
        self.btnConfirmar = QtWidgets.QPushButton(ConfirmarFechamentoCaixaDialog)
        self.btnConfirmar.setObjectName("btnConfirmar")
        self.buttonLayout.addWidget(self.btnConfirmar)
        self.verticalLayout.addLayout(self.buttonLayout)

        self.retranslateUi(ConfirmarFechamentoCaixaDialog)
        QtCore.QMetaObject.connectSlotsByName(ConfirmarFechamentoCaixaDialog)

    def retranslateUi(self, ConfirmarFechamentoCaixaDialog):
        _translate = QtCore.QCoreApplication.translate
        ConfirmarFechamentoCaixaDialog.setWindowTitle(_translate("ConfirmarFechamentoCaixaDialog", "Confirmar Fechamento"))
        self.lblTitulo.setText(_translate("ConfirmarFechamentoCaixaDialog", "Confirme os dados do fechamento do caixa"))
        self.lblTotal.setText(_translate("ConfirmarFechamentoCaixaDialog", "Total esperado:"))
        self.lblContado.setText(_translate("ConfirmarFechamentoCaixaDialog", "Valor contado:"))
        self.lblDiferenca.setText(_translate("ConfirmarFechamentoCaixaDialog", "Diferenca:"))
        self.lineSenhaAdmin.setPlaceholderText(_translate("ConfirmarFechamentoCaixaDialog", "Senha do administrador"))
        self.btnCancelar.setText(_translate("ConfirmarFechamentoCaixaDialog", "Cancelar"))
        self.btnConfirmar.setText(_translate("ConfirmarFechamentoCaixaDialog", "Confirmar fechamento"))


class Ui_FechamentoRealizadoDialog(object):
    def setupUi(self, FechamentoRealizadoDialog):
        FechamentoRealizadoDialog.setObjectName("FechamentoRealizadoDialog")
        FechamentoRealizadoDialog.resize(420, 170)
        FechamentoRealizadoDialog.setStyleSheet(
            """
            QDialog {
                background-color: #eef4fa;
            }
            QLabel {
                background-color: transparent;
                color: #17324d;
            }
            QFrame {
                background-color: #ffffff;
                border: 1px solid #d5e2ee;
                border-radius: 12px;
            }
            QPushButton {
                min-width: 120px;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
                background-color: #2f78bd;
                color: white;
                border: 1px solid #2869a5;
            }
            QPushButton:hover {
                background-color: #2769a8;
            }
            """
        )

        self.verticalLayout = QtWidgets.QVBoxLayout(FechamentoRealizadoDialog)
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setSpacing(14)

        self.lblTitulo = QtWidgets.QLabel(FechamentoRealizadoDialog)
        self.lblTitulo.setObjectName("lblTitulo")
        self.lblTitulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #163a59;")
        self.verticalLayout.addWidget(self.lblTitulo)

        self.cardMensagem = QtWidgets.QFrame(FechamentoRealizadoDialog)
        self.cardLayout = QtWidgets.QVBoxLayout(self.cardMensagem)
        self.cardLayout.setContentsMargins(14, 12, 14, 12)
        self.cardLayout.setSpacing(8)
        self.lblMensagem = QtWidgets.QLabel(self.cardMensagem)
        self.lblMensagem.setWordWrap(True)
        self.lblMensagem.setStyleSheet("font-size: 13px; color: #31506b;")
        self.cardLayout.addWidget(self.lblMensagem)
        self.verticalLayout.addWidget(self.cardMensagem)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem)
        self.btnOk = QtWidgets.QPushButton(FechamentoRealizadoDialog)
        self.btnOk.setObjectName("btnOk")
        self.buttonLayout.addWidget(self.btnOk)
        self.verticalLayout.addLayout(self.buttonLayout)

        self.retranslateUi(FechamentoRealizadoDialog)
        QtCore.QMetaObject.connectSlotsByName(FechamentoRealizadoDialog)

    def retranslateUi(self, FechamentoRealizadoDialog):
        _translate = QtCore.QCoreApplication.translate
        FechamentoRealizadoDialog.setWindowTitle(_translate("FechamentoRealizadoDialog", "Caixa fechado"))
        self.lblTitulo.setText(_translate("FechamentoRealizadoDialog", "Caixa fechado com sucesso"))
        self.btnOk.setText(_translate("FechamentoRealizadoDialog", "OK"))
