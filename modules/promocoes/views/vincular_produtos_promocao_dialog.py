from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
)

from modules.promocoes.services.promocao_service import PromocaoService
from ui.promocoes.vincular_produtos_promocao import Ui_VincularProdutosPromocao
from utils.format_utils import formatar_data, formatar_moeda
from utils.table_widget_utils import set_table_item
from utils.ui_messages import mostrar_aviso, mostrar_info
from modules.shared.constants import FLAG_NAO, FLAG_SIM

class VincularProdutosPromocaoDialog(QDialog, Ui_VincularProdutosPromocao):
    def __init__(self, promocao_id: int, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)

        self.promocao_id = int(promocao_id)
        self._promocao: dict[str, Any] = {}
        self._produtos_encontrados: list[dict[str, Any]] = []
        self._itens_vinculados: list[dict[str, Any]] = []

        self._configurar_tabelas()
        self.btnVincularProduto.setText("Vincular selecionados")
        self.lblBuscaHint.setText("Selecione um ou mais produtos; use Ctrl/Shift para selecionar em lote.")
        self._conectar_sinais()
        self._carregar_contexto()

    def _configurar_tabelas(self) -> None:
        self.tableProdutos: QTableWidget
        self.tableItensVinculados: QTableWidget
        self.tableProdutos.setColumnWidth(0, 120)
        self.tableProdutos.setColumnWidth(1, 250)
        self.tableProdutos.setColumnWidth(2, 100)
        self.tableProdutos.setColumnWidth(3, 80)
        self.tableProdutos.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableItensVinculados.setColumnCount(7)
        self.tableItensVinculados.setHorizontalHeaderLabels(
            ["Produto", "Regra", "Preço Atual", "Preço Promo", "Desconto (R$)", "Desconto (%)", "Observação"]
        )
        self.tableItensVinculados.setColumnWidth(0, 190)
        self.tableItensVinculados.setColumnWidth(1, 125)
        self.tableItensVinculados.setColumnWidth(2, 90)
        self.tableItensVinculados.setColumnWidth(3, 95)
        self.tableItensVinculados.setColumnWidth(4, 85)
        self.tableItensVinculados.setColumnWidth(5, 85)
        self.tableItensVinculados.setColumnWidth(6, 110)

        self._check_regra_padrao = QCheckBox("Usar regra padrão da promoção", self.frameBusca)
        self._check_regra_padrao.setChecked(True)
        self._check_regra_padrao.toggled.connect(self._alternar_regra_item)

        self._label_regra_item = QLabel("Regra do produto:", self.frameBusca)
        self._combo_regra_item = QComboBox(self.frameBusca)
        self._combo_regra_item.addItem("Desconto percentual", "PERCENTUAL")
        self._combo_regra_item.addItem("Desconto em valor", "VALOR")
        self._combo_regra_item.addItem("Preço promocional", "PRECO_FIXO")
        self._combo_regra_item.addItem("Novo preço por produto", "NOVO_PRECO")
        self._spin_valor_regra = QDoubleSpinBox(self.frameBusca)
        self._spin_valor_regra.setDecimals(2)
        self._spin_valor_regra.setRange(0.01, 999999.99)
        self._spin_valor_regra.setFixedWidth(125)
        self._atualizar_formato_regra_item()
        self._combo_regra_item.currentIndexChanged.connect(self._atualizar_formato_regra_item)

        regra_layout = QHBoxLayout()
        regra_layout.setSpacing(8)
        regra_layout.addWidget(self._check_regra_padrao)
        regra_layout.addWidget(self._label_regra_item)
        regra_layout.addWidget(self._combo_regra_item)
        regra_layout.addWidget(self._spin_valor_regra)
        regra_layout.addStretch()
        self.buscaLayout.insertLayout(3, regra_layout)
        self._alternar_regra_item(True)

    def _conectar_sinais(self) -> None:
        self.btnAtualizar.clicked.connect(self._carregar_contexto)
        self.btnFechar.clicked.connect(self.reject)
        self.btnVincularProduto.clicked.connect(self._vincular_produto)
        self.btnRemoverProduto.clicked.connect(self._remover_produto)
        self.txtBuscaProduto.returnPressed.connect(self._carregar_produtos)
        self.txtBuscaProduto.textChanged.connect(self._carregar_produtos)

    def _carregar_contexto(self) -> None:
        promocao = PromocaoService.buscar_promocao(self.promocao_id)
        if not promocao:
            mostrar_aviso(self, "Promoções", "Promoção não localizada.")
            self.reject()
            return
        self._promocao = promocao
        self._popular_resumo_promocao()
        tipo = str(promocao.get("tipo_desconto") or "").strip().upper()
        if tipo == "POR_PRODUTO":
            self._check_regra_padrao.setChecked(False)
            self._check_regra_padrao.setEnabled(False)
        self._carregar_produtos()
        self._carregar_itens_vinculados()

    def _popular_resumo_promocao(self) -> None:
        nome = str(self._promocao.get("nome") or "-")
        codigo = str(self._promocao.get("codigo") or "-")
        tipo = self._label_tipo(str(self._promocao.get("tipo_desconto") or "-"))
        data_inicio = formatar_data(self._promocao.get("data_inicio"), "%d/%m/%Y %H:%M")
        data_fim = formatar_data(self._promocao.get("data_fim"), "%d/%m/%Y %H:%M")

        self.lblCodigoPromocao.setText(f"Código: {codigo}")
        self.lblTipoPromocao.setText(f"Tipo: {tipo}")
        self.lblResumoNomeValor.setText(nome)
        self.lblResumoVigenciaValor.setText(f"{data_inicio} até {data_fim}")
        self.lblResumoRegraValor.setText(self._formatar_regra_promocao(self._promocao))

    def _carregar_produtos(self) -> None:
        self._produtos_encontrados = PromocaoService.buscar_produtos_disponiveis(
            self.promocao_id,
            self.txtBuscaProduto.text().strip(),
        )
        self.tableProdutos.setRowCount(len(self._produtos_encontrados))
        for row, produto in enumerate(self._produtos_encontrados):
            valores = [
                str(produto.get("codigo_barras") or "-"),
                str(produto.get("nome") or "-"),
                formatar_moeda(produto.get("preco_venda")),
                str(int(float(produto.get("quantidade_estoque") or 0))),
                "Já vinculado" if str(produto.get("vinculado") or FLAG_NAO).upper() == FLAG_SIM else "Disponível",
            ]
            for column, valor in enumerate(valores):
                set_table_item(self.tableProdutos, row, column, valor)

        if self.tableProdutos.rowCount() > 0:
            self.tableProdutos.selectRow(0)

    def _carregar_itens_vinculados(self) -> None:
        self._itens_vinculados = PromocaoService.listar_itens_promocao(self.promocao_id)
        self.tableItensVinculados.setRowCount(len(self._itens_vinculados))
        for row, item in enumerate(self._itens_vinculados):
            valores = [
                str(item.get("produto") or "-"),
                self._formatar_regra_item(item),
                formatar_moeda(item.get("preco_original")),
                formatar_moeda(item.get("preco_promocional")),
                formatar_moeda(item.get("desconto_aplicado")),
                self._formatar_desconto_percentual(item),
                str(item.get("observacao") or "-"),
            ]
            for column, valor in enumerate(valores):
                set_table_item(self.tableItensVinculados, row, column, valor)

        if self.tableItensVinculados.rowCount() > 0:
            self.tableItensVinculados.selectRow(0)

    def _vincular_produto(self) -> None:
        rows = sorted({index.row() for index in self.tableProdutos.selectionModel().selectedRows()})
        if not rows:
            mostrar_aviso(self, "Promoções", "Selecione um ou mais produtos para vincular.")
            return

        tipo_item = None
        valor_item = None
        preco_personalizado = None
        if not self._check_regra_padrao.isChecked():
            tipo_item = str(self._combo_regra_item.currentData() or "")
            valor_item = float(self._spin_valor_regra.value())
            preco_personalizado = valor_item if tipo_item == "NOVO_PRECO" else None

        sucessos = 0
        erros: list[str] = []
        for row in rows:
            produto = self._produtos_encontrados[row]
            sucesso, mensagem = PromocaoService.vincular_produto(
                promocao_id=self.promocao_id,
                produto_id=int(produto.get("id") or 0),
                observacao="",
                preco_personalizado=preco_personalizado,
                tipo_desconto_item=tipo_item,
                valor_desconto_item=valor_item,
            )
            if sucesso:
                sucessos += 1
            else:
                erros.append(f"{produto.get('nome') or 'Produto'}: {mensagem}")

        if sucessos:
            mostrar_info(self, "Promoções", f"{sucessos} produto(s) vinculado(s) à promoção.")
        if erros:
            mostrar_aviso(self, "Produtos não vinculados", "\n".join(erros[:5]))
        self._spin_valor_regra.setValue(0.00)
        self._carregar_produtos()
        self._carregar_itens_vinculados()

    def _alternar_regra_item(self, usar_padrao: bool) -> None:
        self._label_regra_item.setVisible(not usar_padrao)
        self._combo_regra_item.setVisible(not usar_padrao)
        self._spin_valor_regra.setVisible(not usar_padrao)

    def _atualizar_formato_regra_item(self) -> None:
        tipo = str(self._combo_regra_item.currentData() or "")
        if tipo == "PERCENTUAL":
            self._spin_valor_regra.setPrefix("")
            self._spin_valor_regra.setSuffix(" %")
        else:
            self._spin_valor_regra.setPrefix("R$ ")
            self._spin_valor_regra.setSuffix("")

    @staticmethod
    def _formatar_regra_item(item: dict[str, Any]) -> str:
        tipo = str(item.get("tipo_desconto_item") or "").upper()
        if not tipo:
            tipo = "PADRÃO"
        if tipo == "PERCENTUAL":
            return f"{float(item.get('desconto_percentual_item') or 0):.2f}%".replace(".", ",")
        if tipo == "VALOR":
            return f"R$ {float(item.get('desconto_valor_item') or 0):.2f}".replace(".", ",")
        if tipo in ("PRECO_FIXO", "NOVO_PRECO"):
            return f"Preço R$ {float(item.get('preco_fixo_item') or item.get('preco_promocional') or 0):.2f}".replace(".", ",")
        return "Padrão da promoção"

    @staticmethod
    def _formatar_desconto_percentual(item: dict[str, Any]) -> str:
        try:
            preco_original = float(item.get("preco_original") or 0)
            preco_promocional = float(item.get("preco_promocional") or 0)
        except (TypeError, ValueError):
            return "-"
        if preco_original <= 0:
            return "-"
        percentual = max(0.0, (preco_original - preco_promocional) / preco_original * 100)
        return f"{percentual:.2f}%".replace(".", ",")

    def _remover_produto(self) -> None:
        row = self.tableItensVinculados.currentRow()
        if row < 0 or row >= len(self._itens_vinculados):
            mostrar_aviso(self, "Promoções", "Selecione um vínculo para remover.")
            return

        item = self._itens_vinculados[row]
        produto_nome = str(item.get("produto") or "produto")
        produto_id = int(item.get("produto_id") or 0)
        if produto_id <= 0:
            mostrar_aviso(self, "Promoções", "Não foi possível identificar o produto selecionado.")
            return

        sucesso, mensagem = PromocaoService.remover_vinculo_produto(self.promocao_id, produto_id)
        if not sucesso:
            mostrar_aviso(self, "Promoções", mensagem)
            return

        mostrar_info(self, "Promoções", f"{produto_nome}: {mensagem}")
        self._carregar_produtos()
        self._carregar_itens_vinculados()

    @staticmethod
    def _label_tipo(tipo: str) -> str:
        mapa = {
            "PERCENTUAL": "Desconto por percentual",
            "VALOR": "Desconto por valor",
            "PRECO_FIXO": "Preço promocional",
            "NOVO_PRECO": "Novo preço por produto",
            "POR_PRODUTO": "Regra definida por produto",
        }
        return mapa.get(tipo.strip().upper(), tipo)

    @staticmethod
    def _formatar_regra_promocao(promocao: dict[str, Any]) -> str:
        tipo = str(promocao.get("tipo_desconto") or "").strip().upper()
        try:
            percentual = float(promocao.get("desconto_percentual") or 0)
            valor = float(promocao.get("desconto_valor") or 0)
            preco_fixo = float(promocao.get("preco_fixo") or 0)
        except (TypeError, ValueError):
            percentual = valor = preco_fixo = 0.0

        if tipo == "PERCENTUAL":
            return f"{percentual:.2f}%".replace(".", ",")
        if tipo == "VALOR":
            return f"R$ {valor:.2f}".replace(".", ",")
        if tipo == "PRECO_FIXO":
            return f"Preço final R$ {preco_fixo:.2f}".replace(".", ",")
        if tipo == "NOVO_PRECO":
            return "Preço definido por produto"
        if tipo == "POR_PRODUTO":
            return "Regra definida em cada produto"
        return "-"
