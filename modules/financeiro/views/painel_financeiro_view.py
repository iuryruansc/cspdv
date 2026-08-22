from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate, QObject, QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QBrush, QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.admin.services.configuracoes_service import ConfiguracoesService
from modules.financeiro.services.financeiro_service import FinanceiroService
from modules.financeiro.services.reembolso_service import ReembolsoService
from modules.financeiro.views.novo_reembolso_dialog import NovoReembolsoDialog
from modules.shared.constants import (
    STATUS_CONTA_PARCIALMENTE_RECEBIDA,
    STATUS_CONTA_PENDENTE,
    STATUS_CONTA_QUITADA,
    STATUS_CONTA_VENCIDA,
    STATUS_REEMBOLSO_CANCELADO,
    STATUS_REEMBOLSO_CONCLUIDO,
    STATUS_VENDA_CONCLUIDA,
    STATUS_VENDA_CONCLUIDA_COM_PENDENCIA,
    STATUS_VENDA_PARCIALMENTE_REEMBOLSADA,
    STATUS_VENDA_REEMBOLSADA,
)
from modules.venda.services.caixa_service import CaixaService
from ui.financeiro.painel_financeiro import Ui_PainelFinanceiro
from utils.combo_loader import combo_int
from utils.format_utils import formatar_data, formatar_data_hora, formatar_inteiro, formatar_moeda
from utils.operational_panel_mixin import PainelOperacionalMixin
from utils.table_widget_utils import set_table_item
from utils.ui_messages import confirmar_acao, mostrar_aviso, mostrar_info


class _PainelFinanceiroWorker(QObject):
    concluido = pyqtSignal(object, int)
    falhou = pyqtSignal(str, int)

    def __init__(self, parametros: dict[str, Any], geracao: int):
        super().__init__()
        self._parametros = parametros
        self._geracao = geracao

    def executar(self) -> None:
        try:
            data_inicial = self._parametros["data_inicial"]
            data_final = self._parametros["data_final"]
            pdv_id = self._parametros["pdv_id"]
            forma_pagamento = self._parametros["forma_pagamento"]
            busca = self._parametros["busca"]
            status_filtro = self._parametros["status_filtro"]
            dados = {
                "resumo": FinanceiroService.obter_resumo_financeiro(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    pdv_id=pdv_id,
                    forma_pagamento=forma_pagamento,
                ),
                "movimentacoes": FinanceiroService.listar_movimentacoes_caixa(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    pdv_id=pdv_id,
                ),
                "vendas": FinanceiroService.listar_vendas_registradas(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    pdv_id=pdv_id,
                    forma_pagamento=forma_pagamento,
                    busca=busca,
                ),
                "contas": FinanceiroService.listar_contas_receber(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    pdv_id=pdv_id,
                    busca=busca,
                    status_filtro=status_filtro,
                ),
                "reembolsos": FinanceiroService.listar_reembolsos(
                    data_inicial=data_inicial,
                    data_final=data_final,
                    pdv_id=pdv_id,
                    forma_pagamento=forma_pagamento,
                ),
            }
            self.concluido.emit(dados, self._geracao)
        except Exception as exc:
            self.falhou.emit(str(exc), self._geracao)

