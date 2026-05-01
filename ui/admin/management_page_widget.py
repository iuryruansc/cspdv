from PyQt5 import QtCore, QtWidgets


class Ui_ManagementPageWidget(object):
    def setupUi(self, widget):
        widget.setObjectName("frameManagementPage")
        widget.setStyleSheet(
            """
            QFrame#frameManagementPage {
                background-color: white;
                border: 1px solid #a8c4d8;
                border-radius: 6px;
            }
            QLabel[sectionTitle="true"] {
                color: #1a3a5c;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel[sectionHint="true"] {
                color: #5d7f99;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #f7fbff;
                border: 1px solid #c5d8e6;
                border-radius: 4px;
                padding: 7px 10px;
                font-size: 12px;
            }
            QPushButton[toolbarButton="true"] {
                background-color: #f0f6fc;
                color: #1a3a5c;
                border: 1px solid #c0d8ec;
                border-radius: 4px;
                padding: 7px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton[toolbarButton="true"]:hover {
                background-color: #dceaf4;
                border-color: #3585c8;
                color: #1a5fa0;
            }
            QPushButton[primaryButton="true"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3585c8, stop:1 #1a5fa0);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton[primaryButton="true"]:hover {
                background: #2a74b8;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #d6e3ee;
                border-radius: 4px;
                font-size: 12px;
                gridline-color: #dce8f0;
            }
            QHeaderView::section {
                background-color: #f0f6fc;
                color: #1a3a5c;
                font-size: 11px;
                font-weight: bold;
                padding: 5px 6px;
                border: none;
                border-right: 1px solid #dce8f0;
                border-bottom: 2px solid #3585c8;
            }
            """
        )

        self.rootLayout = QtWidgets.QVBoxLayout(widget)
        self.rootLayout.setContentsMargins(16, 16, 16, 16)
        self.rootLayout.setSpacing(12)

        self.headerLayout = QtWidgets.QVBoxLayout()
        self.headerLayout.setSpacing(4)
        self.lblTitle = QtWidgets.QLabel(widget)
        self.lblTitle.setProperty("sectionTitle", True)
        self.lblTitle.setText("Gerenciamento")
        self.lblHint = QtWidgets.QLabel(widget)
        self.lblHint.setProperty("sectionHint", True)
        self.lblHint.setWordWrap(True)
        self.lblHint.setText("Selecione um cadastro para consultar e abrir acoes rapidas.")
        self.headerLayout.addWidget(self.lblTitle)
        self.headerLayout.addWidget(self.lblHint)
        self.rootLayout.addLayout(self.headerLayout)

        self.toolbarLayout = QtWidgets.QHBoxLayout()
        self.toolbarLayout.setSpacing(8)
        self.lineEditBusca = QtWidgets.QLineEdit(widget)
        self.lineEditBusca.setPlaceholderText("Buscar por qualquer coluna visivel...")
        self.toolbarLayout.addWidget(self.lineEditBusca, 1)

        self.btnAtualizar = QtWidgets.QPushButton(widget)
        self.btnAtualizar.setProperty("toolbarButton", True)
        self.btnAtualizar.setText("Atualizar")
        self.toolbarLayout.addWidget(self.btnAtualizar)

        self.btnDetalhes = QtWidgets.QPushButton(widget)
        self.btnDetalhes.setProperty("toolbarButton", True)
        self.btnDetalhes.setEnabled(False)
        self.btnDetalhes.setText("Detalhes")
        self.btnDetalhes.hide()
        self.toolbarLayout.addWidget(self.btnDetalhes)

        self.btnEditar = QtWidgets.QPushButton(widget)
        self.btnEditar.setProperty("toolbarButton", True)
        self.btnEditar.setEnabled(False)
        self.btnEditar.setToolTip("A edicao inline sera adicionada na proxima etapa.")
        self.btnEditar.setText("Editar")
        self.toolbarLayout.addWidget(self.btnEditar)

        self.btnAjustarQuantidade = QtWidgets.QPushButton(widget)
        self.btnAjustarQuantidade.setProperty("toolbarButton", True)
        self.btnAjustarQuantidade.setText("Ajustar Quantidade")
        self.btnAjustarQuantidade.hide()
        self.toolbarLayout.addWidget(self.btnAjustarQuantidade)

        self.btnToggleAtivo = QtWidgets.QPushButton(widget)
        self.btnToggleAtivo.setProperty("toolbarButton", True)
        self.btnToggleAtivo.setEnabled(False)
        self.btnToggleAtivo.setToolTip("A alteracao de status sera adicionada na proxima etapa.")
        self.btnToggleAtivo.setText("Ativar / Desativar")
        self.toolbarLayout.addWidget(self.btnToggleAtivo)

        self.btnNovo = QtWidgets.QPushButton(widget)
        self.btnNovo.setProperty("primaryButton", True)
        self.btnNovo.setText("Novo cadastro")
        self.toolbarLayout.addWidget(self.btnNovo)

        self.rootLayout.addLayout(self.toolbarLayout)

        self.tableResultados = QtWidgets.QTableWidget(widget)
        self.tableResultados.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableResultados.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableResultados.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableResultados.verticalHeader().setVisible(False)
        self.tableResultados.horizontalHeader().setStretchLastSection(False)
        self.rootLayout.addWidget(self.tableResultados, 1)

        self.footerLayout = QtWidgets.QHBoxLayout()
        self.lblResumo = QtWidgets.QLabel(widget)
        self.lblResumo.setProperty("sectionHint", True)
        self.lblResumo.setText("Nenhum registro carregado.")
        self.footerLayout.addWidget(self.lblResumo)
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.footerLayout.addItem(spacer)
        self.rootLayout.addLayout(self.footerLayout)

        QtCore.QMetaObject.connectSlotsByName(widget)
