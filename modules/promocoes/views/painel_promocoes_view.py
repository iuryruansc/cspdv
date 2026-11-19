from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QColor, QBrush, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QSizePolicy,
)

from modules.promocoes.services.promocao_service import PromocaoService
from modules.promocoes.views.cadastro_promocao_view import CadastroPromocaoView
from modules.promocoes.views.vincular_produtos_promocao_dialog import VincularProdutosPromocaoDialog
from modules.produtos.models.produto_model import ProdutoModel
from modules.produtos.views.detalhes_produto_dialog import DetalhesProdutoDialog
from modules.shared.constants import (
    STATUS_PROMOCAO_AGENDADA,
    STATUS_PROMOCAO_ATIVA,
    STATUS_PROMOCAO_CANCELADA,
    STATUS_PROMOCAO_EDITAVEL,
    STATUS_PROMOCAO_ENCERRADA,
    STATUS_PROMOCAO_RASCUNHO,
)
from ui.promocoes.painel_promocoes import Ui_PainelPromocoes
from utils.format_utils import formatar_moeda
from utils.operational_panel_mixin import PainelOperacionalMixin
from utils.table_widget_utils import set_table_item
from utils.ui_messages import confirmar_acao, mostrar_aviso, mostrar_info

class PainelPromocoesView(QMainWindow, Ui_PainelPromocoes, PainelOperacionalMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.txtBuscaPromocao: QLineEdit
        self.cmbStatusFiltro: QComboBox
        self.cmbTipoFiltro: QComboBox
        self.tablePromocoes: QTableWidget
        self.tableItensPromocao: QTableWidget
        self.lblPromocoesAtivasValor: QLabel
        self.lblAgendadasValor: QLabel
        self.lblProdutosPromocaoValor: QLabel
        self.lblEncerradasValor: QLabel
        self._promocoes_base: list[dict[str, Any]] = []
        self._promocoes_filtradas: list[dict[str, Any]] = []
        self._filtro_card = ""
        self._itens_promocao_atual: list[dict[str, Any]] = []
        self._cadastro_promocao_dialog = None
        self._vincular_produtos_dialog = None

        self.setMinimumSize(0, 0)
        self._configurar_tamanho_responsivo()
        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
        self._configurar_tabelas()
        self._conectar_eventos()
        self._configurar_melhorias_ui()
        self._configurar_toolbar_responsiva()
        self._configurar_navegacao()
        self._carregar_dados()

    def _configurar_melhorias_ui(self) -> None:
        self.btnLimparFiltros = QPushButton("Limpar filtros", self.toolbarCard)
        self.btnLimparFiltros.setObjectName("btnLimparFiltros")
        self.btnLimparFiltros.setToolTip("Remove a busca e os filtros aplicados.")
        self.btnLimparFiltros.setStyleSheet(
            "QPushButton { background:#f7fafc; color:#315676; border:1px solid #c8d7e6; } "
            "QPushButton:hover { background:#e8f1f8; }"
        )
        self.toolbarLayout.insertWidget(3, self.btnLimparFiltros)
        self.btnLimparFiltros.clicked.connect(self._limpar_filtros)

        self.cmbPeriodoFiltro = QComboBox(self.toolbarCard)
        self.cmbPeriodoFiltro.setObjectName("cmbPeriodoFiltro")
        self.cmbPeriodoFiltro.addItems(
            ["Todos os períodos", "Vigentes hoje", "Próximas promoções", "Período encerrado"]
        )
        self.cmbPeriodoFiltro.setToolTip("Filtre as promoções pela situação da vigência.")
        self.toolbarLayout.insertWidget(3, self.cmbPeriodoFiltro)
        self.cmbPeriodoFiltro.currentIndexChanged.connect(self._aplicar_filtros)

        for texto in ("Rascunhos", "Canceladas"):
            if self.cmbStatusFiltro.findText(texto) < 0:
                self.cmbStatusFiltro.addItem(texto)

        self._adicionar_separadores_toolbar()

        self.cardProblemas, self.lblProblemasValor = self._criar_card_problemas()
        self.cardsLayout.addWidget(self.cardProblemas)
        self.cardProblemas.installEventFilter(self)
        self.cardProblemas.setCursor(Qt.PointingHandCursor)
        self.cardProblemas.setToolTip("Mostrar promoções sem produtos ou com vigência inválida.")

        self.lblResumoPromocao = QLabel("Selecione uma promoção para visualizar o resumo.", self.framePromocoes)
        self.lblResumoPromocao.setWordWrap(True)
        self.lblResumoPromocao.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.lblResumoPromocao.setStyleSheet(
            "background:#f2f7fb; color:#315676; border:1px solid #d6e2ec; "
            "border-radius:8px; padding:8px 10px; font-size:11px;"
        )
        self.framePromocoesLayout.insertWidget(2, self.lblResumoPromocao)

        self.lblPromocoesVazio = QLabel(
            "Nenhuma promoção encontrada. Ajuste os filtros ou crie uma nova promoção.",
            self.framePromocoes,
        )
        self.lblPromocoesVazio.setAlignment(Qt.AlignCenter)
        self.lblPromocoesVazio.setWordWrap(True)
        self.lblPromocoesVazio.setStyleSheet("color:#65829b; padding:18px; font-size:12px;")
        self.framePromocoesLayout.insertWidget(4, self.lblPromocoesVazio)

        self.lblItensVazio = QLabel(
            "Selecione uma promoção para visualizar os produtos vinculados.",
            self.frameAgenda,
        )
        self.lblItensVazio.setAlignment(Qt.AlignCenter)
        self.lblItensVazio.setWordWrap(True)
        self.lblItensVazio.setStyleSheet("color:#65829b; padding:18px; font-size:12px;")
        self.frameAgendaLayout.insertWidget(2, self.lblItensVazio)

        self.btnDetalhesProduto = QPushButton("Ver detalhes do produto", self.frameAgenda)
        self.btnDetalhesProduto.setObjectName("btnDetalhesProduto")
        self.btnDetalhesProduto.setEnabled(False)
        self.btnDetalhesProduto.setToolTip("Selecione um produto vinculado para consultar seus detalhes.")
        self.frameAgendaLayout.addWidget(self.btnDetalhesProduto)
        self.btnDetalhesProduto.clicked.connect(self._abrir_detalhes_produto_vinculado)
        self.tableItensPromocao.itemSelectionChanged.connect(self._atualizar_estado_detalhes_produto)

        for card in (
            self.cardPromocoesAtivas,
            self.cardAgendadas,
            self.cardProdutosPromocao,
            self.cardEncerradas,
        ):
            card.installEventFilter(self)
            card.setCursor(Qt.PointingHandCursor)
        self.cardPromocoesAtivas.setToolTip("Filtrar promoções ativas.")
        self.cardAgendadas.setToolTip("Filtrar promoções agendadas.")
        self.cardProdutosPromocao.setToolTip("Mostrar apenas promoções com produtos vinculados.")
        self.cardEncerradas.setToolTip("Filtrar promoções encerradas.")

        self.framePromocoes.setMinimumWidth(0)
        self.frameAgenda.setMinimumWidth(250)
        self.frameAgenda.setMaximumWidth(460)
        self.mainGridLayout.setSpacing(10)
        self.cardsLayout.setSpacing(10)

    def _configurar_toolbar_responsiva(self) -> None:
        """Mantém a barra de ações dentro da largura disponível da tela."""
        self.toolbarLayout.setContentsMargins(8, 8, 8, 8)
        self.toolbarLayout.setSpacing(6)

        self.txtBuscaPromocao.setMinimumWidth(180)
        self.txtBuscaPromocao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        for label, largura in (
            (self.lblOperadorInfo, 125),
            (self.lblDataHora, 155),
        ):
            label.setFixedWidth(largura)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.btnVoltarSelecao.setFixedWidth(120)

        for combo, largura in (
            (self.cmbStatusFiltro, 125),
            (self.cmbTipoFiltro, 145),
            (self.cmbPeriodoFiltro, 145),
        ):
            combo.setMinimumWidth(0)
            combo.setFixedWidth(largura)

        for botao, largura in (
            (self.btnLimparFiltros, 125),
            (self.btnAtualizar, 82),
            (self.btnNovaPromocao, 140),
            (self.btnDuplicarPromocao, 105),
            (self.btnEncerrarPromocao, 100),
            (self.btnCancelarPromocao, 100),
            (self.btnVincularProdutos, 150),
        ):
            botao.setMinimumWidth(0)
            botao.setFixedWidth(largura)

        self.framePromocoes.setMinimumWidth(0)
        self.frameAgenda.setMinimumWidth(500)
        self.frameAgenda.setMaximumWidth(620)

    def _configurar_navegacao(self) -> None:
        self.btnVisaoGeral = QPushButton("Visão geral", self.frameHeader)
        self.btnVisaoGeral.setObjectName("btnVisaoGeral")
        self.btnVisaoGeral.setToolTip("Visualizar as promoções sem ações administrativas.")
        self.btnVisaoGeral.setStyleSheet(
            "QPushButton { background:#e8f1f8; color:#174d78; border:1px solid #b8d3e8; "
            "border-radius:8px; padding:8px 12px; font-weight:700; } "
            "QPushButton:hover { background:#d8e9f5; }"
        )
        self.btnVisaoGeral.setFixedWidth(120)
        self.headerHLayout.insertWidget(4, self.btnVisaoGeral)
        self.btnVisaoGeral.clicked.connect(self._abrir_visao_geral)

    def _abrir_visao_geral(self) -> None:
        from modules.promocoes.views.visao_geral_promocoes_view import VisaoGeralPromocoesView

        self._janela_navegacao = VisaoGeralPromocoesView()
        self._janela_navegacao.showMaximized()
        self.hide()

    def _adicionar_separadores_toolbar(self) -> None:
        for index in (4, 7, 10):
            separador = QFrame(self.toolbarCard)
            separador.setFrameShape(QFrame.VLine)
            separador.setFrameShadow(QFrame.Sunken)
            separador.setStyleSheet("color:#c8d7e6;")
            self.toolbarLayout.insertWidget(index, separador)

    def _criar_card_problemas(self):
        card = QFrame(self)
        card.setObjectName("cardProblemas")
        card.setMinimumHeight(92)
        card.setStyleSheet(
            "QFrame#cardProblemas { background:#fff3cd; border:1px solid #f0c36d; border-radius:10px; }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        valor = QLabel("0", card)
        valor.setStyleSheet("color:#8a4b00; font-size:27px; font-weight:700;")
        titulo = QLabel("Promoções com atenção", card)
        titulo.setStyleSheet("color:#8a4b00; font-size:11px; font-weight:600;")
        layout.addWidget(valor)
        layout.addWidget(titulo)
        return card, valor

    def _configurar_tabelas(self) -> None:
        header_promocoes = self.tablePromocoes.horizontalHeader()
        header_promocoes.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_promocoes.setSectionResizeMode(1, QHeaderView.Stretch)
        header_promocoes.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_promocoes.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_promocoes.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_promocoes.setSectionResizeMode(5, QHeaderView.Stretch)
        header_promocoes.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header_promocoes.setStretchLastSection(False)
        self.tablePromocoes.setTextElideMode(Qt.ElideNone)
        self.tablePromocoes.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tablePromocoes.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        header_itens = self.tableItensPromocao.horizontalHeader()
        header_itens.setSectionResizeMode(0, QHeaderView.Stretch)
        header_itens.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_itens.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_itens.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_itens.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_itens.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_itens.setStretchLastSection(False)
        self.tableItensPromocao.setTextElideMode(Qt.ElideNone)
        self.tableItensPromocao.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tableItensPromocao.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def _conectar_eventos(self) -> None:
        self.btnAtualizar.clicked.connect(self._abrir_editar_promocao)
        self.btnNovaPromocao.clicked.connect(self._abrir_nova_promocao)
        self.btnDuplicarPromocao.clicked.connect(self._duplicar_promocao)
        self.btnEncerrarPromocao.clicked.connect(self._encerrar_promocao)
        self.btnCancelarPromocao.clicked.connect(self._cancelar_promocao)
        self.btnVincularProdutos.clicked.connect(self._abrir_vincular_produtos)
        self.txtBuscaPromocao.returnPressed.connect(self._aplicar_filtros)
        self.txtBuscaPromocao.textChanged.connect(self._aplicar_filtros)
        self.cmbStatusFiltro.currentIndexChanged.connect(self._aplicar_filtros)
        self.cmbTipoFiltro.currentIndexChanged.connect(self._aplicar_filtros)
        self.tablePromocoes.itemSelectionChanged.connect(self._popular_itens_da_promocao)
        self.tablePromocoes.itemSelectionChanged.connect(self._atualizar_estado_acoes)

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.MouseButtonRelease:
            card_status = {
                self.cardPromocoesAtivas: STATUS_PROMOCAO_ATIVA,
                self.cardAgendadas: STATUS_PROMOCAO_AGENDADA,
                self.cardEncerradas: STATUS_PROMOCAO_ENCERRADA,
            }.get(watched)
            if card_status:
                self._alternar_filtro_card_status(card_status)
                return True
            if watched is self.cardProdutosPromocao:
                self._filtro_card = "" if self._filtro_card == "produtos" else "produtos"
                self._aplicar_filtros()
                return True
            if watched is getattr(self, "cardProblemas", None):
                self._filtro_card = "" if self._filtro_card == "problemas" else "problemas"
                self._aplicar_filtros()
                return True
        return super().eventFilter(watched, event)

    def _alternar_filtro_card_status(self, status: str) -> None:
        texto = self._label_status(status)
        if self._filtro_card == status:
            self._filtro_card = ""
            self.cmbStatusFiltro.setCurrentIndex(0)
            return
        self._filtro_card = status
        self.cmbStatusFiltro.setCurrentText(texto + "s" if status != STATUS_PROMOCAO_ATIVA else "Ativas")
        self._aplicar_filtros()

    def _limpar_filtros(self) -> None:
        self._filtro_card = ""
        self.txtBuscaPromocao.clear()
        self.cmbStatusFiltro.setCurrentIndex(0)
        self.cmbTipoFiltro.setCurrentIndex(0)
        self.cmbPeriodoFiltro.setCurrentIndex(0)

    def _carregar_dados(self) -> None:
        self.lblStatusBar.setText("CSPdv - Módulo de Promoções | Carregando promoções...")
        self.tablePromocoes.setEnabled(False)
        try:
            self._promocoes_base = PromocaoService.listar_promocoes()
        except Exception as exc:
            self._promocoes_base = []
            mostrar_aviso(self, "Promoções", f"Não foi possível carregar as promoções.\n\nDetalhes: {exc}")
        finally:
            self.tablePromocoes.setEnabled(True)
        self._aplicar_filtros()

    def _aplicar_filtros(self) -> None:
        busca = self.txtBuscaPromocao.text().strip().lower()
        status = self._mapear_status_filtro(self.cmbStatusFiltro.currentText())
        tipo = self._mapear_tipo_filtro(self.cmbTipoFiltro.currentText())
        periodo = self.cmbPeriodoFiltro.currentIndex()

        self._promocoes_filtradas = []
        for promocao in self._promocoes_base:
            status_promocao = self._status_normalizado(promocao)
            tipo_promocao = str(promocao.get("tipo_desconto", "")).strip().upper()

            if status and status_promocao != status:
                continue
            if tipo and tipo_promocao != tipo:
                continue
            if self._filtro_card == "produtos" and int(promocao.get("qtd_produtos") or 0) <= 0:
                continue
            if self._filtro_card == "problemas" and not self._promocao_tem_problema(promocao):
                continue
            if not self._corresponde_periodo(promocao, periodo):
                continue

            texto_base = " ".join(
                [
                    str(promocao.get("codigo", "")),
                    str(promocao.get("nome", "")),
                    str(promocao.get("tipo_desconto", "")),
                    str(promocao.get("status", "")),
                    self._regra_exibicao(promocao),
                ]
            ).lower()
            if busca and busca not in texto_base:
                continue

            self._promocoes_filtradas.append(promocao)

        self._renderizar_promocoes()
        self._atualizar_metricas()

    def _renderizar_promocoes(self) -> None:
        self.tablePromocoes.setRowCount(len(self._promocoes_filtradas))
        self.lblPromocoesVazio.setVisible(not self._promocoes_filtradas)
        self.tablePromocoes.setVisible(bool(self._promocoes_filtradas))
        for row, promocao in enumerate(self._promocoes_filtradas):
            valores = [
                str(promocao.get("codigo") or "-"),
                str(promocao.get("nome") or "-"),
                self._label_tipo(str(promocao.get("tipo_desconto") or "-")),
                str(promocao.get("vigencia") or "-"),
                self._label_status(str(promocao.get("status") or "-")),
                self._regra_exibicao(promocao),
                str(promocao.get("qtd_produtos") or "0"),
            ]
            tooltip = (
                f"Código: {promocao.get('codigo') or '-'}\n"
                f"Promoção: {promocao.get('nome') or '-'}\n"
                f"Tipo: {self._label_tipo(str(promocao.get('tipo_desconto') or '-'))}\n"
                f"Status: {self._label_status(str(promocao.get('status') or '-'))}\n"
                f"Vigência: {promocao.get('vigencia') or '-'}\n"
                f"Regra: {self._regra_exibicao(promocao)}\n"
                f"Produtos: {promocao.get('qtd_produtos') or '0'}"
            )
            for column, value in enumerate(valores):
                item = set_table_item(self.tablePromocoes, row, column, value)
                item.setToolTip(tooltip)
                if column == 2:
                    self._aplicar_estilo_tipo(item, str(promocao.get("tipo_desconto") or ""))
                if column == 3:
                    self._aplicar_estilo_vigencia(item, str(promocao.get("status") or ""))
                if column == 4:
                    self._aplicar_estilo_status(item, str(promocao.get("status") or ""))

        if self.tablePromocoes.rowCount() > 0:
            self.tablePromocoes.selectRow(0)
        else:
            self._itens_promocao_atual = []
            self.btnDetalhesProduto.setEnabled(False)
            self.tableItensPromocao.setRowCount(0)
            self.tableItensPromocao.hide()
            self.lblItensVazio.show()
            self.lblResumoPromocao.setText("Nenhuma promoção encontrada para os filtros atuais.")
            self.lblStatusBar.setText("CSPdv - Módulo de Promoções | Nenhuma promoção encontrada para os filtros atuais")
        self._atualizar_estado_acoes()

    def _atualizar_metricas(self) -> None:
        total_ativas = sum(
            1 for promocao in self._promocoes_base if self._status_normalizado(promocao) == STATUS_PROMOCAO_ATIVA
        )
        total_agendadas = sum(
            1 for promocao in self._promocoes_base if self._status_normalizado(promocao) == STATUS_PROMOCAO_AGENDADA
        )
        total_encerradas = sum(
            1 for promocao in self._promocoes_base if self._status_normalizado(promocao) == STATUS_PROMOCAO_ENCERRADA
        )
        total_itens = sum(int(promocao.get("qtd_produtos") or 0) for promocao in self._promocoes_base)

        self.lblPromocoesAtivasValor.setText(str(total_ativas))
        self.lblAgendadasValor.setText(str(total_agendadas))
        self.lblProdutosPromocaoValor.setText(str(total_itens))
        self.lblEncerradasValor.setText(str(total_encerradas))
        self.lblProblemasValor.setText(str(sum(1 for p in self._promocoes_base if self._promocao_tem_problema(p))))
        self._restaurar_status_padrao()

    def _popular_itens_da_promocao(self) -> None:
        promocao = self._obter_promocao_selecionada()
        if not promocao:
            self._itens_promocao_atual = []
            self.btnDetalhesProduto.setEnabled(False)
            self.tableItensPromocao.setRowCount(0)
            self.tableItensPromocao.hide()
            self.lblItensVazio.show()
            self.lblResumoPromocao.setText("Selecione uma promoção para visualizar o resumo.")
            self._restaurar_status_padrao()
            return

        itens_db = PromocaoService.listar_itens_promocao(int(promocao.get("id") or 0))
        self._itens_promocao_atual = list(itens_db)
        self.tableItensPromocao.setRowCount(len(itens_db))
        self.tableItensPromocao.setVisible(bool(itens_db))
        self.lblItensVazio.setVisible(not itens_db)
        self.btnDetalhesProduto.setEnabled(bool(itens_db))
        for row, item in enumerate(itens_db):
            valores = [
                str(item.get("produto") or "-"),
                formatar_moeda(item.get("preco_original")),
                formatar_moeda(item.get("preco_promocional")),
                self._formatar_desconto(item),
                self._formatar_desconto_percentual(item),
                str(item.get("observacao") or "-"),
            ]
            for column, valor in enumerate(valores):
                cell = set_table_item(self.tableItensPromocao, row, column, valor)
                cell.setToolTip(str(item.get("produto") or "Produto vinculado"))
        self._atualizar_status_promocao_selecionada(promocao, len(itens_db))

    def _atualizar_resumo_promocao(self, promocao: dict[str, Any] | None) -> None:
        if not promocao:
            self.lblResumoPromocao.setText("Selecione uma promoção para visualizar o resumo.")
            return
        tipo = self._label_tipo(str(promocao.get("tipo_desconto") or "-"))
        status = self._label_status(str(promocao.get("status") or "-"))
        regra = self._regra_exibicao(promocao)
        self.lblResumoPromocao.setText(
            f"<b>{promocao.get('nome') or promocao.get('codigo') or 'Promoção'}</b>  •  "
            f"Status: <b>{status}</b>  •  Tipo: {tipo}<br>"
            f"Vigência: {promocao.get('vigencia') or '-'}  •  Regra: {regra}  •  "
            f"Produtos vinculados: <b>{int(promocao.get('qtd_produtos') or 0)}</b>"
        )

    def _atualizar_estado_detalhes_produto(self) -> None:
        row = self.tableItensPromocao.currentRow()
        produto_id = 0
        if 0 <= row < len(self._itens_promocao_atual):
            produto_id = int(self._itens_promocao_atual[row].get("produto_id") or 0)
        self.btnDetalhesProduto.setEnabled(produto_id > 0)

    def _abrir_detalhes_produto_vinculado(self) -> None:
        row = self.tableItensPromocao.currentRow()
        if row < 0 or row >= len(self._itens_promocao_atual):
            mostrar_aviso(self, "Promoções", "Selecione um produto vinculado.")
            return
        produto_id = int(self._itens_promocao_atual[row].get("produto_id") or 0)
        produto = ProdutoModel.buscar_por_id(produto_id) if produto_id else None
        if not produto:
            mostrar_aviso(self, "Promoções", "Não foi possível localizar os detalhes deste produto.")
            return
        DetalhesProdutoDialog(produto, self).exec_()

    def _abrir_nova_promocao(self) -> None:
        self._cadastro_promocao_dialog = CadastroPromocaoView(self)
        if self._cadastro_promocao_dialog.exec_():
            self._carregar_dados()

    def _abrir_editar_promocao(self) -> None:
        promocao = self._obter_promocao_selecionada()
        if not promocao:
            mostrar_aviso(self, "Promoções", "Selecione uma promoção antes de editar.")
            return

        promocao_id = int(promocao.get("id") or 0)
        self._cadastro_promocao_dialog = CadastroPromocaoView(self, promocao_id=promocao_id)
        if self._cadastro_promocao_dialog.exec_():
            self._carregar_dados()
            self._restaurar_promocao_por_id(promocao_id)

    def _abrir_vincular_produtos(self) -> None:
        promocao = self._obter_promocao_selecionada()
        if not promocao:
            mostrar_aviso(self, "Promoções", "Selecione uma promoção antes de vincular produtos.")
            return

        promocao_id = int(promocao.get("id") or 0)
        self._vincular_produtos_dialog = VincularProdutosPromocaoDialog(promocao_id, self)
        self._vincular_produtos_dialog.exec_()
        self._carregar_dados()
        self._restaurar_promocao_por_id(promocao_id)

    def _duplicar_promocao(self) -> None:
        promocao = self._obter_promocao_selecionada()
        if not promocao:
            mostrar_aviso(self, "Promoções", "Selecione uma promoção antes de duplicar.")
            return

        if not confirmar_acao(
            self,
            "Duplicar promoção",
            "Deseja duplicar a promoção selecionada com os produtos já vinculados?",
        ):
            return

        sucesso, mensagem, novo_id = PromocaoService.duplicar_promocao(int(promocao.get("id") or 0))
        if not sucesso or not novo_id:
            mostrar_aviso(self, "Promoções", mensagem)
            return

        novo_id_int = int(novo_id)
        self._carregar_dados()
        self._restaurar_promocao_por_id(novo_id_int)

        self._cadastro_promocao_dialog = CadastroPromocaoView(self, promocao_id=novo_id_int)
        if self._cadastro_promocao_dialog.exec_():
            self._carregar_dados()
            self._restaurar_promocao_por_id(novo_id_int)
            return

        self._carregar_dados()
        self._restaurar_promocao_por_id(novo_id_int)
        mostrar_info(
            self,
            "Promoções",
            f"{mensagem}\n\nA cópia foi aberta para revisão e permaneceu salva em Rascunho.",
        )

    def _encerrar_promocao(self) -> None:
        self._alterar_status_promocao(
            titulo="Encerrar promoção",
            pergunta="Deseja encerrar a promoção selecionada agora?",
            acao=PromocaoService.encerrar_promocao,
        )

    def _cancelar_promocao(self) -> None:
        self._alterar_status_promocao(
            titulo="Cancelar promoção",
            pergunta="Deseja cancelar a promoção selecionada? Esta ação altera o status para Cancelada.",
            acao=PromocaoService.cancelar_promocao,
        )

    def _alterar_status_promocao(self, *, titulo: str, pergunta: str, acao: Callable[[int], tuple[bool, str]]) -> None:
        promocao = self._obter_promocao_selecionada()
        if not promocao:
            mostrar_aviso(self, "Promoções", "Selecione uma promoção antes de continuar.")
            return

        promocao_id = int(promocao.get("id") or 0)
        if promocao_id <= 0:
            mostrar_aviso(self, "Promoções", "Não foi possível identificar a promoção selecionada.")
            return

        nome_promocao = str(promocao.get("nome") or promocao.get("codigo") or "promoção").strip()
        status_atual = self._label_status(str(promocao.get("status") or "-"))
        mensagem_confirmacao = f"{pergunta}\n\nPromoção: {nome_promocao}\nStatus atual: {status_atual}"

        if not confirmar_acao(self, titulo, mensagem_confirmacao):
            return

        sucesso, mensagem = acao(promocao_id)
        if not sucesso:
            mostrar_aviso(self, "Promoções", mensagem)
            return

        self._carregar_dados()
        self._restaurar_promocao_por_id(promocao_id)
        mostrar_info(self, "Promoções", mensagem)

    def _atualizar_estado_acoes(self) -> None:
        promocao = self._obter_promocao_selecionada()
        status = self._status_normalizado(promocao)
        selecionada = promocao is not None

        self.btnAtualizar.setEnabled(selecionada and status in STATUS_PROMOCAO_EDITAVEL)
        self.btnDuplicarPromocao.setEnabled(selecionada)
        self.btnVincularProdutos.setEnabled(selecionada and status in STATUS_PROMOCAO_EDITAVEL)
        self.btnEncerrarPromocao.setEnabled(selecionada and status in {STATUS_PROMOCAO_AGENDADA, STATUS_PROMOCAO_ATIVA})
        self.btnCancelarPromocao.setEnabled(selecionada and status in STATUS_PROMOCAO_EDITAVEL)
        self._atualizar_resumo_promocao(promocao)
        self._atualizar_tooltips_acoes(promocao, status)

    def _obter_promocao_selecionada(self) -> dict[str, Any] | None:
        row = self.tablePromocoes.currentRow()
        if row < 0 or row >= len(self._promocoes_filtradas):
            return None
        return self._promocoes_filtradas[row]

    def _restaurar_promocao_por_id(self, promocao_id: int) -> None:
        if promocao_id <= 0:
            return
        for row, promocao in enumerate(self._promocoes_filtradas):
            if int(promocao.get("id") or 0) == promocao_id:
                self.tablePromocoes.selectRow(row)
                self._popular_itens_da_promocao()
                self._atualizar_estado_acoes()
                break

    @staticmethod
    def _formatar_desconto(item: dict[str, Any]) -> str:
        try:
            desconto = float(item.get("desconto_aplicado") or 0)
        except (TypeError, ValueError):
            desconto = 0.0
        return formatar_moeda(desconto) if desconto > 0 else "-"

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

    @staticmethod
    def _mapear_status_filtro(texto: str) -> str:
        mapa = {
            "RASCUNHOS": STATUS_PROMOCAO_RASCUNHO,
            "ATIVAS": STATUS_PROMOCAO_ATIVA,
            "AGENDADAS": STATUS_PROMOCAO_AGENDADA,
            "ENCERRADAS": STATUS_PROMOCAO_ENCERRADA,
            "CANCELADAS": STATUS_PROMOCAO_CANCELADA,
        }
        return mapa.get(texto.strip().upper(), "")

    @staticmethod
    def _converter_data(valor: Any) -> datetime | None:
        if isinstance(valor, datetime):
            return valor
        if valor is None:
            return None
        texto = str(valor).strip()
        for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
            try:
                return datetime.strptime(texto[:19], formato)
            except ValueError:
                continue
        return None

    @classmethod
    def _corresponde_periodo(cls, promocao: dict[str, Any], filtro: int) -> bool:
        if filtro == 0:
            return True
        agora = datetime.now()
        inicio = cls._converter_data(promocao.get("data_inicio"))
        fim = cls._converter_data(promocao.get("data_fim"))
        status = cls._status_normalizado(promocao)
        if filtro == 1:
            return status == STATUS_PROMOCAO_ATIVA or (inicio is not None and fim is not None and inicio <= agora <= fim)
        if filtro == 2:
            return status == STATUS_PROMOCAO_AGENDADA or (inicio is not None and inicio > agora)
        if filtro == 3:
            return status == STATUS_PROMOCAO_ENCERRADA or (fim is not None and fim < agora)
        return True

    @classmethod
    def _promocao_tem_problema(cls, promocao: dict[str, Any]) -> bool:
        if int(promocao.get("qtd_produtos") or 0) <= 0:
            return True
        inicio = cls._converter_data(promocao.get("data_inicio"))
        fim = cls._converter_data(promocao.get("data_fim"))
        return bool(inicio is None or fim is None or fim <= inicio)

    @classmethod
    def _regra_exibicao(cls, promocao: dict[str, Any]) -> str:
        regra = str(promocao.get("regra_texto") or "").strip()
        if regra:
            return regra
        tipo = str(promocao.get("tipo_desconto") or "").strip().upper()
        if tipo == "PERCENTUAL":
            return f"{promocao.get('desconto_percentual') or 0}% de desconto"
        if tipo == "VALOR":
            return f"{formatar_moeda(promocao.get('desconto_valor'))} de desconto"
        if tipo in {"PRECO_FIXO", "NOVO_PRECO"}:
            return "Preço promocional"
        if tipo == "LEVE_X_PAGUE_Y":
            return "Leve X, pague Y"
        if tipo == "COMBO":
            return "Preço especial para combo"
        if tipo == "DESCONTO_PROGRESSIVO":
            return "Desconto progressivo por quantidade"
        if tipo == "POR_PRODUTO":
            return "Regras individuais por produto"
        return "Regra não informada"

    @staticmethod
    def _mapear_tipo_filtro(texto: str) -> str:
        mapa = {
            "DESCONTO POR PERCENTUAL": "PERCENTUAL",
            "DESCONTO POR VALOR": "VALOR",
            "PREÇO PROMOCIONAL": "PRECO_FIXO",
            "PRECO PROMOCIONAL": "PRECO_FIXO",
            "NOVO PREÇO POR PRODUTO": "NOVO_PRECO",
            "NOVO PRECO POR PRODUTO": "NOVO_PRECO",
            "LEVE X PAGUE Y": "LEVE_X_PAGUE_Y",
            "DESCONTO PROGRESSIVO": "DESCONTO_PROGRESSIVO",
            "COMBO": "COMBO",
            "REGRA POR PRODUTO": "POR_PRODUTO",
        }
        return mapa.get(texto.strip().upper(), "")

    @staticmethod
    def _label_tipo(tipo: str) -> str:
        mapa = {
            "PERCENTUAL": "Desconto por percentual",
            "VALOR": "Desconto por valor",
            "PRECO_FIXO": "Preço promocional",
            "NOVO_PRECO": "Novo preço por produto",
            "LEVE_X_PAGUE_Y": "Leve X Pague Y",
            "DESCONTO_PROGRESSIVO": "Desconto progressivo",
            "COMBO": "Combo",
            "POR_PRODUTO": "Regra por produto",
        }
        return mapa.get(tipo.strip().upper(), tipo)

    @staticmethod
    def _label_status(status: str) -> str:
        mapa = {
            STATUS_PROMOCAO_RASCUNHO: "Rascunho",
            STATUS_PROMOCAO_AGENDADA: "Agendada",
            STATUS_PROMOCAO_ATIVA: "Ativa",
            STATUS_PROMOCAO_ENCERRADA: "Encerrada",
            STATUS_PROMOCAO_CANCELADA: "Cancelada",
        }
        return mapa.get(status.strip().upper(), status)

    @staticmethod
    def _status_normalizado(promocao: dict[str, Any] | None) -> str:
        if not promocao:
            return ""
        return str(promocao.get("status") or "").strip().upper()

    @staticmethod
    def _aplicar_estilo_status(item: QTableWidgetItem, status: str) -> None:
        status_normalizado = status.strip().upper()
        cores = {
            STATUS_PROMOCAO_RASCUNHO: ("#7a5c00", "#fff3cd"),
            STATUS_PROMOCAO_AGENDADA: ("#0f5f8f", "#d9ecfb"),
            STATUS_PROMOCAO_ATIVA: ("#1d6a3a", "#dff7e6"),
            STATUS_PROMOCAO_ENCERRADA: ("#546275", "#e6ebf2"),
            STATUS_PROMOCAO_CANCELADA: ("#8a1f1f", "#f8d7da"),
        }
        cor_texto, cor_fundo = cores.get(status_normalizado, ("#315676", "#f2f7fb"))
        fonte = QFont(item.font())
        fonte.setBold(True)
        item.setFont(fonte)
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(QBrush(QColor(cor_texto)))
        item.setBackground(QBrush(QColor(cor_fundo)))

    @staticmethod
    def _aplicar_estilo_tipo(item: QTableWidgetItem, tipo: str) -> None:
        tipo_normalizado = tipo.strip().upper()
        cores = {
            "PERCENTUAL": "#7c3aed",
            "VALOR": "#0f766e",
            "PRECO_FIXO": "#b45309",
            "NOVO_PRECO": "#c2410c",
            "LEVE_X_PAGUE_Y": "#0369a1",
            "DESCONTO_PROGRESSIVO": "#be185d",
            "COMBO": "#4338ca",
        }
        fonte = QFont(item.font())
        fonte.setBold(True)
        item.setFont(fonte)
        item.setForeground(QBrush(QColor(cores.get(tipo_normalizado, "#315676"))))

    @staticmethod
    def _aplicar_estilo_vigencia(item: QTableWidgetItem, status: str) -> None:
        status_normalizado = status.strip().upper()
        cores = {
            STATUS_PROMOCAO_RASCUNHO: "#667085",
            STATUS_PROMOCAO_AGENDADA: "#175cd3",
            STATUS_PROMOCAO_ATIVA: "#027a48",
            STATUS_PROMOCAO_ENCERRADA: "#475467",
            STATUS_PROMOCAO_CANCELADA: "#b42318",
        }
        fonte = QFont(item.font())
        fonte.setBold(status_normalizado in {STATUS_PROMOCAO_AGENDADA, STATUS_PROMOCAO_ATIVA})
        item.setFont(fonte)
        item.setForeground(QBrush(QColor(cores.get(status_normalizado, "#315676"))))

    def _restaurar_status_padrao(self) -> None:
        self.lblStatusBar.setText(
            "CSPdv - Módulo de Promoções | "
            f"{len(self._promocoes_filtradas)} promoção(ões) listada(s) com os filtros atuais"
        )

    def _atualizar_status_promocao_selecionada(self, promocao: dict[str, Any], quantidade_itens: int) -> None:
        self.lblStatusBar.setText(
            "CSPdv - Módulo de Promoções | "
            f"{promocao.get('codigo') or '-'} | "
            f"{promocao.get('nome') or '-'} | "
            f"{self._label_status(str(promocao.get('status') or '-'))} | "
            f"{quantidade_itens} item(ns) vinculado(s) | "
            f"{promocao.get('vigencia') or '-'}"
        )

    def _atualizar_tooltips_acoes(self, promocao: dict[str, Any] | None, status: str) -> None:
        if not promocao:
            self.btnAtualizar.setToolTip("Selecione uma promoção para editar.")
            self.btnDuplicarPromocao.setToolTip("Selecione uma promoção para duplicar.")
            self.btnVincularProdutos.setToolTip("Selecione uma promoção para vincular produtos.")
            self.btnEncerrarPromocao.setToolTip("Selecione uma promoção ativa ou agendada para encerrar.")
            self.btnCancelarPromocao.setToolTip("Selecione uma promoção para cancelar.")
            return

        nome = str(promocao.get("nome") or promocao.get("codigo") or "promoção").strip()
        status_label = self._label_status(status)
        self.btnAtualizar.setToolTip(f"Editar dados da promoção '{nome}'.")
        self.btnDuplicarPromocao.setToolTip(f"Criar uma cópia em Rascunho a partir de '{nome}'.")
        self.btnVincularProdutos.setToolTip(
            f"Vincular produtos a '{nome}' enquanto ela estiver em Rascunho, Agendada ou Ativa."
        )

        if status in {STATUS_PROMOCAO_AGENDADA, STATUS_PROMOCAO_ATIVA}:
            self.btnEncerrarPromocao.setToolTip(f"Encerrar agora a promoção '{nome}'.")
        else:
            self.btnEncerrarPromocao.setToolTip(
                f"A promoção '{nome}' está em status {status_label} e não pode ser encerrada."
            )

        if status in STATUS_PROMOCAO_EDITAVEL:
            self.btnCancelarPromocao.setToolTip(f"Cancelar a promoção '{nome}'.")
        else:
            self.btnCancelarPromocao.setToolTip(
                f"A promoção '{nome}' está em status {status_label} e não pode ser cancelada."
            )
