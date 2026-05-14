import re
from itertools import count
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QDateTime, QEvent, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator, QKeyEvent
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QInputDialog,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from modules.admin.services.configuracoes_service import ConfiguracoesService
from modules.produtos.services.produto_service import ProdutoService
from modules.venda.services.cupom_service import (
    aplicar_desconto_item,
    criar_item_cupom,
    definir_quantidade_item,
    desconto_itens_total,
    item_tem_promocao,
    quantidade_total_itens,
    priorizar_desconto_manual_item,
    remover_desconto_item,
    restaurar_preco_promocional_item,
    subtotal_itens,
    total_geral,
)
from modules.venda.views.aplicar_desconto_dialog import AplicarDescontoDialog
from modules.venda.views.consulta_preco_dialog import ConsultaPrecoDialog
from modules.venda.views.confirmar_venda_dialog import ConfirmarVendaDialog
from modules.venda.views.modal_consulta_produto_view import ModalConsultaProdutoView
from modules.venda.views.selecionar_cliente_dialog import SelecionarClienteDialog
from ui.venda.frente_venda import Ui_FrenteVenda
from utils.format_utils import formatar_decimal
from utils.image_utils import atualizar_preview_label
from utils.ui_messages import mostrar_aviso, mostrar_info

class FrenteVendaView(QWidget, Ui_FrenteVenda):
    _sequencia_venda = count(1)
    pagamento_solicitado = pyqtSignal(dict)

    lineEditDescricaoProduto: QLineEdit
    lineEditCodigo: QLineEdit
    lineEditQuantidade: QLineEdit
    lineEditPrecoUnitario: QLineEdit
    lineEditSubtotalItem: QLineEdit
    lineEditDesconto: QLineEdit
    lineEditDescontoItens: QLineEdit
    lineEditDescontoTotal: QLineEdit
    lineEditTotalItens: QLineEdit
    lblImagemProduto: QLabel
    lblTotalAPagarValor: QLabel
    lblStatusVenda: QLabel
    lblDataHora: QLabel
    lblNumVendaValor: QLabel
    lblClienteNome: QLabel
    lblInfoStatusVenda: QLabel
    listaSugestoesProdutos: QListWidget
    tableCupom: QTableWidget
    btnAtalhoF2: Any
    btnAtalhoF3: Any
    btnAtalhoF7: Any
    btnAtalhoF10: Any
    btnAlterarCliente: Any
    btnFecharVenda: Any
    btnCancelarItem: Any
    btnCancelarVenda: Any

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._numero_venda = next(self._sequencia_venda)
        self._produto_atual: Optional[Dict[str, Any]] = None
        self._itens_venda: List[Dict[str, Any]] = []
        self._cliente_atual: Optional[Dict[str, Any]] = None
        self._linha_cupom_selecionada: Optional[int] = None
        self._desconto_global_valor = 0.0
        self._resultados_busca_produto: List[Dict[str, Any]] = []
        self._bloquear_busca_descricao = False
        self._parametros_venda = ConfiguracoesService.carregar_parametros_venda()
        self._parametros_promocoes = ConfiguracoesService.carregar_parametros_promocoes()
        self._cliente_selecionado_manualmente = False

        self._busca_timer = QTimer(self)
        self._busca_timer.setSingleShot(True)
        self._busca_timer.setInterval(180)
        self._busca_timer.timeout.connect(self._executar_busca_produto)

        self._relogio_timer = QTimer(self)
        self._relogio_timer.setInterval(1000)
        self._relogio_timer.timeout.connect(self._atualizar_data_hora)

        self._configurar_interface()
        self._conectar_sinais()
        self._limpar_preview_produto()
        self._configurar_venda_inicial()
        self._atualizar_data_hora()
        self._relogio_timer.start()
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        QTimer.singleShot(0, self.lineEditDescricaoProduto.setFocus)

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        QTimer.singleShot(0, self.lineEditDescricaoProduto.setFocus)
        self.lineEditDescricaoProduto.selectAll()

    def hideEvent(self, a0) -> None:
        super().hideEvent(a0)

    def eventFilter(self, a0, a1) -> bool:
        if not self.isVisible() or a1.type() != QEvent.KeyPress:
            return super().eventFilter(a0, a1)

        if QApplication.activeWindow() is not self:
            return super().eventFilter(a0, a1)

        key_event = a1 if isinstance(a1, QKeyEvent) else None
        if key_event is None:
            return super().eventFilter(a0, a1)

        if a0 is self.lineEditDescricaoProduto and self.listaSugestoesProdutos.isVisible():
            if key_event.key() == Qt.Key_Down:
                self.listaSugestoesProdutos.setFocus()
                if self.listaSugestoesProdutos.currentRow() < 0 and self.listaSugestoesProdutos.count() > 0:
                    self.listaSugestoesProdutos.setCurrentRow(0)
                return True
            if key_event.key() == Qt.Key_Escape:
                self._ocultar_sugestoes_produto()
                return True

        if a0 is self.listaSugestoesProdutos:
            if key_event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self._confirmar_produto_sugerido(self.listaSugestoesProdutos.currentItem())
                return True
            if key_event.key() == Qt.Key_Escape:
                self._ocultar_sugestoes_produto()
                self.lineEditDescricaoProduto.setFocus()
                return True

        from typing import Callable

        mapa: Dict[Qt.Key, Callable[[], None]] = {
            Qt.Key_F3: self._ajustar_quantidade_item,
            Qt.Key_F4: self._abrir_confirmacao_venda,
            Qt.Key_F5: self._cancelar_item_selecionado,
            Qt.Key_F6: self._cancelar_venda,
            Qt.Key_F7: self._abrir_consulta_preco,
            Qt.Key_F10: self._abrir_desconto,
        }
        acao = mapa.get(Qt.Key(key_event.key()))
        if acao:
            acao()
            return True

        return super().eventFilter(a0, a1)

    def _configurar_interface(self) -> None:
        self.setFocusPolicy(Qt.StrongFocus)
        self.lineEditQuantidade.setValidator(QIntValidator(1, 999999, self))
        self.lineEditQuantidade.setText("1")
        self.btnAtalhoF7 = self._criar_botao_atalho("F7  Consulta Preço")
        self.atalhosHLayout.insertWidget(4, self.btnAtalhoF7)
        self.lblSepConsultaPreco = QLabel("|", self.frameAtalhos)
        self.lblSepConsultaPreco.setStyleSheet("color:rgba(255,255,255,30);")
        self.atalhosHLayout.insertWidget(5, self.lblSepConsultaPreco)
        self.listaSugestoesProdutos = QListWidget(self)
        self.listaSugestoesProdutos.setObjectName("listaSugestoesProdutos")
        self.listaSugestoesProdutos.setMaximumHeight(180)
        self.listaSugestoesProdutos.setFocusPolicy(Qt.StrongFocus)
        self.listaSugestoesProdutos.setStyleSheet(
            """
            QListWidget {
                background-color: #ffffff;
                color: #15324c;
                border: 1px solid #2a6fa8;
                border-top: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                font-size: 12px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #2a6fa8;
                color: #ffffff;
            }
            QListWidget::item:hover:!selected {
                background-color: #e8f2fa;
            }
            """
        )
        self.listaSugestoesProdutos.hide()
        self.mainVLayout.insertWidget(3, self.listaSugestoesProdutos)
        self.rightPanelVLayout.setStretch(0, 5)
        self.rightPanelVLayout.setStretch(1, 2)

    def _criar_botao_atalho(self, texto: str) -> QPushButton:
        botao = QPushButton(texto, self.frameAtalhos)
        botao.setAutoDefault(False)
        botao.setDefault(False)
        return botao

    def _conectar_sinais(self) -> None:
        self.lineEditDescricaoProduto.textChanged.connect(self._agendar_busca_produto)
        self.lineEditDescricaoProduto.returnPressed.connect(self._adicionar_produto_pelo_enter)
        self.listaSugestoesProdutos.itemClicked.connect(self._selecionar_produto_sugerido)
        self.listaSugestoesProdutos.itemDoubleClicked.connect(self._confirmar_produto_sugerido)
        self.listaSugestoesProdutos.itemActivated.connect(self._confirmar_produto_sugerido)
        self.lineEditQuantidade.textChanged.connect(self._atualizar_subtotal)
        self.btnAtalhoF2.clicked.connect(self._abrir_consulta_produto)
        self.btnAtalhoF3.clicked.connect(self._ajustar_quantidade_item)
        self.btnAtalhoF7.clicked.connect(self._abrir_consulta_preco)
        self.btnAtalhoF10.clicked.connect(self._abrir_desconto)
        self.btnAlterarCliente.clicked.connect(self._alterar_cliente)
        self.btnFecharVenda.clicked.connect(self._abrir_confirmacao_venda)
        self.btnCancelarItem.clicked.connect(self._cancelar_item_selecionado)
        self.btnCancelarVenda.clicked.connect(self._cancelar_venda)
        self.tableCupom.itemClicked.connect(self._ao_clicar_item_cupom)

    def _configurar_venda_inicial(self) -> None:
        self.lblNumVendaValor.setText(str(self._numero_venda))
        self._cliente_selecionado_manualmente = self._cliente_padrao_venda() == "CONSUMIDOR_FINAL"
        self.lblClienteNome.setText("Consumidor Final" if self._cliente_selecionado_manualmente else "Selecionar cliente")
        self.lineEditDesconto.setText("0,00")
        self.lineEditDescontoItens.setText("0,00")
        self.lineEditDescontoTotal.setText("0,00")
        self.lineEditTotalItens.setText("0")
        self.lblInfoStatusVenda.setText("● Venda em aberto")

    def _abrir_consulta_produto(self) -> None:
        dialog = ModalConsultaProdutoView(self)
        if dialog.exec_() != dialog.Accepted or not dialog.produto_selecionado:
            return

        self._produto_atual = dialog.produto_selecionado
        self._definir_descricao_produto(str(self._produto_atual.get("nome") or ""))
        self._preencher_preview_produto(self._produto_atual)
        self._ocultar_sugestoes_produto()
        self._adicionar_produto_pelo_enter()

    def _abrir_consulta_preco(self) -> None:
        dialog = ConsultaPrecoDialog(self)
        dialog.exec_()

    def _alterar_cliente(self) -> bool:
        dialog = SelecionarClienteDialog(self)
        if dialog.exec_() != dialog.Accepted:
            return False

        self._cliente_atual = dialog.cliente_selecionado
        self._cliente_selecionado_manualmente = True
        if not self._cliente_atual:
            self.lblClienteNome.setText("Consumidor Final")
            return True

        self.lblClienteNome.setText(str(self._cliente_atual.get("nome") or "Consumidor Final"))
        return True

    def _atualizar_data_hora(self) -> None:
        self.lblDataHora.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm:ss"))

    def _extrair_quantidade_descricao(self, termo: str) -> tuple[Optional[int], str]:
        correspondencia = re.match(r"^\s*(\d+)\s*\*\s*(.+?)\s*$", termo)
        if not correspondencia:
            return None, termo.strip()
        return int(correspondencia.group(1)), correspondencia.group(2).strip()

    def _agendar_busca_produto(self) -> None:
        if self._bloquear_busca_descricao:
            return
        quantidade_informada, termo_busca = self._extrair_quantidade_descricao(
            self.lineEditDescricaoProduto.text().strip()
        )
        if quantidade_informada is not None:
            self.lineEditQuantidade.setText(str(quantidade_informada))
        if termo_busca and self._linha_cupom_selecionada is not None:
            self._limpar_selecao_cupom()
        if not termo_busca:
            self._produto_atual = None
            self._resultados_busca_produto = []
            self._ocultar_sugestoes_produto()
            self._limpar_preview_produto()
            return
        self._busca_timer.start()

    def _executar_busca_produto(self) -> None:
        quantidade_informada, termo_busca = self._extrair_quantidade_descricao(
            self.lineEditDescricaoProduto.text().strip()
        )
        if quantidade_informada is not None:
            self.lineEditQuantidade.setText(str(quantidade_informada))
        if not termo_busca:
            self._produto_atual = None
            self._resultados_busca_produto = []
            self._ocultar_sugestoes_produto()
            self._limpar_preview_produto()
            return

        produtos = ProdutoService.buscar_para_venda(termo_busca)
        if not produtos:
            self._produto_atual = None
            self._resultados_busca_produto = []
            self._ocultar_sugestoes_produto()
            self._limpar_preview_produto(manter_descricao=True, mensagem_imagem="Nenhum produto encontrado")
            return

        self._resultados_busca_produto = produtos
        self._produto_atual = produtos[0]
        self._preencher_sugestoes_produto(produtos)
        self._preencher_preview_produto(self._produto_atual)

    def _preencher_sugestoes_produto(self, produtos: List[Dict[str, Any]]) -> None:
        self.listaSugestoesProdutos.clear()
        for produto in produtos[:8]:
            nome = str(produto.get("nome") or "Produto")
            codigo_fabricante = str(produto.get("cod_produto") or "").strip()
            codigo = str(produto.get("codigo_barras") or "---")
            preco = formatar_decimal(produto.get("preco_venda"))
            partes = [nome]
            if codigo_fabricante:
                partes.append(f"Cód. Fab.: {codigo_fabricante}")
            partes.append(f"Cód. Barras: {codigo}")
            partes.append(f"R$ {preco}")
            item = QListWidgetItem("  |  ".join(partes))
            item.setData(Qt.UserRole, dict(produto))
            self.listaSugestoesProdutos.addItem(item)

        if self.listaSugestoesProdutos.count() <= 0:
            self._ocultar_sugestoes_produto()
            return

        self.listaSugestoesProdutos.setCurrentRow(0)
        self.listaSugestoesProdutos.show()

    def _ocultar_sugestoes_produto(self) -> None:
        self.listaSugestoesProdutos.hide()
        self.listaSugestoesProdutos.clear()

    def _definir_descricao_produto(self, descricao: str) -> None:
        self._bloquear_busca_descricao = True
        self.lineEditDescricaoProduto.setText(descricao)
        self._bloquear_busca_descricao = False

    def _selecionar_produto_sugerido(self, item: QListWidgetItem | None) -> None:
        if item is None:
            return
        produto = item.data(Qt.UserRole)
        if not isinstance(produto, dict):
            return
        self._produto_atual = produto
        self._definir_descricao_produto(str(produto.get("nome") or ""))
        self._preencher_preview_produto(produto)

    def _confirmar_produto_sugerido(self, item: QListWidgetItem | None) -> None:
        if item is None:
            return
        self._selecionar_produto_sugerido(item)
        self._ocultar_sugestoes_produto()
        self._adicionar_produto_pelo_enter()

    def _adicionar_produto_pelo_enter(self) -> None:
        quantidade_informada, _ = self._extrair_quantidade_descricao(
            self.lineEditDescricaoProduto.text().strip()
        )
        if self.listaSugestoesProdutos.isVisible() and self.listaSugestoesProdutos.currentItem() is not None:
            self._selecionar_produto_sugerido(self.listaSugestoesProdutos.currentItem())
        else:
            self._executar_busca_produto()
        if not self._produto_atual:
            return

        quantidade = quantidade_informada or int(self.lineEditQuantidade.text().strip() or "1")
        self.lineEditQuantidade.setText(str(quantidade))
        if quantidade <= 0:
            mostrar_aviso(self, "Quantidade invalida", "Informe uma quantidade maior que zero.")
            self.lineEditQuantidade.setFocus()
            return

        produto_id = int(self._produto_atual.get("id") or 0)
        estoque_disponivel = float(self._produto_atual.get("quantidade_estoque") or 0.0)
        quantidade_ja_lancada = sum(
            int(item.get("quantidade") or 0)
            for item in self._itens_venda
            if int(item.get("id") or 0) == produto_id
        )
        quantidade_total_solicitada = quantidade_ja_lancada + quantidade

        if not self._permitir_venda_sem_estoque() and quantidade_total_solicitada > int(estoque_disponivel):
            mostrar_aviso(
                self,
                "Estoque insuficiente",
                (
                    f"O produto possui {int(estoque_disponivel)} unidade(s) em estoque.\n"
                    f"Não é possível lançar {quantidade_total_solicitada} unidade(s) com a política atual."
                ),
            )
            self.lineEditQuantidade.setFocus()
            self.lineEditQuantidade.selectAll()
            return

        self._itens_venda.append(criar_item_cupom(self._produto_atual, quantidade))

        self._reconciliar_precos_promocionais()
        self._renderizar_cupom()
        self._produto_atual = None
        self._resultados_busca_produto = []
        self._ocultar_sugestoes_produto()
        self._limpar_preview_produto()
        self.lineEditDescricaoProduto.setFocus()

    def _preencher_preview_produto(self, produto: Dict[str, Any]) -> None:
        codigo = str(produto.get("codigo_barras") or "")
        preco = float(produto.get("preco_venda") or 0)

        self.lineEditCodigo.setText(codigo)
        if not self.lineEditQuantidade.text().strip():
            self.lineEditQuantidade.setText("1")

        self.lineEditPrecoUnitario.setText(formatar_decimal(preco))
        self._atualizar_subtotal()
        self._atualizar_imagem_produto(produto.get("imagem_path"))

    def _preencher_preview_item_venda(self, item: Dict[str, Any]) -> None:
        self.lineEditCodigo.setText(str(item.get("codigo_barras") or ""))
        self.lineEditQuantidade.setText(str(int(item.get("quantidade") or 1)))
        self.lineEditPrecoUnitario.setText(formatar_decimal(item.get("preco_venda")))
        self.lineEditSubtotalItem.setText(formatar_decimal(item.get("total")))
        self._atualizar_imagem_produto(item.get("imagem_path"))

    def _atualizar_subtotal(self) -> None:
        preco = 0.0
        quantidade = int(self.lineEditQuantidade.text().strip() or "1")
        if self._produto_atual:
            preco = float(self._produto_atual.get("preco_venda") or 0)

        subtotal = preco * quantidade
        texto_valor = formatar_decimal(subtotal)
        self.lineEditSubtotalItem.setText(texto_valor if preco else "")
        if not self._itens_venda:
            self.lblTotalAPagarValor.setText(texto_valor if preco else "0,00")

    def _atualizar_imagem_produto(self, imagem_path: Any) -> None:
        atualizar_preview_label(self.lblImagemProduto, imagem_path)

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        if self._produto_atual:
            self._atualizar_imagem_produto(self._produto_atual.get("imagem_path"))

    def _limpar_preview_produto(
        self,
        manter_descricao: bool = False,
        mensagem_imagem: str = "Imagem do produto",
    ) -> None:
        self.lineEditCodigo.clear()
        if not manter_descricao:
            self.lineEditDescricaoProduto.clear()
        self.lineEditQuantidade.setText("1")
        self.lineEditPrecoUnitario.clear()
        self.lineEditSubtotalItem.clear()
        if not self._itens_venda:
            self.lineEditTotalItens.setText("0")
            self.lblTotalAPagarValor.setText("0,00")
        atualizar_preview_label(self.lblImagemProduto, None, texto_padrao=mensagem_imagem)

    def _ao_clicar_item_cupom(self, item_tabela: QTableWidgetItem) -> None:
        row = item_tabela.row()
        if row < 0 or row >= len(self._itens_venda):
            return
        self._selecionar_item_cupom(row)

    def _selecionar_item_cupom(self, row: int) -> None:
        if row < 0 or row >= len(self._itens_venda):
            return
        self._linha_cupom_selecionada = row
        self._preencher_preview_item_venda(self._itens_venda[row])

    def _obter_linha_item_selecionado(
        self,
        *,
        titulo: str = "Selecionar item",
        mensagem: str = "Selecione um item no cupom antes de continuar.",
        mostrar_mensagem: bool = True,
    ) -> Optional[int]:
        row = self.tableCupom.currentRow()
        if 0 <= row < len(self._itens_venda):
            return row
        if mostrar_mensagem:
            mostrar_info(self, titulo, mensagem)
        return None

    def _sincronizar_item_alterado(self, row: int) -> None:
        self._selecionar_item_cupom(row)
        self._renderizar_cupom()
        self.tableCupom.selectRow(row)

    def _limpar_selecao_cupom(self) -> None:
        self.tableCupom.blockSignals(True)
        self.tableCupom.clearSelection()
        self.tableCupom.setCurrentItem(None)
        self.tableCupom.blockSignals(False)
        self._linha_cupom_selecionada = None
        self._restaurar_preview_contexto()

    def _restaurar_preview_contexto(self) -> None:
        if self._produto_atual and self.lineEditDescricaoProduto.text().strip():
            self._preencher_preview_produto(self._produto_atual)
            return
        self._limpar_preview_produto(manter_descricao=bool(self.lineEditDescricaoProduto.text().strip()))

    def _renderizar_cupom(self) -> None:
        self.tableCupom.setRowCount(len(self._itens_venda))

        for row, item in enumerate(self._itens_venda):
            valores = (
                item["codigo_barras"],
                item["nome"],
                str(item["quantidade"]),
                formatar_decimal(item["preco_venda"]),
                formatar_decimal(item.get("desconto_item") or 0.0),
                formatar_decimal(item["total"]),
            )
            for col, valor in enumerate(valores):
                table_item = QTableWidgetItem(valor)
                if col in (2, 3, 4, 5):
                    table_item.setTextAlignment(int(Qt.AlignRight | Qt.AlignVCenter))
                self.tableCupom.setItem(row, col, table_item)

        desconto_itens = desconto_itens_total(self._itens_venda)
        total_itens = quantidade_total_itens(self._itens_venda)
        valor_total = total_geral(self._itens_venda, self._desconto_global_valor)
        self.lineEditTotalItens.setText(str(total_itens))
        self.lineEditDesconto.setText(formatar_decimal(self._desconto_global_valor))
        self.lineEditDescontoItens.setText(formatar_decimal(desconto_itens))
        self.lineEditDescontoTotal.setText(formatar_decimal(self._desconto_total()))
        self.lblTotalAPagarValor.setText(formatar_decimal(valor_total))
        if self._linha_cupom_selecionada is not None and 0 <= self._linha_cupom_selecionada < len(self._itens_venda):
            self.tableCupom.selectRow(self._linha_cupom_selecionada)
            self._selecionar_item_cupom(self._linha_cupom_selecionada)

    def _cancelar_item_selecionado(self) -> None:
        row = self._obter_linha_item_selecionado(mostrar_mensagem=False)
        if row is None:
            return
        self._itens_venda.pop(row)
        self._linha_cupom_selecionada = None
        self._renderizar_cupom()
        if not self._itens_venda:
            self._limpar_preview_produto()
        else:
            self._restaurar_preview_contexto()

    def _cancelar_venda(self) -> None:
        self._itens_venda.clear()
        self._linha_cupom_selecionada = None
        self._desconto_global_valor = 0.0
        self.tableCupom.setRowCount(0)
        self._cliente_atual = None
        self._cliente_selecionado_manualmente = self._cliente_padrao_venda() == "CONSUMIDOR_FINAL"
        self.lblClienteNome.setText("Consumidor Final" if self._cliente_selecionado_manualmente else "Selecionar cliente")
        self._limpar_preview_produto()

    def _abrir_confirmacao_venda(self) -> None:
        if not self._garantir_cliente_conforme_regra():
            return
        dialog = ConfirmarVendaDialog(
            numero_venda=self._numero_venda,
            cliente_nome=self.lblClienteNome.text().strip() or "Consumidor Final",
            itens_venda=self._itens_venda,
            subtotal=subtotal_itens(self._itens_venda),
            desconto_total=self._desconto_total(),
            total=total_geral(self._itens_venda, self._desconto_global_valor),
            parent=self,
        )
        if dialog.exec_() != dialog.Accepted:
            return
        self.pagamento_solicitado.emit(
            {
                "numero_venda": self._numero_venda,
                "cliente_id": self._cliente_atual.get("id") if self._cliente_atual else None,
                "cliente_nome": self.lblClienteNome.text().strip() or "Consumidor Final",
                "itens": [dict(item) for item in self._itens_venda],
                "subtotal": subtotal_itens(self._itens_venda),
                "desconto_global": self._desconto_global_valor,
                "desconto_itens": self._desconto_itens_total(),
                "desconto_total": self._desconto_total(),
                "total": total_geral(self._itens_venda, self._desconto_global_valor),
            }
        )

    def _ajustar_quantidade_item(self) -> None:
        row = self._obter_linha_item_selecionado(
            mensagem="Selecione um item no cupom para alterar a quantidade.",
        )
        if row is None:
            return

        item = self._itens_venda[row]
        quantidade_atual = int(item.get("quantidade") or 1)
        nova_quantidade, confirmado = QInputDialog.getInt(
            self,
            "Alterar quantidade",
            f"Informe a nova quantidade para:\n{item.get('nome')}",
            quantidade_atual,
            1,
            999999,
            1,
        )
        if not confirmado:
            return

        definir_quantidade_item(item, nova_quantidade)
        self._reconciliar_precos_promocionais()
        self._sincronizar_item_alterado(row)

    def _abrir_desconto(self) -> None:
        if self._regra_desconto_venda() == "EXIGIR_AUTORIZACAO":
            senha_admin, confirmado = QInputDialog.getText(
                self,
                "Autorização de desconto",
                "Informe a senha de um administrador para liberar o desconto:",
                QLineEdit.Password,
            )
            if not confirmado:
                return

            from modules.venda.services.caixa_service import CaixaService

            if not CaixaService.validar_admin_para_diferenca(senha_admin):
                mostrar_aviso(
                    self,
                    "Autorização inválida",
                    "Informe uma senha de administrador válida para aplicar ou remover descontos.",
                )
                return

        dialog = AplicarDescontoDialog(
            item_disponivel=0 <= self.tableCupom.currentRow() < len(self._itens_venda),
            parent=self,
        )
        if dialog.exec_() != dialog.Accepted or not dialog.resultado:
            return

        modo = str(dialog.resultado["modo"])
        acao = str(dialog.resultado.get("acao", "aplicar"))
        tipo = str(dialog.resultado.get("tipo", "valor"))
        valor = float(dialog.resultado.get("valor", 0.0))

        if modo == "item":
            row = self._obter_linha_item_selecionado(
                mensagem="Selecione um item no cupom para aplicar desconto no item.",
            )
            if row is None:
                return

            item = self._itens_venda[row]
            if acao == "remover":
                remover_desconto_item(item)
                self._reconciliar_precos_promocionais()
                self._sincronizar_item_alterado(row)
                return

            if self._prioridade_promocional() == "DESCONTO_ANTES_PROMOCAO":
                priorizar_desconto_manual_item(item)

            subtotal_bruto = float(item["preco_venda"]) * float(item["quantidade"])
            desconto = self._calcular_desconto(subtotal_bruto, tipo, valor)
            if desconto >= subtotal_bruto:
                mostrar_aviso(
                    self,
                    "Desconto inválido",
                    "O desconto do item não pode ser maior ou igual ao valor do item.",
                )
                return

            aplicar_desconto_item(item, desconto)
            self._reconciliar_precos_promocionais()
            self._sincronizar_item_alterado(row)
            return

        if acao == "remover":
            self._desconto_global_valor = 0.0
            self._reconciliar_precos_promocionais()
            self._renderizar_cupom()
            return

        if self._prioridade_promocional() == "DESCONTO_ANTES_PROMOCAO":
            for item in self._itens_venda:
                priorizar_desconto_manual_item(item)

        subtotal_venda = subtotal_itens(self._itens_venda)
        if subtotal_venda <= 0:
            mostrar_info(
                self,
                "Venda vazia",
                "Adicione itens antes de aplicar desconto.",
            )
            return

        desconto_global = self._calcular_desconto(subtotal_venda, tipo, valor)
        if desconto_global >= subtotal_venda:
            mostrar_aviso(
                self,
                "Desconto inválido",
                "O desconto da venda não pode ser maior ou igual ao total atual.",
            )
            return

        self._desconto_global_valor = desconto_global
        self._reconciliar_precos_promocionais()
        self._renderizar_cupom()

    def _desconto_itens_total(self) -> float:
        return desconto_itens_total(self._itens_venda)

    def _desconto_total(self) -> float:
        return self._desconto_itens_total() + float(self._desconto_global_valor)

    @staticmethod
    def _calcular_desconto(base: float, tipo: str, valor: float) -> float:
        if tipo == "percentual":
            return round(base * (valor / 100.0), 2)
        return round(valor, 2)

    def _cliente_padrao_venda(self) -> str:
        return str(self._parametros_venda.get("cliente_padrao_venda") or "CONSUMIDOR_FINAL").strip().upper()

    def _regra_desconto_venda(self) -> str:
        return str(self._parametros_venda.get("regra_desconto_venda") or "PERMITIR_DESCONTO").strip().upper()

    def _permitir_venda_sem_estoque(self) -> bool:
        return bool(self._parametros_venda.get("permitir_venda_sem_estoque", False))

    def _prioridade_promocional(self) -> str:
        return str(
            self._parametros_promocoes.get("prioridade_promocional")
            or "PROMOCAO_ANTES_DESCONTO"
        ).strip().upper()

    def _reconciliar_precos_promocionais(self) -> None:
        if self._prioridade_promocional() != "DESCONTO_ANTES_PROMOCAO":
            return

        desconto_global_ativo = float(self._desconto_global_valor or 0.0) > 0
        for item in self._itens_venda:
            if not item_tem_promocao(item):
                continue
            if desconto_global_ativo or float(item.get("desconto_item") or 0.0) > 0:
                priorizar_desconto_manual_item(item)
            else:
                restaurar_preco_promocional_item(item)

    def _garantir_cliente_conforme_regra(self) -> bool:
        if self._cliente_padrao_venda() != "SELECIONAR_NO_MOMENTO":
            return True
        if self._cliente_selecionado_manualmente:
            return True

        mostrar_info(
            self,
            "Selecionar cliente",
            "Selecione o cliente da venda antes de continuar.",
        )
        return self._alterar_cliente()
