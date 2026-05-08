# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets

class Ui_DetalhesProdutoDialog(object):
    def setupUi(self, DetalhesProdutoDialog):
        DetalhesProdutoDialog.setObjectName("DetalhesProdutoDialog")
        DetalhesProdutoDialog.resize(720, 420)
        DetalhesProdutoDialog.setMinimumSize(QtCore.QSize(720, 420))
        self.verticalLayout = QtWidgets.QVBoxLayout(DetalhesProdutoDialog)
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setSpacing(16)

        self.lblTitulo = QtWidgets.QLabel(DetalhesProdutoDialog)
        self.lblTitulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a3a5c;")
        self.verticalLayout.addWidget(self.lblTitulo)

        self.contentLayout = QtWidgets.QHBoxLayout()
        self.contentLayout.setSpacing(18)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSpacing(10)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.contentLayout.addLayout(self.formLayout, 2)

        self.lblImagem = QtWidgets.QLabel(DetalhesProdutoDialog)
        self.lblImagem.setAlignment(QtCore.Qt.AlignCenter)
        self.lblImagem.setMinimumSize(QtCore.QSize(220, 220))
        self.lblImagem.setStyleSheet(
            "border: 1px solid #c0d8ec; border-radius: 6px; background-color: #f7fbff; color: #5d7f99;"
        )
        self.contentLayout.addWidget(self.lblImagem, 1)
        self.verticalLayout.addLayout(self.contentLayout)

        self.buttonLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem)
        self.btnFechar = QtWidgets.QPushButton(DetalhesProdutoDialog)
        self.buttonLayout.addWidget(self.btnFechar)
        self.verticalLayout.addLayout(self.buttonLayout)

        self.retranslateUi(DetalhesProdutoDialog)
        QtCore.QMetaObject.connectSlotsByName(DetalhesProdutoDialog)

    def retranslateUi(self, DetalhesProdutoDialog):
        _translate = QtCore.QCoreApplication.translate
        DetalhesProdutoDialog.setWindowTitle(_translate("DetalhesProdutoDialog", "Detalhes do Produto"))
        self.lblImagem.setText(_translate("DetalhesProdutoDialog", "Sem imagem"))
        self.btnFechar.setText(_translate("DetalhesProdutoDialog", "Fechar"))
