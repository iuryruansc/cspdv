# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets

class Ui_AbrirFrenteCaixaDialog(object):
    def setupUi(self, AbrirFrenteCaixaDialog):
        AbrirFrenteCaixaDialog.setObjectName("AbrirFrenteCaixaDialog")
        AbrirFrenteCaixaDialog.resize(1280, 820)
        AbrirFrenteCaixaDialog.setMinimumSize(QtCore.QSize(1240, 800))
        self.verticalLayout = QtWidgets.QVBoxLayout(AbrirFrenteCaixaDialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.contentHost = QtWidgets.QFrame(AbrirFrenteCaixaDialog)
        self.contentLayout = QtWidgets.QVBoxLayout(self.contentHost)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.contentHost)
        self.retranslateUi(AbrirFrenteCaixaDialog)
        QtCore.QMetaObject.connectSlotsByName(AbrirFrenteCaixaDialog)

    def retranslateUi(self, AbrirFrenteCaixaDialog):
        _translate = QtCore.QCoreApplication.translate
        AbrirFrenteCaixaDialog.setWindowTitle(_translate("AbrirFrenteCaixaDialog", "Abrir Frente de Caixa"))
