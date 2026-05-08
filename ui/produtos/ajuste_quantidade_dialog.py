# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets

class Ui_AjusteQuantidadeDialog(object):
    def setupUi(self, AjusteQuantidadeDialog):
        AjusteQuantidadeDialog.setObjectName("AjusteQuantidadeDialog")
        AjusteQuantidadeDialog.resize(460, 280)
        AjusteQuantidadeDialog.setMinimumSize(QtCore.QSize(460, 280))
        self.verticalLayout = QtWidgets.QVBoxLayout(AjusteQuantidadeDialog)
        self.verticalLayout.setContentsMargins(16, 16, 16, 16)
        self.verticalLayout.setSpacing(12)

        self.lblTitulo = QtWidgets.QLabel(AjusteQuantidadeDialog)
        self.lblTitulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a3a5c;")
        self.verticalLayout.addWidget(self.lblTitulo)

        self.lblCodigo = QtWidgets.QLabel(AjusteQuantidadeDialog)
        self.lblCodigo.setStyleSheet("color: #5d7f99; font-size: 12px;")
        self.verticalLayout.addWidget(self.lblCodigo)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSpacing(10)

        self.lblQuantidadeAtual = QtWidgets.QLabel(AjusteQuantidadeDialog)
        self.formLayout.addRow("Quantidade atual:", self.lblQuantidadeAtual)

        self.comboModo = QtWidgets.QComboBox(AjusteQuantidadeDialog)
        self.formLayout.addRow("Operacao:", self.comboModo)

        self.spinQuantidade = QtWidgets.QSpinBox(AjusteQuantidadeDialog)
        self.formLayout.addRow("Quantidade:", self.spinQuantidade)

        self.lblResultado = QtWidgets.QLabel(AjusteQuantidadeDialog)
        self.lblResultado.setStyleSheet("font-weight: bold; color: #1a5fa0;")
        self.formLayout.addRow("Saldo previsto:", self.lblResultado)

        self.textObservacao = QtWidgets.QPlainTextEdit(AjusteQuantidadeDialog)
        self.textObservacao.setPlaceholderText("Motivo do ajuste ou observacao operacional...")
        self.formLayout.addRow("Observacao:", self.textObservacao)
        self.verticalLayout.addLayout(self.formLayout)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem)
        self.btnCancelar = QtWidgets.QPushButton(AjusteQuantidadeDialog)
        self.buttonLayout.addWidget(self.btnCancelar)
        self.btnSalvar = QtWidgets.QPushButton(AjusteQuantidadeDialog)
        self.btnSalvar.setStyleSheet(
            "QPushButton { background-color: #1a5fa0; color: white; font-weight: bold; border: none; border-radius: 4px; padding: 8px 14px; }"
            "QPushButton:hover { background-color: #2a74b8; }"
        )
        self.buttonLayout.addWidget(self.btnSalvar)
        self.verticalLayout.addLayout(self.buttonLayout)

        self.retranslateUi(AjusteQuantidadeDialog)
        QtCore.QMetaObject.connectSlotsByName(AjusteQuantidadeDialog)

    def retranslateUi(self, AjusteQuantidadeDialog):
        _translate = QtCore.QCoreApplication.translate
        AjusteQuantidadeDialog.setWindowTitle(_translate("AjusteQuantidadeDialog", "Ajustar Quantidade"))
        self.btnCancelar.setText(_translate("AjusteQuantidadeDialog", "Cancelar"))
        self.btnSalvar.setText(_translate("AjusteQuantidadeDialog", "Aplicar Ajuste"))
