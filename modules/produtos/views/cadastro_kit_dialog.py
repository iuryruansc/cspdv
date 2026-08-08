from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
)

from modules.produtos.models.produto_model import ProdutoModel
from modules.produtos.services.kit_service import KitService
from utils.format_utils import formatar_moeda
from utils.table_widget_utils import set_table_item
from utils.ui_messages import mostrar_aviso, mostrar_info


class CadastroKitDialog(QDialog):
    def __init__(self, kit_id: int | None = None, parent=None):
        super().__init__(parent)
        self._kit_id = kit_id
        self.resultado: dict[str, Any] | None = None
        self._itens: list[dict[str, Any]] = []
        self._montar_interface()
        if self._kit_id:
            self._carregar_kit()

    def _montar_interface(self) -> None:
        self.setWindowTitle("Cadastro de Kit")
        self.setMinimumSize(700, 550)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        titulo = QLabel("Cadastro de Kit de Produtos", self)
        titulo.setStyleSheet("font-size:18px;font-weight:bold;color:#14324c;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.lineEditNome = QLineEdit(self)
        self.lineEditNome.setMaxLength(250)
        self.lineEditNome.setPlaceholderText("Nome do kit")
        form.addRow("Nome do Kit *", self.lineEditNome)

        self.lineEditCodProduto = QLineEdit(self)
        self.lineEditCodProduto.setMaxLength(60)
        self.lineEditCodProduto.setPlaceholderText("Codigo do kit (opcional)")
        form.addRow("Codigo do Produto", self.lineEditCodProduto)

        self.lineEditDescricao = QLineEdit(self)
        self.lineEditDescricao.setMaxLength(500)
        self.lineEditDescricao.setPlaceholderText("Descricao opcional")
        form.addRow("Descricao", self.lineEditDescricao)

        self.spinPrecoKit = QDoubleSpinBox(self)
        self.spinPrecoKit.setDecimals(2)
        self.spinPrecoKit.setRange(0.01, 999999.99)
        self.spinPrecoKit.setPrefix("R$ ")
        self.spinPrecoKit.setValue(0.00)
        form.addRow("Preco do Kit *", self.spinPrecoKit)

        self.spinEstoque = QSpinBox(self)
        self.spinEstoque.setRange(0, 999999)
        self.spinEstoque.setValue(0)
        form.addRow("Quantidade em Estoque", self.spinEstoque)

        layout.addLayout(form)

        itensHeader = QHBoxLayout()
        lblItens = QLabel("Itens do Kit", self)
        lblItens.setStyleSheet("font-size:14px;font-weight:bold;color:#14324c;")
        itensHeader.addWidget(lblItens)
        itensHeader.addStretch()
        layout.addLayout(itensHeader)

        addItemLayout = QHBoxLayout()
        addItemLayout.setSpacing(6)

        addItemLayout.addWidget(QLabel("Codigo / Barras:"))
        self.lineEditNovoItemCodigo = QLineEdit(self)
        self.lineEditNovoItemCodigo.setPlaceholderText("Digite e pressione Enter")
        self.lineEditNovoItemCodigo.returnPressed.connect(self._buscar_item_para_adicionar)
        addItemLayout.addWidget(self.lineEditNovoItemCodigo, 1)

        addItemLayout.addWidget(QLabel("Qtd:"))
        self.spinNovaQtd = QSpinBox(self)
        self.spinNovaQtd.setRange(1, 9999)
        self.spinNovaQtd.setValue(1)
        self.spinNovaQtd.setFixedWidth(60)
        addItemLayout.addWidget(self.spinNovaQtd)

        layout.addLayout(addItemLayout)

        self.tableItens = QTableWidget(self)
        self.tableItens.setColumnCount(5)
        self.tableItens.setHorizontalHeaderLabels(["Produto", "Codigo", "Preco Unit.", "Qtd.", "Subtotal"])
        self.tableItens.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableItens.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableItens.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tableItens.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tableItens.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tableItens.verticalHeader().setVisible(False)
        self.tableItens.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableItens.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableItens.setStyleSheet(
            "QTableWidget { border: 1px solid #c8d9ea; gridline-color: #dce8f0; }"
            "QHeaderView::section { background: #f0f6fc; color: #1a3a5c; font-weight: bold; border: none; border-right: 1px solid #dce8f0; border-bottom: 2px solid #3585c8; padding: 5px; }"
        )
        layout.addWidget(self.tableItens, 1)

        self.lblTotalItens = QLabel("Total dos componentes: R$ 0,00", self)
        self.lblTotalItens.setStyleSheet("font-size:12px;font-weight:bold;color:#1a3a5c;")
        layout.addWidget(self.lblTotalItens)

        self.btnRemoverItem = QPushButton("Remover Item Selecionado", self)
        self.btnRemoverItem.setStyleSheet(
            "QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 4px; padding: 6px 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #c0392b; }"
        )
        self.btnRemoverItem.clicked.connect(self._remover_item)
        layout.addWidget(self.btnRemoverItem)

        botoesLayout = QHBoxLayout()
        botoesLayout.addStretch()
        self.btnCancelar = QPushButton("Cancelar", self)
        self.btnCancelar.setStyleSheet(
            "QPushButton { background-color: #e8eef5; color: #274764; border: 1px solid #c5d6e4; border-radius: 6px; padding: 8px 20px; font-weight: bold; }"
        )
        self.btnCancelar.clicked.connect(self.reject)
        botoesLayout.addWidget(self.btnCancelar)

        self.btnSalvar = QPushButton("Salvar Kit", self)
        self.btnSalvar.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3585c8, stop:1 #1a5fa0); color: white; border: none; border-radius: 6px; padding: 8px 20px; font-weight: bold; }"
            "QPushButton:hover { background: #2a74b8; }"
        )
        self.btnSalvar.clicked.connect(self._salvar)
        botoesLayout.addWidget(self.btnSalvar)
        layout.addLayout(botoesLayout)

    def _buscar_produto(self, termo: str) -> dict[str, Any] | None:
        termo = termo.strip()
        if not termo:
            return None
        produto = ProdutoModel.buscar_por_codigo_barras(termo)
        if produto:
            return produto
        produto = ProdutoModel.buscar_por_codigo(termo)
        return produto

    def _buscar_item_para_adicionar(self) -> None:
        termo = self.lineEditNovoItemCodigo.text().strip()
        if not termo:
            return
        produto = self._buscar_produto(termo)
        if not produto:
            mostrar_aviso(self, "Produto nao encontrado", f"Nenhum produto encontrado com o codigo '{termo}'.")
            self.lineEditNovoItemCodigo.clear()
            return

        produto_id = int(produto.get("id") or 0)
        preco = float(produto.get("preco_venda") or 0)
        qtd = self.spinNovaQtd.value()

        for i, it in enumerate(self._itens):
            if it["produto_id"] == produto_id:
                self._itens[i]["quantidade"] = it["quantidade"] + qtd
                self._atualizar_tabela()
                self.lineEditNovoItemCodigo.clear()
                self.spinNovaQtd.setValue(1)
                return

        self._itens.append({
            "produto_id": produto_id,
            "produto_nome": str(produto.get("nome") or ""),
            "codigo_barras": str(produto.get("codigo_barras") or "-"),
            "preco_venda": preco,
            "quantidade": qtd,
        })
        self._atualizar_tabela()
        self.lineEditNovoItemCodigo.clear()
        self.spinNovaQtd.setValue(1)

    def _remover_item(self) -> None:
        row = self.tableItens.currentRow()
        if row < 0 or row >= len(self._itens):
            return
        self._itens.pop(row)
        self._atualizar_tabela()

    def _atualizar_tabela(self) -> None:
        self.tableItens.setRowCount(len(self._itens))
        total = 0.0
        for row, item in enumerate(self._itens):
            subtotal = item["preco_venda"] * item["quantidade"]
            total += subtotal
            set_table_item(self.tableItens, row, 0, item["produto_nome"])
            set_table_item(self.tableItens, row, 1, item["codigo_barras"], alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 2, formatar_moeda(item["preco_venda"]), alignment=Qt.AlignRight | Qt.AlignVCenter)
            set_table_item(self.tableItens, row, 3, str(item["quantidade"]), alignment=Qt.AlignCenter)
            set_table_item(self.tableItens, row, 4, formatar_moeda(subtotal), alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.lblTotalItens.setText(f"Total dos componentes: {formatar_moeda(total)}")

    def _carregar_kit(self) -> None:
        kit = KitService.buscar_por_id(self._kit_id)
        if not kit:
            return
        self.lineEditNome.setText(str(kit.get("nome") or ""))
        self.lineEditCodProduto.setText(str(kit.get("cod_produto") or ""))
        self.lineEditDescricao.setText(str(kit.get("descricao") or ""))
        self.spinPrecoKit.setValue(float(kit.get("preco_kit") or 0))
        self.spinEstoque.setValue(int(kit.get("quantidade_estoque") or 0))

        itens = KitService.listar_itens(self._kit_id)
        self._itens = [
            {
                "produto_id": int(it.get("produto_id") or 0),
                "produto_nome": str(it.get("produto") or ""),
                "codigo_barras": str(it.get("codigo_barras") or "-"),
                "preco_venda": float(it.get("preco_venda") or 0),
                "quantidade": int(it.get("quantidade") or 1),
            }
            for it in itens
        ]
        self._atualizar_tabela()

    def _salvar(self) -> None:
        nome = self.lineEditNome.text().strip()
        cod_produto = self.lineEditCodProduto.text().strip() or None
        descricao = self.lineEditDescricao.text().strip()
        preco_kit = self.spinPrecoKit.value()
        quantidade_estoque = self.spinEstoque.value()

        if not nome:
            mostrar_aviso(self, "Campo obrigatorio", "Informe o nome do kit.")
            return
        if not self._itens:
            mostrar_aviso(self, "Itens obrigatorios", "Adicione ao menos um item ao kit.")
            return
        if preco_kit <= 0:
            mostrar_aviso(self, "Campo obrigatorio", "Informe um preco para o kit.")
            return

        dados = {
            "cod_produto": cod_produto,
            "nome": nome,
            "descricao": descricao,
            "preco_kit": preco_kit,
            "quantidade_estoque": quantidade_estoque,
            "itens": self._itens,
        }

        if self._kit_id:
            sucesso, mensagem = KitService.atualizar_kit(kit_id=self._kit_id, **dados)
        else:
            sucesso, mensagem = KitService.cadastrar_kit(**dados)

        if sucesso:
            self.resultado = dados
            mostrar_info(self, "Sucesso", mensagem)
            self.accept()
        else:
            mostrar_aviso(self, "Atencao", mensagem)
