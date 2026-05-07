from PyQt5.QtWidgets import QWidget

from modules.admin.services.configuracoes_service import ConfiguracoesService
from ui.admin.configuracoes import Ui_ConfiguracoesWidget
from utils.format_utils import formatar_decimal
from utils.ui_messages import mostrar_aviso, mostrar_info


class ConfiguracoesView(QWidget, Ui_ConfiguracoesWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._configurar_defaults()
        self._carregar_parametros_iniciais()
        self._conectar_eventos()

    def _configurar_defaults(self) -> None:
        self.lineEditRazaoSocial.setText("Empresa em configuração")
        self.lineEditFundoSugerido.setText("0,00")
        self.lineEditHorasSessao.setText("12")
        self.lineEditIntervaloBackup.setText("24")
        self.lineEditVersaoReferencia.setText("CSPdv v1.0.0")
        self.checkVendaRapidaAdmin.setChecked(True)
        self.checkBloquearPromocoesSimultaneas.setChecked(True)
        self.checkAtivarPorVigencia.setChecked(True)
        self.checkRestaurarLogin.setChecked(True)
        self.checkBloquearFecharAppCaixa.setChecked(True)
        self.checkExigirAdminSangria.setChecked(True)
        self.checkExigirAdminReembolso.setChecked(True)
        self.checkExigirAdminDiferenca.setChecked(True)
        self._repopular_moedas()
        self._repopular_parametros_venda()
        self._repopular_parametros_sistema()

    def _repopular_moedas(self) -> None:
        self.comboMoeda.clear()
        self.comboMoeda.addItems(ConfiguracoesService.opcoes_moeda())

    def _repopular_parametros_venda(self) -> None:
        self.comboClientePadrao.clear()
        self.comboClientePadrao.addItems(ConfiguracoesService.opcoes_cliente_padrao())
        self.comboRegraDesconto.clear()
        self.comboRegraDesconto.addItems(ConfiguracoesService.opcoes_regra_desconto())
        self.comboPrioridadePromocao.clear()
        self.comboPrioridadePromocao.addItems(ConfiguracoesService.opcoes_prioridade_promocional())

    def _repopular_parametros_sistema(self) -> None:
        self.comboPerfilLog.clear()
        self.comboPerfilLog.addItems(ConfiguracoesService.opcoes_perfil_log())

    def _carregar_parametros_iniciais(self) -> None:
        try:
            payload = ConfiguracoesService.carregar_empresa_pdv()
        except Exception as exc:
            mostrar_aviso(
                self,
                "Configurações",
                f"Não foi possível carregar os dados iniciais da configuração.\n\nDetalhes: {exc}",
            )
            return

        empresa = payload.get("empresa") or {}
        pdvs = payload.get("pdvs") or []
        self.lineEditRazaoSocial.setText(str(empresa.get("razao_social") or "Empresa em configuração"))

        self.comboPdvPadrao.clear()
        self.comboPdvPadrao.addItem("Selecionar depois", None)
        indice_padrao = 0
        pdv_padrao_id = empresa.get("pdv_padrao_id")

        for indice, pdv in enumerate(pdvs, start=1):
            descricao = str(pdv.get("descricao") or "").strip()
            texto = str(pdv.get("identificacao") or "PDV")
            if descricao:
                texto = f"{texto} - {descricao}"
            self.comboPdvPadrao.addItem(texto, pdv.get("id"))
            if pdv_padrao_id is not None and int(pdv.get("id") or 0) == int(pdv_padrao_id):
                indice_padrao = indice

        self.comboPdvPadrao.setCurrentIndex(indice_padrao)

        moeda_label = ConfiguracoesService.label_moeda(empresa.get("moeda_padrao"))
        moeda_index = self.comboMoeda.findText(moeda_label)
        self.comboMoeda.setCurrentIndex(moeda_index if moeda_index >= 0 else 0)

        cliente_label = ConfiguracoesService.label_cliente_padrao(empresa.get("cliente_padrao_venda"))
        cliente_index = self.comboClientePadrao.findText(cliente_label)
        self.comboClientePadrao.setCurrentIndex(cliente_index if cliente_index >= 0 else 0)

        desconto_label = ConfiguracoesService.label_regra_desconto(empresa.get("regra_desconto_venda"))
        desconto_index = self.comboRegraDesconto.findText(desconto_label)
        self.comboRegraDesconto.setCurrentIndex(desconto_index if desconto_index >= 0 else 0)

        self.checkVendaRapidaAdmin.setChecked(bool(empresa.get("habilitar_venda_rapida_admin", True)))
        self.checkPermitirVendaSemEstoque.setChecked(bool(empresa.get("permitir_venda_sem_estoque", False)))
        self.lineEditFundoSugerido.setText(formatar_decimal(empresa.get("fundo_inicial_sugerido") or 0.0))
        self.checkExigirAdminSangria.setChecked(bool(empresa.get("exigir_admin_sangria", True)))
        self.checkExigirAdminReembolso.setChecked(bool(empresa.get("exigir_admin_reembolso", True)))
        self.checkExigirAdminDiferenca.setChecked(bool(empresa.get("exigir_admin_diferenca_fechamento", True)))

        prioridade_label = ConfiguracoesService.label_prioridade_promocional(
            empresa.get("prioridade_promocional")
        )
        prioridade_index = self.comboPrioridadePromocao.findText(prioridade_label)
        self.comboPrioridadePromocao.setCurrentIndex(prioridade_index if prioridade_index >= 0 else 0)
        self.checkBloquearPromocoesSimultaneas.setChecked(
            bool(empresa.get("bloquear_promocoes_simultaneas", True))
        )
        self.checkAtivarPorVigencia.setChecked(bool(empresa.get("ativar_promocoes_por_vigencia", True)))

        self.lineEditHorasSessao.setText(str(int(empresa.get("horas_sessao_persistida") or 12)))
        self.checkRestaurarLogin.setChecked(bool(empresa.get("restaurar_login_automaticamente", True)))
        self.checkBloquearFecharAppCaixa.setChecked(
            bool(empresa.get("bloquear_fechamento_programa_caixa_aberto", True))
        )

        self.lineEditIntervaloBackup.setText(str(int(empresa.get("intervalo_backup_horas") or 24)))
        perfil_log_label = ConfiguracoesService.label_perfil_log(empresa.get("perfil_log"))
        perfil_log_index = self.comboPerfilLog.findText(perfil_log_label)
        self.comboPerfilLog.setCurrentIndex(perfil_log_index if perfil_log_index >= 0 else 0)
        self.lineEditVersaoReferencia.setText(str(empresa.get("versao_referencia") or "CSPdv v1.0.0"))

    def _conectar_eventos(self) -> None:
        self.btnSalvarParametros.clicked.connect(self._salvar_estrutura_inicial)
        self.btnRestaurarPadroes.clicked.connect(self._restaurar_defaults)

    def _salvar_estrutura_inicial(self) -> None:
        sucesso_empresa, mensagem_empresa = ConfiguracoesService.salvar_empresa_pdv(
            razao_social=self.lineEditRazaoSocial.text(),
            pdv_padrao_id=self.comboPdvPadrao.currentData(),
            moeda_label=self.comboMoeda.currentText(),
        )
        if not sucesso_empresa:
            mostrar_aviso(self, "Configurações", mensagem_empresa)
            return

        sucesso_vendas, mensagem_vendas = ConfiguracoesService.salvar_parametros_venda(
            cliente_padrao_label=self.comboClientePadrao.currentText(),
            regra_desconto_label=self.comboRegraDesconto.currentText(),
            habilitar_venda_rapida_admin=self.checkVendaRapidaAdmin.isChecked(),
            permitir_venda_sem_estoque=self.checkPermitirVendaSemEstoque.isChecked(),
        )
        if not sucesso_vendas:
            mostrar_aviso(self, "Configurações", mensagem_vendas)
            return

        sucesso_caixa, mensagem_caixa = ConfiguracoesService.salvar_parametros_caixa(
            fundo_inicial_sugerido_texto=self.lineEditFundoSugerido.text(),
            exigir_admin_sangria=self.checkExigirAdminSangria.isChecked(),
            exigir_admin_reembolso=self.checkExigirAdminReembolso.isChecked(),
            exigir_admin_diferenca_fechamento=self.checkExigirAdminDiferenca.isChecked(),
        )
        if not sucesso_caixa:
            mostrar_aviso(self, "Configurações", mensagem_caixa)
            return

        sucesso_promocoes, mensagem_promocoes = ConfiguracoesService.salvar_parametros_promocoes(
            prioridade_promocional_label=self.comboPrioridadePromocao.currentText(),
            bloquear_promocoes_simultaneas=self.checkBloquearPromocoesSimultaneas.isChecked(),
            ativar_promocoes_por_vigencia=self.checkAtivarPorVigencia.isChecked(),
        )
        if not sucesso_promocoes:
            mostrar_aviso(self, "Configurações", mensagem_promocoes)
            return

        sucesso_seguranca, mensagem_seguranca = ConfiguracoesService.salvar_parametros_seguranca(
            horas_sessao_persistida_texto=self.lineEditHorasSessao.text(),
            restaurar_login_automaticamente=self.checkRestaurarLogin.isChecked(),
            bloquear_fechamento_programa_caixa_aberto=self.checkBloquearFecharAppCaixa.isChecked(),
        )
        if not sucesso_seguranca:
            mostrar_aviso(self, "Configurações", mensagem_seguranca)
            return

        sucesso_sistema, mensagem_sistema = ConfiguracoesService.salvar_parametros_sistema(
            intervalo_backup_horas_texto=self.lineEditIntervaloBackup.text(),
            perfil_log_label=self.comboPerfilLog.currentText(),
            versao_referencia=self.lineEditVersaoReferencia.text(),
        )
        if not sucesso_sistema:
            mostrar_aviso(self, "Configurações", mensagem_sistema)
            return

        self._carregar_parametros_iniciais()
        janela_principal = self.window()
        if janela_principal is not None and hasattr(janela_principal, "_atualizar_acao_caixa_dashboard"):
            janela_principal._atualizar_acao_caixa_dashboard()
        mostrar_info(
            self,
            "Configurações",
            (
                f"{mensagem_empresa}\n"
                f"{mensagem_vendas}\n"
                f"{mensagem_caixa}\n"
                f"{mensagem_promocoes}\n"
                f"{mensagem_seguranca}\n"
                f"{mensagem_sistema}"
            ),
        )

    def _restaurar_defaults(self) -> None:
        self._configurar_defaults()
        self._carregar_parametros_iniciais()
        mostrar_info(
            self,
            "Configurações",
            "Os valores visuais padrão foram restaurados e os dados persistidos já configurados foram recarregados.",
        )