class PainelFinanceiroView(QMainWindow, Ui_PainelFinanceiro, PainelOperacionalMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.cmbPdvFiltro: QComboBox
        self.cmbFormaPagamentoFiltro: QComboBox
        self.cmbStatusContaFiltro: QComboBox
        self.lineEditBuscaConta: QLineEdit
        self.tableCaixaMovimentacoes: QTableWidget
        self.tablePagamentos: QTableWidget
        self.tableContasReceber: QTableWidget
        self.tableReembolsos: QTableWidget
        self.tabWidgetRight: QtWidgets.QTabWidget
        self._painel_load_generation = 0
        self._painel_thread: QThread | None = None
        self._painel_worker: _PainelFinanceiroWorker | None = None

        self._configurar_resumos_abas()
        self._configurar_tamanho_responsivo()
        self._configurar_operador()
        self._configurar_relogio()
        self._conectar_retorno_selecao()
        self._configurar_tabelas()
        self._configurar_filtros_iniciais()
        self._conectar_eventos()
        self._carregar_painel()

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self._carregar_painel()

    def _configurar_tabelas(self) -> None:
        for table in (self.tableCaixaMovimentacoes, self.tablePagamentos, self.tableContasReceber, self.tableReembolsos):
            table.setAlternatingRowColors(True)
            table.setShowGrid(True)
            table.verticalHeader().setDefaultSectionSize(30)
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.tablePagamentos.setToolTip("Clique em uma venda para consultar seus detalhes.")
        self.tableContasReceber.setToolTip("Clique em uma conta para consultar, receber ou acompanhar o saldo.")
        self.tableReembolsos.setToolTip("Clique em um reembolso para consultar seus detalhes.")
        self.tablePagamentos.cellDoubleClicked.connect(self._consultar_venda)
        self.tableContasReceber.cellDoubleClicked.connect(self._abrir_detalhe_conta)
        self.tablePagamentos.itemSelectionChanged.connect(self._atualizar_contexto_selecao)
        self.tableContasReceber.itemSelectionChanged.connect(self._atualizar_contexto_selecao)
        self.tableReembolsos.cellDoubleClicked.connect(self._abrir_detalhe_reembolso)
        self.tableReembolsos.itemSelectionChanged.connect(self._atualizar_contexto_selecao)
        return None

    def _configurar_filtros_iniciais(self) -> None:
        self.frameToolbarFilters.setStyleSheet(
            "QFrame#frameToolbarFilters { background:#f8fbff; border:1px solid #b8cde0; border-radius:6px; }"
        )
        self.framePeriodoFiltro.setStyleSheet(
            "QFrame#framePeriodoFiltro { background:#eef6ff; border:1px solid #8db8df; border-radius:5px; } "
            "QLabel { color:#1a5fa0; font-weight:bold; }"
        )
        self.cmbPdvFiltro.setToolTip("Filtra os dados pelo ponto de venda.")
        self.cmbFormaPagamentoFiltro.setToolTip("Filtra os dados pela forma de pagamento.")
        self.cmbStatusContaFiltro.setToolTip("Define quais contas a receber serão exibidas.")
        self.lineEditBuscaConta.setToolTip("Pesquise por cliente, conta ou venda e pressione Enter.")
        self.dateInicial.setToolTip("Data inicial do período analisado.")
        self.dateFinal.setToolTip("Data final do período analisado.")
        self.btnOperacoes.setText("Ações")
        self.btnCaixa.setToolTip("Ações de abertura e fechamento de caixa.")
        self.btnFinanceiro.setToolTip("Recebimentos, reembolsos e movimentações financeiras.")
        self.btnOperacoes.setToolTip("Atualização e consulta de vendas.")
        self.lblSaldoCaixaTitulo.setText("Saldo em Caixa")
        self._configurar_periodo_padrao()
        self._carregar_pdvs()
        self._carregar_formas_pagamento()
        self._carregar_status_conta()

    def _conectar_eventos(self) -> None:
        self.actionAtualizar.triggered.connect(self._carregar_painel)
        self.actionConsultarVenda.triggered.connect(self._consultar_venda)
        self.actionAbrirCaixa.triggered.connect(self._abrir_caixa_financeiro)
        self.actionFecharCaixa.triggered.connect(self._fechar_caixa_financeiro)
        self.actionReceberPendencia.triggered.connect(self._receber_pendencia)
        self.actionNovoReembolso.triggered.connect(self._novo_reembolso)
        self.actionRegistrarMovimento.triggered.connect(self._registrar_movimentacao_financeiro)
        self.lineEditBuscaConta.returnPressed.connect(self._carregar_painel)
        self.cmbStatusContaFiltro.currentIndexChanged.connect(lambda _=0: self._carregar_painel())

    def _configurar_periodo_padrao(self) -> None:
        hoje = QDate.currentDate()
        inicio_mes = hoje.addDays(1 - hoje.day())
        fim_mes = QDate(hoje.year(), hoje.month(), hoje.daysInMonth())
        self.dateInicial.setDisplayFormat("dd/MM/yyyy")
        self.dateFinal.setDisplayFormat("dd/MM/yyyy")
        self.dateInicial.setDate(inicio_mes)
        self.dateFinal.setDate(fim_mes)

    def _carregar_pdvs(self) -> None:
        self.cmbPdvFiltro.clear()
        self.cmbPdvFiltro.addItem("Todos os PDVs", None)
        for pdv in FinanceiroService.listar_pdvs():
            descricao = str(pdv.get("descricao") or "").strip()
            identificacao = str(pdv.get("identificacao") or "").strip()
            rotulo = identificacao if not descricao else f"{identificacao} - {descricao}"
            self.cmbPdvFiltro.addItem(rotulo, int(pdv["id"]))

    def _carregar_formas_pagamento(self) -> None:
        self.cmbFormaPagamentoFiltro.clear()
        self.cmbFormaPagamentoFiltro.addItem("Todas as formas de pagamento", None)
        for forma in FinanceiroService.listar_formas_pagamento():
            self.cmbFormaPagamentoFiltro.addItem(str(forma.get("nome") or "Forma"), int(forma["id"]))

    def _carregar_status_conta(self) -> None:
        self.cmbStatusContaFiltro.clear()
        self.cmbStatusContaFiltro.addItem("Contas a receber em aberto", "ABERTAS")
        self.cmbStatusContaFiltro.addItem("Todas as contas", "TODAS")
        self.cmbStatusContaFiltro.addItem("Pendentes", "PENDENTE")
        self.cmbStatusContaFiltro.addItem("Parcialmente recebidas", "PARCIALMENTE_RECEBIDA")
        self.cmbStatusContaFiltro.addItem("Vencidas", "VENCIDA")
        self.cmbStatusContaFiltro.addItem("Quitadas", "QUITADA")
        self.cmbStatusContaFiltro.addItem("Vence hoje", "VENCE_HOJE")
        self.cmbStatusContaFiltro.addItem("Próximos 7 dias", "PROXIMOS_7_DIAS")

    def _carregar_painel(self) -> None:
        if self._painel_thread is not None and self._painel_thread.isRunning():
            self.lblStatusBar.setText("Atualização financeira já está em andamento...")
            return

        self._painel_load_generation += 1
        geracao = self._painel_load_generation
        parametros = {
            "data_inicial": self.dateInicial.date().toPyDate(),
            "data_final": self.dateFinal.date().toPyDate(),
            "pdv_id": combo_int(self.cmbPdvFiltro),
            "forma_pagamento": self._forma_pagamento_filtro(),
            "busca": self.lineEditBuscaConta.text().strip() or None,
            "status_filtro": self.cmbStatusContaFiltro.currentData(),
        }
        self.lblResumoVendas.setText("Carregando vendas...")
        self.lblResumoContas.setText("Carregando contas a receber...")
        self.lblResumoReembolsos.setText("Carregando reembolsos...")
        self.lblStatusBar.setText("Atualizando dados financeiros...")

        thread = QThread(self)
        worker = _PainelFinanceiroWorker(parametros, geracao)
        worker.moveToThread(thread)
        thread.started.connect(worker.executar)
        worker.concluido.connect(self._painel_carregado)
        worker.falhou.connect(self._painel_falhou)
        worker.concluido.connect(thread.quit)
        worker.falhou.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._finalizar_carregamento_painel)
        self._painel_thread = thread
        self._painel_worker = worker
        thread.start()

    @pyqtSlot(object, int)
    def _painel_carregado(self, dados: dict[str, Any], geracao: int) -> None:
        if geracao != self._painel_load_generation:
            return
        self._carregar_cards(dados.get("resumo") or {})
        self._carregar_movimentacoes_caixa(dados.get("movimentacoes") or [])
        self._carregar_vendas_registradas(dados.get("vendas") or [])
        self._carregar_contas_receber(dados.get("contas") or [])
        self._carregar_reembolsos(dados.get("reembolsos") or [])
        self._atualizar_resumo_secoes_direita()
        self._ajustar_alturas_secao_direita()
        self._atualizar_contexto_selecao()
        self.lblStatusBar.setText("Dados financeiros atualizados.")

    @pyqtSlot(str, int)
    def _painel_falhou(self, mensagem: str, geracao: int) -> None:
        if geracao != self._painel_load_generation:
            return
        self.lblResumoVendas.setText("Não foi possível carregar as vendas.")
        self.lblResumoContas.setText("Não foi possível carregar as contas.")
        self.lblResumoReembolsos.setText("Não foi possível carregar os reembolsos.")
        self.lblStatusBar.setText("Falha ao atualizar os dados financeiros.")
        mostrar_aviso(
            self,
            "Falha ao carregar dados",
            f"Não foi possível atualizar o painel financeiro agora.\n\nDetalhes: {mensagem}",
        )

    def _finalizar_carregamento_painel(self) -> None:
        self._painel_thread = None
        self._painel_worker = None

    def _abrir_caixa_financeiro(self) -> None:
        if not SessionManager.has_permission("vendas.pdv"):
            mostrar_aviso(
                self,
                "Acesso negado",
                "O usuário atual não possui permissão para abrir caixa por este módulo.",
            )
            return

        usuario = SessionManager.current_user() or {}
        from modules.venda.services.caixa_service import CaixaService

        if not CaixaSession.has_open_caixa():
            CaixaService.restaurar_caixa_aberto(usuario.get("id"))

        if CaixaSession.has_open_caixa():
            mostrar_info(
                self,
                "Caixa ja aberto",
                "Ja existe um caixa aberto nesta sessao. Voce pode acompanhar os dados e fechar o caixa por aqui quando necessario.",
            )
            self._carregar_painel()
            return

        confirmar = confirmar_acao(
            self,
            "Abrir caixa",
            "Deseja abrir o caixa agora sem sair do módulo financeiro?",
        )
        if not confirmar:
            return

        from modules.venda.views.abrir_frente_caixa_dialog import AbrirFrenteCaixaDialog

        dialog = AbrirFrenteCaixaDialog(self)
        if dialog.exec_() != dialog.Accepted:
            return

        self._carregar_painel()
        mostrar_info(
            self,
            "Caixa aberto",
            "Caixa aberto com sucesso. O modulo financeiro foi atualizado com a sessao atual.",
        )

    def _fechar_caixa_financeiro(self) -> None:
        if not CaixaSession.has_open_caixa():
            mostrar_aviso(
                self,
                "Caixa não encontrado",
                "Não há um caixa aberto no momento para encerrar por este módulo.",
            )
            self._carregar_painel()
            return

        from modules.venda.views.fechar_caixa_dialog import FecharCaixaDialog

        dialog = FecharCaixaDialog(self)
        if dialog.exec_() != dialog.Accepted:
            return

        self._carregar_painel()
        mostrar_info(
            self,
            "Caixa fechado",
            "Caixa encerrado com sucesso. O modulo financeiro foi recarregado.",
        )

    def _registrar_movimentacao_financeiro(self) -> None:
        if not CaixaSession.has_open_caixa():
            mostrar_aviso(
                self,
                "Caixa não encontrado",
                "Abra um caixa antes de registrar sangria, suprimento ou reforco de troco.",
            )
            return

        from modules.venda.views.movimentacao_caixa_dialog import MovimentacaoCaixaDialog

        dialog = MovimentacaoCaixaDialog(self)
        if dialog.exec_() == dialog.Accepted:
            self._carregar_painel()

    def _consultar_venda(self) -> None:
        venda_id = self._obter_venda_id_selecionada()
        if not venda_id:
            mostrar_aviso(
                self,
                "Selecione uma venda",
                "Escolha uma linha em Vendas Registradas, Contas a Receber ou Reembolsos Registrados para consultar os detalhes da venda.",
            )
            return

        detalhes = FinanceiroService.obter_venda_detalhada(venda_id)
        if not detalhes:
            mostrar_aviso(
                self,
                "Venda não encontrada",
                "Não foi possível localizar os detalhes da venda selecionada.",
            )
            return

        from modules.financeiro.views.consulta_venda_dialog import ConsultaVendaDialog

        dialog = ConsultaVendaDialog(detalhes, self)
        dialog.exec_()
        if dialog.payment_registered:
            self._carregar_painel()

    def _receber_pendencia(self) -> None:
        if not CaixaSession.has_open_caixa():
            mostrar_aviso(
                self,
                "Caixa não encontrado",
                "Abra um caixa antes de registrar recebimentos de pendências.",
            )
            return

        conta_id = self._obter_conta_id_selecionada()
        self._executar_recebimento_conta(conta_id)
        return

    def _executar_recebimento_conta(self, conta_id: int | None) -> None:
        if not CaixaSession.has_open_caixa():
            mostrar_aviso(
                self,
                "Caixa não encontrado",
                "Abra um caixa antes de registrar recebimentos de pendências.",
            )
            return
        if not conta_id:
            mostrar_aviso(
                self,
                "Selecione uma conta",
                "Escolha uma linha em Contas a Receber para registrar o recebimento.",
            )
            return

        conta_detalhada = FinanceiroService.obter_conta_receber_detalhada(conta_id)
        if not conta_detalhada:
            mostrar_aviso(
                self,
                "Conta não encontrada",
                "Não foi possível localizar os dados da conta selecionada.",
            )
            return

        from modules.financeiro.views.receber_pendencia_dialog import ReceberPendenciaDialog

        dialog = ReceberPendenciaDialog(conta_detalhada, self)
        if dialog.exec_() != dialog.Accepted or not dialog.resultado:
            return

        usuario = SessionManager.current_user() or {}
        caixa = CaixaSession.current() or {}
        try:
            resultado = FinanceiroService.registrar_recebimento_conta(
                conta_id=int(dialog.resultado["conta_id"]),
                usuario_id=int(usuario.get("id") or 0),
                caixa_id=int(caixa.get("id") or 0),
                forma_pagamento_id=int(dialog.resultado["forma_pagamento_id"]),
                valor_recebido=Decimal(str(dialog.resultado["valor_recebido"])).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                ),
                observacao=str(dialog.resultado.get("observacao") or "").strip(),
                data_recebimento=dialog.resultado.get("data_recebimento") or datetime.now(),
            )
        except Exception as exc:
            mostrar_aviso(self, "Recebimento não registrado", str(exc))
            return

        self._carregar_painel()

        from modules.financeiro.views.comprovante_recebimento_dialog import ComprovanteRecebimentoDialog

        operador_nome = str(usuario.get("nome") or "Operador")
        caixa_label = str(caixa.get("pdv_label") or "Caixa")
        recebimento_dialog = ComprovanteRecebimentoDialog(
            conta=dict(conta_detalhada.get("conta") or {}),
            recebimento={
                **resultado,
                "observacao": str(dialog.resultado.get("observacao") or "").strip(),
                "data_recebimento": dialog.resultado.get("data_recebimento") or datetime.now(),
            },
            operador_nome=operador_nome,
            caixa_label=caixa_label,
            parent=self,
        )
        recebimento_dialog.exec_()

    def _abrir_detalhe_conta(self, row: int, _column: int) -> None:
        if row < 0:
            return
        conta_id = self._obter_conta_id_selecionada()
        if not conta_id:
            return
        conta_detalhada = FinanceiroService.obter_conta_receber_detalhada(conta_id)
        if not conta_detalhada:
            mostrar_aviso(self, "Conta não encontrada", "Não foi possível localizar os detalhes da conta selecionada.")
            return
        from modules.financeiro.views.consulta_conta_receber_dialog import ConsultaContaReceberDialog

        dialog = ConsultaContaReceberDialog(conta_detalhada, self)
        if dialog.exec_() == dialog.Accepted and dialog.solicitar_recebimento:
            self._executar_recebimento_conta(conta_id)

    def _abrir_detalhe_reembolso(self, row: int, _column: int) -> None:
        if row < 0:
            return
        reembolso_id = self._obter_reembolso_id_selecionado()
        if not reembolso_id:
            return
        detalhes = FinanceiroService.obter_reembolso_detalhado(reembolso_id)
        if not detalhes:
            mostrar_aviso(self, "Reembolso não encontrado", "Não foi possível localizar os detalhes do reembolso selecionado.")
            return
        from modules.financeiro.views.consulta_reembolso_dialog import ConsultaReembolsoDialog

        dialog = ConsultaReembolsoDialog(detalhes, self)
        if dialog.exec_() == dialog.Accepted and dialog.venda_id > 0:
            detalhes_venda = FinanceiroService.obter_venda_detalhada(dialog.venda_id)
            if detalhes_venda:
                from modules.financeiro.views.consulta_venda_dialog import ConsultaVendaDialog
                venda_dialog = ConsultaVendaDialog(detalhes_venda, self)
                venda_dialog.exec_()
                if venda_dialog.payment_registered:
                    self._carregar_painel()

    def _novo_reembolso(self) -> None:
        venda_id = self._obter_venda_id_selecionada()
        if not venda_id:
            mostrar_aviso(
                self,
                "Selecione uma venda",
                "Escolha uma linha em Vendas Registradas, Contas a Receber ou Reembolsos Registrados para iniciar um novo reembolso.",
            )
            return

        detalhes = FinanceiroService.obter_venda_detalhada(venda_id)
        if not detalhes:
            mostrar_aviso(
                self,
                "Venda não encontrada",
                "Não foi possível localizar os detalhes da venda selecionada.",
            )
            return

        dialog = NovoReembolsoDialog(detalhes, self)
        if dialog.exec_() != dialog.Accepted or not dialog.resultado:
            return

        parametros_caixa = ConfiguracoesService.carregar_parametros_caixa()
        if bool(parametros_caixa.get("exigir_admin_reembolso", True)):
            senha_admin, confirmou = QInputDialog.getText(
                self,
                "Autorização de reembolso",
                "Informe a senha de um administrador para concluir o reembolso.",
                QLineEdit.Password,
            )
            if not confirmou:
                return
            if not CaixaService.validar_admin_para_diferenca(str(senha_admin or "").strip()):
                mostrar_aviso(
                    self,
                    "Autorização inválida",
                    "Informe uma senha de administrador válida para registrar o reembolso.",
                )
                return

        sucesso, mensagem, resultado = ReembolsoService.registrar_reembolso(dialog.resultado)
        if not sucesso or resultado is None:
            mostrar_aviso(self, "Reembolso não registrado", mensagem)
            return

        self._carregar_painel()
        mostrar_info(
            self,
            "Reembolso registrado",
            f"{mensagem}\n\nReembolso #{resultado['reembolso_id']} | Venda #{resultado['venda_id']} | Valor {formatar_moeda(resultado['valor_total'])}",
        )

    def _obter_venda_id_selecionada(self) -> int | None:
        for table in (self.tablePagamentos, self.tableContasReceber, self.tableReembolsos):
            row = table.currentRow()
            if row < 0:
                continue
            item = table.item(row, 0)
            if not item:
                continue
            value = item.data(Qt.UserRole)
            try:
                venda_id = int(value)
            except (TypeError, ValueError):
                continue
            if venda_id > 0:
                return venda_id
        return None

    def _obter_conta_id_selecionada(self) -> int | None:
        row = self.tableContasReceber.currentRow()
        if row < 0:
            return None
        item = self.tableContasReceber.item(row, 0)
        if not item:
            return None
        value = item.data(Qt.UserRole + 1)
        try:
            conta_id = int(value)
        except (TypeError, ValueError):
            return None
        return conta_id if conta_id > 0 else None

    def _obter_reembolso_id_selecionado(self) -> int | None:
        row = self.tableReembolsos.currentRow()
        if row < 0:
            return None
        item = self.tableReembolsos.item(row, 0)
        if not item:
            return None
        value = item.data(Qt.UserRole + 1)
        try:
            reembolso_id = int(value)
        except (TypeError, ValueError):
            return None
        return reembolso_id if reembolso_id > 0 else None

    def _carregar_cards(self, resumo: dict[str, Any] | None = None) -> None:
        if resumo is None:
            resumo = FinanceiroService.obter_resumo_financeiro(
                data_inicial=self.dateInicial.date().toPyDate(),
                data_final=self.dateFinal.date().toPyDate(),
                pdv_id=combo_int(self.cmbPdvFiltro),
                forma_pagamento=self._forma_pagamento_filtro(),
            )
        self.lblSaldoCaixaValor.setText(formatar_moeda(resumo.get("saldo_atual_caixa")))
        self.lblEntradasDiaValor.setText(formatar_moeda(resumo.get("entradas_periodo")))
        self.lblSaidasDiaValor.setText(formatar_moeda(resumo.get("saidas_periodo")))
        self.lblPagamentosPendentesValor.setText(formatar_inteiro(resumo.get("contas_abertas_periodo")))

    def _carregar_movimentacoes_caixa(self, registros: list[dict[str, Any]] | None = None) -> None:
        if registros is None:
            registros = FinanceiroService.listar_movimentacoes_caixa(
                data_inicial=self.dateInicial.date().toPyDate(),
                data_final=self.dateFinal.date().toPyDate(),
                pdv_id=combo_int(self.cmbPdvFiltro),
            )

        registros.sort(key=lambda r: r.get("data_hora") or 0, reverse=True)

        if not registros:
            self.tableCaixaMovimentacoes.setRowCount(1)
            self.tableCaixaMovimentacoes.setColumnCount(1)
            item = QTableWidgetItem("Nenhuma movimentacao no periodo")
            item.setTextAlignment(Qt.AlignCenter)
            fonte = QFont(item.font())
            fonte.setItalic(True)
            fonte.setPointSize(11)
            item.setFont(fonte)
            item.setForeground(QBrush(QColor("#98a8b8")))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.tableCaixaMovimentacoes.setItem(0, 0, item)
            self.tableCaixaMovimentacoes.horizontalHeader().setStretchLastSection(True)
            return

        self.tableCaixaMovimentacoes.setColumnCount(6)
        self.tableCaixaMovimentacoes.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            set_table_item(self.tableCaixaMovimentacoes, row, 0, formatar_data_hora(registro.get("data_hora")))
            set_table_item(self.tableCaixaMovimentacoes, row, 1, str(registro.get("pdv") or "-"))
            set_table_item(self.tableCaixaMovimentacoes, row, 2, str(registro.get("operador") or "-"))
            set_table_item(self.tableCaixaMovimentacoes, row, 3, str(registro.get("motivo") or "-"))
            set_table_item(self.tableCaixaMovimentacoes, row, 4, str(registro.get("forma_pagamento") or "-"))
            set_table_item(
                self.tableCaixaMovimentacoes,
                row,
                5,
                formatar_moeda(registro.get("valor")),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )

    def _carregar_vendas_registradas(self, registros: list[dict[str, Any]] | None = None) -> None:
        if registros is None:
            registros = FinanceiroService.listar_vendas_registradas(
                data_inicial=self.dateInicial.date().toPyDate(),
                data_final=self.dateFinal.date().toPyDate(),
                pdv_id=combo_int(self.cmbPdvFiltro),
                forma_pagamento=self._forma_pagamento_filtro(),
                busca=self.lineEditBuscaConta.text().strip() or None,
            )

        self.tablePagamentos.setRowCount(len(registros))
        total_vendas = sum((Decimal(str(registro.get("valor_total") or 0)) for registro in registros), Decimal("0.00"))
        self.lblResumoVendas.setText(
            f"{len(registros)} venda(s) no período • Total: {formatar_moeda(total_vendas)}"
        )
        for row, registro in enumerate(registros):
            item_venda = set_table_item(
                self.tablePagamentos,
                row,
                0,
                str(registro.get("venda_id") or "-"),
                alignment=Qt.AlignCenter,
            )
            item_venda.setData(Qt.UserRole, int(registro.get("venda_id") or 0))
            set_table_item(self.tablePagamentos, row, 1, str(registro.get("data_hora") or "-"))
            set_table_item(self.tablePagamentos, row, 2, str(registro.get("cliente") or "-"))
            set_table_item(self.tablePagamentos, row, 3, str(registro.get("forma_pagamento") or "-"))
            status_item = set_table_item(
                self.tablePagamentos,
                row,
                4,
                str(registro.get("status") or "-"),
                alignment=Qt.AlignCenter,
            )
            total_item = set_table_item(
                self.tablePagamentos,
                row,
                5,
                formatar_moeda(registro.get("valor_total")),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )
            self._aplicar_estilo_status_venda(status_item, str(registro.get("status") or ""))
            self._destacar_total(total_item)
            self._aplicar_tooltip_venda(row, registro)

    def _carregar_contas_receber(self, registros: list[dict[str, Any]] | None = None) -> None:
        if registros is None:
            registros = FinanceiroService.listar_contas_receber(
                data_inicial=self.dateInicial.date().toPyDate(),
                data_final=self.dateFinal.date().toPyDate(),
                pdv_id=combo_int(self.cmbPdvFiltro),
                busca=self.lineEditBuscaConta.text().strip() or None,
                status_filtro=self.cmbStatusContaFiltro.currentData(),
            )

        self.tableContasReceber.setRowCount(len(registros))
        total_aberto = sum((Decimal(str(registro.get("valor_aberto") or 0)) for registro in registros), Decimal("0.00"))
        self.lblResumoContas.setText(
            f"{len(registros)} conta(s) exibida(s) • Saldo em aberto: {formatar_moeda(total_aberto)}"
        )
        for row, registro in enumerate(registros):
            item_conta = set_table_item(
                self.tableContasReceber,
                row,
                0,
                str(registro.get("conta_id") or "-"),
                alignment=Qt.AlignCenter,
            )
            item_conta.setData(Qt.UserRole, int(registro.get("venda_id") or 0))
            item_conta.setData(Qt.UserRole + 1, int(registro.get("conta_id") or 0))
            item_conta.setData(Qt.UserRole + 2, registro.get("ultimo_recebimento"))
            item_conta.setData(Qt.UserRole + 3, int(registro.get("total_recebimentos") or 0))
            item_conta.setData(Qt.UserRole + 4, int(registro.get("dias_atraso") or 0))
            set_table_item(
                self.tableContasReceber,
                row,
                1,
                str(registro.get("venda_id") or "-"),
                alignment=Qt.AlignCenter,
            )
            set_table_item(self.tableContasReceber, row, 2, str(registro.get("cliente") or "-"))
            set_table_item(
                self.tableContasReceber,
                row,
                3,
                formatar_data(registro.get("data_vencimento")),
                alignment=Qt.AlignCenter,
            )
            status_item = set_table_item(
                self.tableContasReceber,
                row,
                4,
                str(registro.get("status") or "-"),
                alignment=Qt.AlignCenter,
            )
            saldo_item = set_table_item(
                self.tableContasReceber,
                row,
                5,
                formatar_moeda(registro.get("valor_aberto")),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )
            if bool(registro.get("vencida")):
                self._destacar_linha_vencida(self.tableContasReceber, row)
            self._aplicar_estilo_status_conta(status_item, str(registro.get("status") or ""), bool(registro.get("vencida")))
            self._destacar_saldo_conta(saldo_item, bool(registro.get("vencida")))
            self._aplicar_tooltip_conta(row, registro)

    def _carregar_reembolsos(self, registros: list[dict[str, Any]] | None = None) -> None:
        if registros is None:
            registros = FinanceiroService.listar_reembolsos(
                data_inicial=self.dateInicial.date().toPyDate(),
                data_final=self.dateFinal.date().toPyDate(),
                pdv_id=combo_int(self.cmbPdvFiltro),
                forma_pagamento=self._forma_pagamento_filtro(),
            )
        registros.sort(
            key=lambda r: (
                r.get("data_hora") or 0,
                int(r.get("reembolso_id") or 0),
            ),
            reverse=True,
        )
        self.tableReembolsos.setRowCount(len(registros))
        total_reembolsado = sum((Decimal(str(registro.get("valor_total") or 0)) for registro in registros), Decimal("0.00"))
        self.lblResumoReembolsos.setText(
            f"{len(registros)} reembolso(s) • Total devolvido: {formatar_moeda(total_reembolsado)}"
        )
        for row, registro in enumerate(registros):
            item_venda = set_table_item(
                self.tableReembolsos,
                row,
                0,
                str(registro.get("venda_id") or "-"),
                alignment=Qt.AlignCenter,
            )
            item_venda.setData(Qt.UserRole, int(registro.get("venda_id") or 0))
            item_venda.setData(Qt.UserRole + 1, int(registro.get("reembolso_id") or 0))
            set_table_item(self.tableReembolsos, row, 1, str(registro.get("tipo") or "-"), alignment=Qt.AlignCenter)
            set_table_item(self.tableReembolsos, row, 2, str(registro.get("motivo") or "-"))
            status_item = set_table_item(
                self.tableReembolsos,
                row,
                3,
                str(registro.get("status") or "-"),
                alignment=Qt.AlignCenter,
            )
            valor_item = set_table_item(
                self.tableReembolsos,
                row,
                4,
                formatar_moeda(registro.get("valor_total")),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )
            self._aplicar_estilo_status_reembolso(status_item, str(registro.get("status") or ""))
            self._destacar_total(valor_item)
            self._aplicar_tooltip_reembolso(row, registro)

    def _forma_pagamento_filtro(self) -> str | None:
        if self.cmbFormaPagamentoFiltro.currentData() is None:
            return None
        return self.cmbFormaPagamentoFiltro.currentText().strip() or None

    @staticmethod
    def _destacar_linha_vencida(table: QTableWidget, row: int) -> None:
        background = QColor("#fff1f0")
        foreground = QColor("#b42318")
        for column in range(table.columnCount()):
            item = table.item(row, column)
            if not item:
                continue
            item.setBackground(background)
            item.setForeground(foreground)

    @staticmethod
    def _aplicar_estilo_status_venda(item: QTableWidgetItem, status: str) -> None:
        status_normalizado = status.strip().upper()
        rotulo = PainelFinanceiroView._rotulo_status(status_normalizado)
        icones = {
            STATUS_VENDA_CONCLUIDA: "\u2713",
            STATUS_VENDA_CONCLUIDA_COM_PENDENCIA: "\u25CB",
            STATUS_VENDA_PARCIALMENTE_REEMBOLSADA: "\u25D1",
            STATUS_VENDA_REEMBOLSADA: "\u2717",
        }
        icone = icones.get(status_normalizado, "\u2022")
        texto = f" {icone}  {rotulo} "
        item.setText(texto)
        if status_normalizado == STATUS_VENDA_CONCLUIDA:
            PainelFinanceiroView._estilizar_item_status(item, "#ecfdf3", "#027a48")
            return
        if status_normalizado == STATUS_VENDA_CONCLUIDA_COM_PENDENCIA:
            PainelFinanceiroView._estilizar_item_status(item, "#fff7e6", "#b54708")
            return
        if status_normalizado == STATUS_VENDA_PARCIALMENTE_REEMBOLSADA:
            PainelFinanceiroView._estilizar_item_status(item, "#eff8ff", "#175cd3")
            return
        if status_normalizado == STATUS_VENDA_REEMBOLSADA:
            PainelFinanceiroView._estilizar_item_status(item, "#fef3f2", "#b42318")
            return
        PainelFinanceiroView._estilizar_item_status(item, "#f2f4f7", "#344054")

    @staticmethod
    def _aplicar_estilo_status_conta(item: QTableWidgetItem, status: str, vencida: bool) -> None:
        status_normalizado = status.strip().upper()
        item.setText("Vencida" if vencida else PainelFinanceiroView._rotulo_status(status_normalizado))
        if vencida or status_normalizado == STATUS_CONTA_VENCIDA:
            PainelFinanceiroView._estilizar_item_status(item, "#fef3f2", "#b42318")
            return
        if status_normalizado == STATUS_CONTA_PENDENTE:
            PainelFinanceiroView._estilizar_item_status(item, "#fff7e6", "#b54708")
            return
        if status_normalizado == STATUS_CONTA_PARCIALMENTE_RECEBIDA:
            PainelFinanceiroView._estilizar_item_status(item, "#eff8ff", "#175cd3")
            return
        if status_normalizado == STATUS_CONTA_QUITADA:
            PainelFinanceiroView._estilizar_item_status(item, "#ecfdf3", "#027a48")
            return
        PainelFinanceiroView._estilizar_item_status(item, "#f2f4f7", "#344054")

    @staticmethod
    def _aplicar_estilo_status_reembolso(item: QTableWidgetItem, status: str) -> None:
        status_normalizado = status.strip().upper()
        item.setText(PainelFinanceiroView._rotulo_status(status_normalizado))
        if status_normalizado == STATUS_REEMBOLSO_CONCLUIDO:
            PainelFinanceiroView._estilizar_item_status(item, "#ecfdf3", "#027a48")
            return
        if status_normalizado == STATUS_REEMBOLSO_CANCELADO:
            PainelFinanceiroView._estilizar_item_status(item, "#fef3f2", "#b42318")
            return
        PainelFinanceiroView._estilizar_item_status(item, "#f2f4f7", "#344054")

    @staticmethod
    def _estilizar_item_status(item: QTableWidgetItem, background_hex: str, foreground_hex: str) -> None:
        fonte = QFont(item.font())
        fonte.setBold(True)
        item.setFont(fonte)
        item.setBackground(QBrush(QColor(background_hex)))
        item.setForeground(QBrush(QColor(foreground_hex)))

    @staticmethod
    def _rotulo_status(status: str) -> str:
        rotulos = {
            STATUS_VENDA_CONCLUIDA: "Concluída",
            STATUS_VENDA_CONCLUIDA_COM_PENDENCIA: "Concluída com pendência",
            STATUS_VENDA_PARCIALMENTE_REEMBOLSADA: "Reembolso parcial",
            STATUS_VENDA_REEMBOLSADA: "Reembolsada",
            STATUS_CONTA_PENDENTE: "Pendente",
            STATUS_CONTA_PARCIALMENTE_RECEBIDA: "Parcialmente recebida",
            STATUS_CONTA_QUITADA: "Quitada",
            STATUS_CONTA_VENCIDA: "Vencida",
            STATUS_REEMBOLSO_CONCLUIDO: "Concluído",
            STATUS_REEMBOLSO_CANCELADO: "Cancelado",
        }
        return rotulos.get(status, status.replace("_", " ").capitalize() or "-")

    @staticmethod
    def _destacar_total(item: QTableWidgetItem) -> None:
        fonte = QFont(item.font())
        fonte.setBold(True)
        item.setFont(fonte)
        item.setForeground(QBrush(QColor("#1a3a5c")))

    @staticmethod
    def _destacar_saldo_conta(item: QTableWidgetItem, vencida: bool) -> None:
        fonte = QFont(item.font())
        fonte.setBold(True)
        item.setFont(fonte)
        cor = "#b42318" if vencida else "#1d4c74"
        item.setForeground(QBrush(QColor(cor)))

    def _atualizar_resumo_secoes_direita(self) -> None:
        qtd_vendas = self.tablePagamentos.rowCount()
        qtd_contas = self.tableContasReceber.rowCount()
        qtd_reembolsos = self.tableReembolsos.rowCount()

        self.tabWidgetRight.setTabText(0, f"Vendas ({qtd_vendas})")
        self.tabWidgetRight.setTabText(1, f"Contas a Receber ({qtd_contas})")
        self.tabWidgetRight.setTabText(2, f"Reembolsos ({qtd_reembolsos})")

    def _configurar_resumos_abas(self) -> None:
        estilo = (
            "QLabel { background:#f8fbff; color:#46627d; border-bottom:1px solid #d8e5f1; "
            "padding:7px 12px; font-size:11px; font-weight:600; }"
        )
        self.lblResumoVendas = QLabel(self.tabVendas)
        self.lblResumoVendas.setStyleSheet(estilo)
        self.tabVendasLayout.insertWidget(0, self.lblResumoVendas)
        self.lblResumoContas = QLabel(self.tabContas)
        self.lblResumoContas.setStyleSheet(estilo)
        self.tabContasLayout.insertWidget(0, self.lblResumoContas)
        self.lblResumoReembolsos = QLabel(self.tabReembolsos)
        self.lblResumoReembolsos.setStyleSheet(estilo)
        self.tabReembolsosLayout.insertWidget(0, self.lblResumoReembolsos)

    def _ajustar_alturas_secao_direita(self) -> None:
        pass

    def _atualizar_contexto_selecao(self) -> None:
        row_conta = self.tableContasReceber.currentRow()
        if row_conta >= 0:
            conta = self._texto_item(self.tableContasReceber, row_conta, 0)
            cliente = self._texto_item(self.tableContasReceber, row_conta, 1)
            vencimento = self._texto_item(self.tableContasReceber, row_conta, 2)
            status = self._texto_item(self.tableContasReceber, row_conta, 3)
            saldo = self._texto_item(self.tableContasReceber, row_conta, 4)
            item_conta = self.tableContasReceber.item(row_conta, 0)
            ultima_baixa = formatar_data_hora(item_conta.data(Qt.UserRole + 2) if item_conta else None)
            recebimentos = formatar_inteiro(item_conta.data(Qt.UserRole + 3) if item_conta else 0)
            self.lblStatusBar.setText(
                "CSPdv - Modulo Financeiro | "
                f"Conta #{conta} | {cliente} | {status} | Vencimento {vencimento} | "
                f"Saldo {saldo} | Recebimentos {recebimentos} | Última baixa {ultima_baixa}"
            )
            return

        row_venda = self.tablePagamentos.currentRow()
        if row_venda >= 0:
            venda = self._texto_item(self.tablePagamentos, row_venda, 0)
            data = self._texto_item(self.tablePagamentos, row_venda, 1)
            cliente = self._texto_item(self.tablePagamentos, row_venda, 2)
            forma = self._texto_item(self.tablePagamentos, row_venda, 3)
            status = self._texto_item(self.tablePagamentos, row_venda, 4)
            total = self._texto_item(self.tablePagamentos, row_venda, 5)
            self.lblStatusBar.setText(
                "CSPdv - Modulo Financeiro | "
                f"Venda #{venda} | {data} | {cliente} | {forma} | {status} | Total {total}"
            )
            return

        row_reembolso = self.tableReembolsos.currentRow()
        if row_reembolso >= 0:
            venda = self._texto_item(self.tableReembolsos, row_reembolso, 0)
            tipo = self._texto_item(self.tableReembolsos, row_reembolso, 1)
            motivo = self._texto_item(self.tableReembolsos, row_reembolso, 2)
            status = self._texto_item(self.tableReembolsos, row_reembolso, 3)
            valor = self._texto_item(self.tableReembolsos, row_reembolso, 4)
            self.lblStatusBar.setText(
                "CSPdv - Modulo Financeiro | "
                f"Reembolso da venda #{venda} | {tipo} | {status} | {valor} | Motivo: {motivo}"
            )
            return

        self.lblStatusBar.setText(
            "CSPdv - Modulo Financeiro | "
            f"{self.tableCaixaMovimentacoes.rowCount()} movimentação(ões), "
            f"{self.tablePagamentos.rowCount()} venda(s), "
            f"{self.tableContasReceber.rowCount()} conta(s), "
            f"{self.tableReembolsos.rowCount()} reembolso(s)"
        )

    def _aplicar_tooltip_venda(self, row: int, registro: dict[str, Any]) -> None:
        tooltip = (
            f"Venda #{registro.get('venda_id') or '-'}\n"
            f"Data: {registro.get('data_hora') or '-'}\n"
            f"Cliente: {registro.get('cliente') or '-'}\n"
            f"Forma: {registro.get('forma_pagamento') or '-'}\n"
            f"Status: {registro.get('status') or '-'}\n"
            f"Total: {formatar_moeda(registro.get('valor_total'))}"
        )
        self._aplicar_tooltip_linha(self.tablePagamentos, row, tooltip)

    def _aplicar_tooltip_conta(self, row: int, registro: dict[str, Any]) -> None:
        ultimo_recebimento = formatar_data_hora(registro.get("ultimo_recebimento"))
        dias_atraso = int(registro.get("dias_atraso") or 0)
        situacao_atraso = f"{dias_atraso} dia(s) em atraso" if dias_atraso > 0 else "Sem atraso"
        tooltip = (
            f"Conta #{registro.get('conta_id') or '-'}\n"
            f"Cliente: {registro.get('cliente') or '-'}\n"
            f"Vencimento: {formatar_data(registro.get('data_vencimento'))}\n"
            f"Status: {registro.get('status') or '-'}\n"
            f"Em aberto: {formatar_moeda(registro.get('valor_aberto'))}\n"
            f"Já recebido: {formatar_moeda(registro.get('valor_recebido'))}\n"
            f"Recebimentos: {formatar_inteiro(registro.get('total_recebimentos'))}\n"
            f"Última baixa: {ultimo_recebimento}\n"
            f"Situação: {situacao_atraso}"
        )
        self._aplicar_tooltip_linha(self.tableContasReceber, row, tooltip)

    def _aplicar_tooltip_reembolso(self, row: int, registro: dict[str, Any]) -> None:
        tooltip = (
            f"Venda #{registro.get('venda_id') or '-'}\n"
            f"Tipo: {registro.get('tipo') or '-'}\n"
            f"Status: {registro.get('status') or '-'}\n"
            f"Valor: {formatar_moeda(registro.get('valor_total'))}\n"
            f"Motivo: {registro.get('motivo') or '-'}"
        )
        self._aplicar_tooltip_linha(self.tableReembolsos, row, tooltip)

    @staticmethod
    def _aplicar_tooltip_linha(table: QTableWidget, row: int, tooltip: str) -> None:
        for column in range(table.columnCount()):
            item = table.item(row, column)
            if item:
                item.setToolTip(tooltip)

    @staticmethod
    def _texto_item(table: QTableWidget, row: int, column: int) -> str:
        item = table.item(row, column)
        return item.text() if item else "-"
