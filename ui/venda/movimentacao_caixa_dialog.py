# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets

class Ui_MovimentacaoCaixaDialog(object):
    def setupUi(self, MovimentacaoCaixaDialog):
        MovimentacaoCaixaDialog.setObjectName("MovimentacaoCaixaDialog")
        MovimentacaoCaixaDialog.resize(1280, 780)
        MovimentacaoCaixaDialog.setMinimumSize(QtCore.QSize(1280, 780))
        self.verticalLayout = QtWidgets.QVBoxLayout(MovimentacaoCaixaDialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.contentHost = QtWidgets.QFrame(MovimentacaoCaixaDialog)
        self.contentLayout = QtWidgets.QVBoxLayout(self.contentHost)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.contentHost)
        self.retranslateUi(MovimentacaoCaixaDialog)
        QtCore.QMetaObject.connectSlotsByName(MovimentacaoCaixaDialog)

    def retranslateUi(self, MovimentacaoCaixaDialog):
        _translate = QtCore.QCoreApplication.translate
        MovimentacaoCaixaDialog.setWindowTitle(_translate("MovimentacaoCaixaDialog", "Registrar Movimentacao de Caixa"))
