from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QComboBox, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem

from core.caixa_session import CaixaSession
from core.session_manager import SessionManager
from modules.financeiro.services.financeiro_service import FinanceiroService
from modules.financeiro.services.reembolso_service import ReembolsoService
from ui.financeiro.painel_financeiro import Ui_PainelFinanceiro
from utils.format_utils import formatar_inteiro, formatar_moeda
from utils.operational_panel_mixin import PainelOperacionalMixin
from utils.ui_messages import confirmar_acao, mostrar_aviso, mostrar_info


class PainelFinanceiroView(QMainWindow, Ui_PainelFinanceiro, PainelOperacionalMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.cmbPdvFiltro: QComboBox
        self.cmbFormaPagamentoFiltro: QComboBox
        self.tableCaixaMovimentacoes: QTableWidget
        self.tablePagamentos: QTableWidget
        self.tableContasReceber: QTableWidget
        self.tableReembolsos: QTableWidget
        self.btnReceberPendencia: QPushButton

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
        return None

    def _configurar_filtros_iniciais(self) -> None:
        self._configurar_periodo_padrao()
        self._carregar_pdvs()
        self._carregar_formas_pagamento()

    def _conectar_eventos(self) -> None:
        self.btnAtualizar.clicked.connect(self._carregar_painel)
        self.btnConsultarVenda.clicked.connect(self._consultar_venda)
        self.btnReceberPendencia.clicked.connect(self._receber_pendencia)
        self.btnRegistrarReembolso.clicked.connect(self._novo_reembolso)
        self.btnAbrirCaixa.clicked.connect(self._abrir_caixa_financeiro)
        self.btnFecharCaixa.clicked.connect(self._fechar_caixa_financeiro)
        self.btnRegistrarMovimento.clicked.connect(self._registrar_movimentacao_financeiro)

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

    def _carregar_painel(self) -> None:
        self._carregar_cards()
        self._carregar_movimentacoes_caixa()
        self._carregar_vendas_registradas()
        self._carregar_contas_receber()
        self._carregar_reembolsos()
        self.lblStatusBar.setText(
            "CSPdv - Modulo Financeiro | "
            f"{self.tableCaixaMovimentacoes.rowCount()} movimentacao(oes), "
            f"{self.tablePagamentos.rowCount()} venda(s), "
            f"{self.tableContasReceber.rowCount()} conta(s), "
            f"{self.tableReembolsos.rowCount()} reembolso(s)"
        )

    def _abrir_caixa_financeiro(self) -> None:
        if not SessionManager.has_permission("vendas.pdv"):
            mostrar_aviso(
                self,
                "Acesso negado",
                "O usuario atual nao possui permissao para abrir caixa por este modulo.",
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
            "Deseja abrir o caixa agora sem sair do modulo financeiro?",
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
                "Caixa nao encontrado",
                "Nao ha um caixa aberto no momento para encerrar por este modulo.",
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
                "Caixa nao encontrado",
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
                "Venda nao encontrada",
                "Nao foi possivel localizar os detalhes da venda selecionada.",
            )
            return

        from modules.financeiro.views.consulta_venda_dialog import ConsultaVendaDialog

        dialog = ConsultaVendaDialog(detalhes, self)
        dialog.exec_()

    def _receber_pendencia(self) -> None:
        if not CaixaSession.has_open_caixa():
            mostrar_aviso(
                self,
                "Caixa nao encontrado",
                "Abra um caixa antes de registrar recebimentos de pendencias.",
            )
            return

        conta_id = self._obter_conta_id_selecionada()
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
                "Conta nao encontrada",
                "Nao foi possivel localizar os dados da conta selecionada.",
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
            mostrar_aviso(self, "Recebimento nao registrado", str(exc))
            return

        self._carregar_painel()
        mostrar_info(
            self,
            "Recebimento registrado",
            f"Conta #{resultado['conta_id']} | Venda #{resultado['venda_id']} | "
            f"Recebido {formatar_moeda(resultado['valor_recebido'])} | "
            f"Saldo {formatar_moeda(resultado['valor_aberto'])}",
        )

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
                "Venda nao encontrada",
                "Nao foi possivel localizar os detalhes da venda selecionada.",
            )
            return

        from modules.financeiro.views.novo_reembolso_dialog import NovoReembolsoDialog

        dialog = NovoReembolsoDialog(detalhes, self)
        if dialog.exec_() != dialog.Accepted or not dialog.resultado:
            return

        sucesso, mensagem, resultado = ReembolsoService.registrar_reembolso(dialog.resultado)
        if not sucesso or resultado is None:
            mostrar_aviso(self, "Reembolso nao registrado", mensagem)
            return

        self._carregar_painel()
        mostrar_info(
            self,
            "Reembolso registrado",
            f"{mensagem}\n\nReembolso #{resultado['reembolso_id']} | Venda #{resultado['venda_id']} | Valor {formatar_moeda(resultado['valor_total'])}",
        )

    def _obter_venda_id_selecionada(self) -> Optional[int]:
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

    def _obter_conta_id_selecionada(self) -> Optional[int]:
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

    def _carregar_cards(self) -> None:
        resumo = FinanceiroService.obter_resumo_financeiro(
            data_inicial=self.dateInicial.date().toPyDate(),
            data_final=self.dateFinal.date().toPyDate(),
            pdv_id=self._combo_data_int(self.cmbPdvFiltro),
            forma_pagamento=self._forma_pagamento_filtro(),
        )
        self.lblSaldoCaixaValor.setText(formatar_moeda(resumo.get("saldo_atual_caixa")))
        self.lblEntradasDiaValor.setText(formatar_moeda(resumo.get("entradas_periodo")))
        self.lblSaidasDiaValor.setText(formatar_moeda(resumo.get("saidas_periodo")))
        self.lblPagamentosPendentesValor.setText(formatar_inteiro(resumo.get("contas_abertas_periodo")))

    def _carregar_movimentacoes_caixa(self) -> None:
        registros = FinanceiroService.listar_movimentacoes_caixa(
            data_inicial=self.dateInicial.date().toPyDate(),
            data_final=self.dateFinal.date().toPyDate(),
            pdv_id=self._combo_data_int(self.cmbPdvFiltro),
        )

        registros.sort(key=lambda r: r.get("data_hora") or 0, reverse=True)

        self.tableCaixaMovimentacoes.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            self._set_table_item(self.tableCaixaMovimentacoes, row, 0, self._formatar_data_hora(registro.get("data_hora")))
            self._set_table_item(self.tableCaixaMovimentacoes, row, 1, str(registro.get("pdv") or "-"))
            self._set_table_item(self.tableCaixaMovimentacoes, row, 2, str(registro.get("operador") or "-"))
            self._set_table_item(self.tableCaixaMovimentacoes, row, 3, str(registro.get("motivo") or "-"))
            self._set_table_item(self.tableCaixaMovimentacoes, row, 4, str(registro.get("forma_pagamento") or "-"))
            self._set_table_item(
                self.tableCaixaMovimentacoes,
                row,
                5,
                formatar_moeda(registro.get("valor")),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )

    def _carregar_vendas_registradas(self) -> None:
        registros = FinanceiroService.listar_vendas_registradas(
            data_inicial=self.dateInicial.date().toPyDate(),
            data_final=self.dateFinal.date().toPyDate(),
            pdv_id=self._combo_data_int(self.cmbPdvFiltro),
            forma_pagamento=self._forma_pagamento_filtro(),
        )

        self.tablePagamentos.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            item_venda = self._set_table_item(
                self.tablePagamentos,
                row,
                0,
                str(registro.get("venda_id") or "-"),
                alignment=Qt.AlignCenter,
            )
            item_venda.setData(Qt.UserRole, int(registro.get("venda_id") or 0))
            self._set_table_item(self.tablePagamentos, row, 1, str(registro.get("cliente") or "-"))
            self._set_table_item(self.tablePagamentos, row, 2, str(registro.get("forma_pagamento") or "-"))
            self._set_table_item(
                self.tablePagamentos,
                row,
                3,
                str(registro.get("status") or "-"),
                alignment=Qt.AlignCenter,
            )
            self._set_table_item(
                self.tablePagamentos,
                row,
                4,
                formatar_moeda(registro.get("valor_total")),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )

    def _carregar_contas_receber(self) -> None:
        registros = FinanceiroService.listar_contas_receber(
            data_inicial=self.dateInicial.date().toPyDate(),
            data_final=self.dateFinal.date().toPyDate(),
            pdv_id=self._combo_data_int(self.cmbPdvFiltro),
        )

        self.tableContasReceber.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            item_conta = self._set_table_item(
                self.tableContasReceber,
                row,
                0,
                str(registro.get("conta_id") or "-"),
                alignment=Qt.AlignCenter,
            )
            item_conta.setData(Qt.UserRole, int(registro.get("venda_id") or 0))
            item_conta.setData(Qt.UserRole + 1, int(registro.get("conta_id") or 0))
            self._set_table_item(self.tableContasReceber, row, 1, str(registro.get("cliente") or "-"))
            self._set_table_item(
                self.tableContasReceber,
                row,
                2,
                self._formatar_data(registro.get("data_vencimento")),
                alignment=Qt.AlignCenter,
            )
            self._set_table_item(
                self.tableContasReceber,
                row,
                3,
                str(registro.get("status") or "-"),
                alignment=Qt.AlignCenter,
            )
            self._set_table_item(
                self.tableContasReceber,
                row,
                4,
                formatar_moeda(registro.get("valor_aberto")),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )

    def _carregar_reembolsos(self) -> None:
        registros = FinanceiroService.listar_reembolsos(
            data_inicial=self.dateInicial.date().toPyDate(),
            data_final=self.dateFinal.date().toPyDate(),
            pdv_id=self._combo_data_int(self.cmbPdvFiltro),
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
        for row, registro in enumerate(registros):
            item_venda = self._set_table_item(
                self.tableReembolsos,
                row,
                0,
                str(registro.get("venda_id") or "-"),
                alignment=Qt.AlignCenter,
            )
            item_venda.setData(Qt.UserRole, int(registro.get("venda_id") or 0))
            self._set_table_item(self.tableReembolsos, row, 1, str(registro.get("tipo") or "-"), alignment=Qt.AlignCenter)
            self._set_table_item(self.tableReembolsos, row, 2, str(registro.get("motivo") or "-"))
            self._set_table_item(self.tableReembolsos, row, 3, str(registro.get("status") or "-"), alignment=Qt.AlignCenter)
            self._set_table_item(
                self.tableReembolsos,
                row,
                4,
                formatar_moeda(registro.get("valor_total")),
                alignment=Qt.AlignRight | Qt.AlignVCenter,
            )

    def _forma_pagamento_filtro(self) -> Optional[str]:
        if self.cmbFormaPagamentoFiltro.currentData() is None:
            return None
        return self.cmbFormaPagamentoFiltro.currentText().strip() or None

    @staticmethod
    def _combo_data_int(combo: QComboBox) -> Optional[int]:
        value = combo.currentData()
        if value in (None, "", 0, "0"):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _set_table_item(
        table: QTableWidget,
        row: int,
        column: int,
        value: str,
        *,
        alignment: Any = Qt.AlignLeft | Qt.AlignVCenter,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(value)
        item.setTextAlignment(int(alignment))
        table.setItem(row, column, item)
        return item

    @staticmethod
    def _formatar_data_hora(value: Any) -> str:
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y %H:%M")
        return "-"

    @staticmethod
    def _formatar_data(value: Any) -> str:
        if hasattr(value, "strftime"):
            return value.strftime("%d/%m/%Y")
        return str(value or "-")
