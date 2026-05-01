# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class Ui_FecharCaixaDialog(object):
    def setupUi(self, FecharCaixaDialog):
        FecharCaixaDialog.setObjectName("FecharCaixaDialog")
        FecharCaixaDialog.resize(1280, 780)
        FecharCaixaDialog.setMinimumSize(QtCore.QSize(1280, 780))
        self.verticalLayout = QtWidgets.QVBoxLayout(FecharCaixaDialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.contentHost = QtWidgets.QFrame(FecharCaixaDialog)
        self.contentLayout = QtWidgets.QVBoxLayout(self.contentHost)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)
        self.verticalLayout.addWidget(self.contentHost)
        self.retranslateUi(FecharCaixaDialog)
        QtCore.QMetaObject.connectSlotsByName(FecharCaixaDialog)

    def retranslateUi(self, FecharCaixaDialog):
        _translate = QtCore.QCoreApplication.translate
        FecharCaixaDialog.setWindowTitle(_translate("FecharCaixaDialog", "Fechar Caixa"))
