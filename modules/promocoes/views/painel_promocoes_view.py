from __future__ import annotations

from typing import Any, Callable

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QTableWidget,
)

from modules.promocoes.services.promocao_service import PromocaoService
from modules.promocoes.views.cadastro_promocao_view import CadastroPromocaoView
from modules.promocoes.views.vincular_produtos_promocao_dialog import VincularProdutosPromocaoDialog
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
        self._cadastro_promocao_dialog = None
        self._vincular_produtos_dialog = None

        self._configurar_tamanho_responsivo()
        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
        self._configurar_tabelas()
        self._conectar_eventos()
        self._carregar_dados()

    def _configurar_tabelas(self) -> None:
        header_promocoes = self.tablePromocoes.horizontalHeader()
        header_promocoes.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_promocoes.setSectionResizeMode(1, QHeaderView.Stretch)
        header_promocoes.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_promocoes.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_promocoes.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_promocoes.setSectionResizeMode(5, QHeaderView.Stretch)
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

    def _carregar_dados(self) -> None:
        self._promocoes_base = PromocaoService.listar_promocoes()
        self._aplicar_filtros()

    def _aplicar_filtros(self) -> None:
        busca = self.txtBuscaPromocao.text().strip().lower()
        status = self._mapear_status_filtro(self.cmbStatusFiltro.currentText())
        tipo = self._mapear_tipo_filtro(self.cmbTipoFiltro.currentText())

        self._promocoes_filtradas = []
        for promocao in self._promocoes_base:
            status_promocao = self._status_normalizado(promocao)
            tipo_promocao = str(promocao.get("tipo_desconto", "")).strip().upper()

            if status and status_promocao != status:
                continue
            if tipo and tipo_promocao != tipo:
                continue

            texto_base = " ".join(
                [
                    str(promocao.get("codigo", "")),
                    str(promocao.get("nome", "")),
                    str(promocao.get("tipo_desconto", "")),
                    str(promocao.get("status", "")),
                    str(promocao.get("alcance", "")),
                ]
            ).lower()
            if busca and busca not in texto_base:
                continue

            self._promocoes_filtradas.append(promocao)

        self._renderizar_promocoes()
        self._atualizar_metricas()

    def _renderizar_promocoes(self) -> None:
        self.tablePromocoes.setRowCount(len(self._promocoes_filtradas))
        for row, promocao in enumerate(self._promocoes_filtradas):
            valores = [
                str(promocao.get("codigo") or "-"),
                str(promocao.get("nome") or "-"),
                self._label_tipo(str(promocao.get("tipo_desconto") or "-")),
                str(promocao.get("vigencia") or "-"),
                self._label_status(str(promocao.get("status") or "-")),
                str(promocao.get("alcance") or "-"),
            ]
            tooltip = (
                f"Código: {promocao.get('codigo') or '-'}\n"
                f"Promoção: {promocao.get('nome') or '-'}\n"
                f"Tipo: {self._label_tipo(str(promocao.get('tipo_desconto') or '-'))}\n"
                f"Status: {self._label_status(str(promocao.get('status') or '-'))}\n"
                f"Vigência: {promocao.get('vigencia') or '-'}\n"
                f"Alcance: {promocao.get('alcance') or '-'}"
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
            self.tableItensPromocao.setRowCount(0)
            self.lblStatusBar.setText("CSPdv - Módulo de Promoções | Nenhuma promoção encontrada para os filtros atuais")
        self._atualizar_estado_acoes()

    def _atualizar_metricas(self) -> None:
        total_ativas = sum(1 for promocao in self._promocoes_base if self._status_normalizado(promocao) == "ATIVA")
        total_agendadas = sum(1 for promocao in self._promocoes_base if self._status_normalizado(promocao) == "AGENDADA")
        total_encerradas = sum(1 for promocao in self._promocoes_base if self._status_normalizado(promocao) == "ENCERRADA")
        total_itens = sum(int(promocao.get("qtd_produtos") or 0) for promocao in self._promocoes_base)

        self.lblPromocoesAtivasValor.setText(str(total_ativas))
        self.lblAgendadasValor.setText(str(total_agendadas))
        self.lblProdutosPromocaoValor.setText(str(total_itens))
        self.lblEncerradasValor.setText(str(total_encerradas))
        self._restaurar_status_padrao()

    def _popular_itens_da_promocao(self) -> None:
        promocao = self._obter_promocao_selecionada()
        if not promocao:
            self.tableItensPromocao.setRowCount(0)
            self._restaurar_status_padrao()
            return

        itens_db = PromocaoService.listar_itens_promocao(int(promocao.get("id") or 0))
        self.tableItensPromocao.setRowCount(len(itens_db))
        for row, item in enumerate(itens_db):
            valores = [
                str(item.get("produto") or "-"),
                formatar_moeda(item.get("preco_original")),
                formatar_moeda(item.get("preco_promocional")),
                self._formatar_desconto(item),
                str(item.get("observacao") or "-"),
            ]
            for column, valor in enumerate(valores):
                set_table_item(self.tableItensPromocao, row, column, valor)
        self._atualizar_status_promocao_selecionada(promocao, len(itens_db))

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

        self.btnAtualizar.setEnabled(selecionada)
        self.btnDuplicarPromocao.setEnabled(selecionada)
        self.btnVincularProdutos.setEnabled(selecionada and status in {"RASCUNHO", "AGENDADA", "ATIVA"})
        self.btnEncerrarPromocao.setEnabled(selecionada and status in {"AGENDADA", "ATIVA"})
        self.btnCancelarPromocao.setEnabled(selecionada and status in {"RASCUNHO", "AGENDADA", "ATIVA"})
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
    def _mapear_status_filtro(texto: str) -> str:
        mapa = {
            "ATIVAS": "ATIVA",
            "AGENDADAS": "AGENDADA",
            "ENCERRADAS": "ENCERRADA",
        }
        return mapa.get(texto.strip().upper(), "")

    @staticmethod
    def _mapear_tipo_filtro(texto: str) -> str:
        mapa = {
            "DESCONTO POR PERCENTUAL": "PERCENTUAL",
            "DESCONTO POR VALOR": "VALOR",
            "PREÇO PROMOCIONAL": "PRECO_FIXO",
            "PRECO PROMOCIONAL": "PRECO_FIXO",
        }
        return mapa.get(texto.strip().upper(), "")

    @staticmethod
    def _label_tipo(tipo: str) -> str:
        mapa = {
            "PERCENTUAL": "Desconto por percentual",
            "VALOR": "Desconto por valor",
            "PRECO_FIXO": "Preço promocional",
        }
        return mapa.get(tipo.strip().upper(), tipo)

    @staticmethod
    def _label_status(status: str) -> str:
        mapa = {
            "RASCUNHO": "Rascunho",
            "AGENDADA": "Agendada",
            "ATIVA": "Ativa",
            "ENCERRADA": "Encerrada",
            "CANCELADA": "Cancelada",
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
            "RASCUNHO": ("#7a5c00", "#fff3cd"),
            "AGENDADA": ("#0f5f8f", "#d9ecfb"),
            "ATIVA": ("#1d6a3a", "#dff7e6"),
            "ENCERRADA": ("#546275", "#e6ebf2"),
            "CANCELADA": ("#8a1f1f", "#f8d7da"),
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
        }
        fonte = QFont(item.font())
        fonte.setBold(True)
        item.setFont(fonte)
        item.setForeground(QBrush(QColor(cores.get(tipo_normalizado, "#315676"))))

    @staticmethod
    def _aplicar_estilo_vigencia(item: QTableWidgetItem, status: str) -> None:
        status_normalizado = status.strip().upper()
        cores = {
            "RASCUNHO": "#667085",
            "AGENDADA": "#175cd3",
            "ATIVA": "#027a48",
            "ENCERRADA": "#475467",
            "CANCELADA": "#b42318",
        }
        fonte = QFont(item.font())
        fonte.setBold(status_normalizado in {"AGENDADA", "ATIVA"})
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

        if status in {"AGENDADA", "ATIVA"}:
            self.btnEncerrarPromocao.setToolTip(f"Encerrar agora a promoção '{nome}'.")
        else:
            self.btnEncerrarPromocao.setToolTip(
                f"A promoção '{nome}' está em status {status_label} e não pode ser encerrada."
            )

        if status in {"RASCUNHO", "AGENDADA", "ATIVA"}:
            self.btnCancelarPromocao.setToolTip(f"Cancelar a promoção '{nome}'.")
        else:
            self.btnCancelarPromocao.setToolTip(
                f"A promoção '{nome}' está em status {status_label} e não pode ser cancelada."
            )
