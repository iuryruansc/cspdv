from typing import Any, Dict, List

from PyQt5.QtCore import QDateTime, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QButtonGroup, QMainWindow, QPushButton, QShortcut, QTableWidgetItem

from core.session_manager import SessionManager
from modules.admin.services.configuracoes_service import ConfiguracoesService
from modules.admin.views.configuracoes_view import ConfiguracoesView
from modules.admin.views.widgets import ManagementPageWidget
from ui.admin.painel_admin import Ui_PainelAdmin
from utils.system_runtime import descricao_ambiente, versao_referencia
from utils.ui_messages import confirmar_acao, mostrar_aviso, mostrar_info
from utils.window_size_utils import aplicar_tamanho_proporcional_tela


class PainelAdminView(QMainWindow, Ui_PainelAdmin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        aplicar_tamanho_proporcional_tela(self)

        self._management_configs: Dict[str, Dict[str, Any]] = {}
        self._setup_user_context()
        self._setup_dashboard_actions()
        self._setup_datetime()
        self._setup_management_area()
        self._setup_navigation()
        self._setup_actions()
        self._setup_shortcuts()
        self._show_dashboard()

    def _setup_dashboard_actions(self) -> None:
        self.btnFecharCaixaDashboard = QPushButton("Fechar Caixa", self.centralWidget)
        self.btnFecharCaixaDashboard.setMinimumSize(172, 38)
        self.btnFecharCaixaDashboard.setStyleSheet(
            """
QPushButton {
 background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5b23c, stop:1 #dc9215);
 color: #173a5f;
 font-size: 12px;
 font-weight: bold;
 border: none;
 border-radius: 5px;
 padding: 6px 16px;
}
QPushButton:hover {
 background: #c9820a;
 color: white;
}
            """
        )
        self.sectionTitleHLayout.addWidget(self.btnFecharCaixaDashboard)
        self.btnFecharCaixaDashboard.hide()

    def _setup_user_context(self) -> None:
        usuario = SessionManager.current_user()
        if usuario:
            nome = usuario["nome"].upper()
            self.lblOperadorInfo.setText(f"Operador: {nome}")
            self.lblStatusBar.setText(f"CSPdv - Operador: {nome}  |  Painel Administrativo")
        else:
            self.lblOperadorInfo.setText("Operador: Não logado")
            self.lblStatusBar.setText("CSPdv - Painel Administrativo")
        self.lblStatusVersao.setText(versao_referencia())
        self.lblStatusVersao.setToolTip(descricao_ambiente())

    def _setup_datetime(self) -> None:
        self._update_datetime()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_datetime)
        self.timer.start(1000)

    def _setup_management_area(self) -> None:
        self.managementPage = ManagementPageWidget(self.centralWidget)
        self.managementPage.hide()
        self.mainContentVLayout.addWidget(self.managementPage)
        self.configuracoesPage = ConfiguracoesView(self.centralWidget)
        self.configuracoesPage.hide()
        self.mainContentVLayout.addWidget(self.configuracoesPage)

        self._management_configs = {
            "produtos": {
                "button": self.btnNavProdutosCadastro,
                "title": "Produtos",
                "section_title": "Gerenciamento de Produtos",
                "hint": "Consulte itens cadastrados, acompanhe preco, estoque e relacoes principais antes de abrir o cadastro completo.",
                "columns": [
                    ("codigo_barras", "Codigo de Barras"),
                    ("nome", "Produto"),
                    ("categoria", "Categoria"),
                    ("marca", "Marca"),
                    ("fornecedor", "Fornecedor"),
                    ("preco_venda", "Preco Venda"),
                    ("quantidade_estoque", "Estoque"),
                    ("ativo", "Ativo"),
                ],
                "loader": self._load_produtos,
                "new_action": self._open_cadastro_produto,
                "new_label": "Novo produto",
                "shortcut": "F1",
            },
            "marcas": {
                "button": self.btnNavMarcas,
                "title": "Marcas",
                "section_title": "Gerenciamento de Marcas",
                "hint": "Marcas ficam dentro do painel para agilizar cadastros auxiliares e manter o operador no mesmo contexto.",
                "columns": [
                    ("id", "ID"),
                    ("nome_marca", "Marca"),
                    ("ativo", "Ativo"),
                ],
                "loader": self._load_marcas,
                "new_action": self._open_cadastro_marca,
                "new_label": "Nova marca",
                "shortcut": "F2",
            },
            "fornecedores": {
                "button": self.btnNavFornecedores,
                "title": "Fornecedores",
                "section_title": "Gerenciamento de Fornecedores",
                "hint": "Consulte os fornecedores ativos e acesse o cadastro completo quando precisar de uma inclusao mais detalhada.",
                "columns": [
                    ("nome_fantasia", "Nome Fantasia"),
                    ("cnpj_cpf", "CNPJ / CPF"),
                    ("telefone", "Telefone"),
                    ("cidade", "Cidade"),
                    ("estado", "UF"),
                    ("ativo", "Ativo"),
                ],
                "loader": self._load_fornecedores,
                "new_action": self._open_cadastro_fornecedor,
                "new_label": "Novo fornecedor",
                "shortcut": "F3",
            },
            "categorias": {
                "button": self.btnNavCategorias,
                "title": "Categorias",
                "section_title": "Gerenciamento de Categorias",
                "hint": "Categorias curtas tambem permanecem dentro do admin para um fluxo mais rapido de organizacao dos produtos.",
                "columns": [
                    ("id", "ID"),
                    ("nome", "Categoria"),
                    ("ativo", "Ativo"),
                ],
                "loader": self._load_categorias,
                "new_action": self._open_cadastro_categoria,
                "new_label": "Nova categoria",
                "shortcut": "F4",
            },
            "clientes": {
                "button": self.btnNavClientesCadastro,
                "title": "Clientes",
                "section_title": "Gerenciamento de Clientes",
                "hint": "Consulte clientes ativos, acompanhe os dados principais e abra o cadastro completo quando precisar atualizar o relacionamento.",
                "columns": [
                    ("nome", "Nome"),
                    ("cpf", "CPF"),
                    ("telefone", "Telefone"),
                    ("cidade", "Cidade"),
                    ("estado", "UF"),
                    ("ativo", "Ativo"),
                ],
                "loader": self._load_clientes,
                "new_action": self._open_cadastro_cliente,
                "new_label": "Novo cliente",
                "shortcut": "F5",
            },
        }

        for config in self._management_configs.values():
            button = config["button"]
            shortcut = config.get("shortcut")
            if shortcut:
                button.setText(f"({shortcut}) {config['title']}")

    def _setup_navigation(self) -> None:
        self.navGroup = QButtonGroup(self)
        self.navGroup.setExclusive(True)
        for button in (
            self.btnNavDashboard,
            self.btnNavProdutos,
            self.btnNavUsuarios,
            self.btnNavVendas,
            self.btnNavClientes,
            self.btnNavLotes,
            self.btnNavConfiguracoes,
        ):
            self.navGroup.addButton(button)

        self.btnNavDashboard.clicked.connect(lambda _=False: self._show_dashboard())
        self.btnNavProdutos.clicked.connect(lambda _=False: self._show_management_page("produtos"))
        self.btnNavClientes.clicked.connect(lambda _=False: self._show_management_page("clientes"))
        self.btnNavConfiguracoes.clicked.connect(lambda _=False: self._show_configuracoes())

        for key, config in self._management_configs.items():
            button = config["button"]
            button.clicked.connect(lambda _, target=key: self._show_management_page(target))

    def _setup_actions(self) -> None:
        self.btnAcaoCadProduto.clicked.connect(self._open_cadastro_produto)
        self.btnAcaoBackup.clicked.connect(self._open_cadastro_marca)
        self.btnAcaoConfig.clicked.connect(self._open_cadastro_categoria)
        self.btnAcaoCadFornecedor.clicked.connect(self._open_cadastro_fornecedor)
        self.btnAcaoCadCliente.clicked.connect(self._open_cadastro_cliente)
        self.btnFrenteCaixa.clicked.connect(self._open_frente_caixa)
        self.btnFecharCaixaDashboard.clicked.connect(self._open_fechamento_caixa_dashboard)
        self.btnSair.clicked.connect(self._exit)
        self.managementPage.btnAtualizar.clicked.connect(self._refresh_current_management_page)
        self.managementPage.btnDetalhes.clicked.connect(self._abrir_detalhes_produto)
        self.managementPage.btnAjustarQuantidade.clicked.connect(self._open_ajuste_quantidade)
        self.managementPage.btnToggleAtivo.clicked.connect(self._toggle_registro_ativo)
        self.managementPage.btnEditar.clicked.connect(self._editar_registro)

    def _setup_shortcuts(self) -> None:
        self.shortcutF1 = QShortcut(QKeySequence("F1"), self)
        self.shortcutF1.activated.connect(lambda: self._show_management_page("produtos"))
        self.shortcutF2 = QShortcut(QKeySequence("F2"), self)
        self.shortcutF2.activated.connect(lambda: self._show_management_page("marcas"))
        self.shortcutF3 = QShortcut(QKeySequence("F3"), self)
        self.shortcutF3.activated.connect(lambda: self._show_management_page("fornecedores"))
        self.shortcutF4 = QShortcut(QKeySequence("F4"), self)
        self.shortcutF4.activated.connect(lambda: self._show_management_page("categorias"))
        self.shortcutF5 = QShortcut(QKeySequence("F5"), self)
        self.shortcutF5.activated.connect(lambda: self._show_management_page("clientes"))

    def _select_primary_nav(self, key: str) -> None:
        if key == "clientes":
            if not self.btnNavClientes.isChecked():
                self.btnNavClientes.setChecked(True)
            return

        if not self.btnNavProdutos.isChecked():
            self.btnNavProdutos.setChecked(True)

    def _show_dashboard(self) -> None:
        self.btnNavDashboard.setChecked(True)
        self.lblSectionTitle.setText("Dashboard Administrativo")
        self.btnFrenteCaixa.show()
        self.btnFecharCaixaDashboard.show()
        self._atualizar_acao_caixa_dashboard()
        self.managementPage.hide()
        self.configuracoesPage.hide()
        self.cardVendasHoje.show()
        self.cardFaturamento.show()
        self.cardProdutos.show()
        self.cardClientes.show()
        self.frameUltimasVendas.show()
        self._mark_subnav_button(None)
        self._load_dashboard_cards()

    def _show_management_page(self, key: str) -> None:
        config = self._management_configs[key]
        self._select_primary_nav(key)
        self.lblSectionTitle.setText(config["section_title"])
        self.btnFrenteCaixa.hide()
        self.btnFecharCaixaDashboard.hide()
        self.cardVendasHoje.hide()
        self.cardFaturamento.hide()
        self.cardProdutos.hide()
        self.cardClientes.hide()
        self.frameUltimasVendas.hide()
        self.managementPage.show()
        self.configuracoesPage.hide()
        self.managementPage.btnNovo.setText(config["new_label"])
        self.managementPage.set_details_enabled(key == "produtos")
        self.managementPage.set_quantity_adjustment_enabled(key == "produtos")
        self.managementPage.set_edit_enabled(key in {"produtos", "marcas", "fornecedores", "categorias", "clientes"})
        self.managementPage.set_toggle_enabled(key in {"produtos", "marcas", "fornecedores", "categorias", "clientes"})
        try:
            self.managementPage.btnNovo.clicked.disconnect()
        except TypeError:
            pass
        self.managementPage.btnNovo.clicked.connect(config["new_action"])
        self._mark_subnav_button(config["button"])
        self._populate_management_page(key)

    def _show_configuracoes(self) -> None:
        self.btnNavConfiguracoes.setChecked(True)
        self.lblSectionTitle.setText("Configurações do Sistema")
        self.btnFrenteCaixa.hide()
        self.btnFecharCaixaDashboard.hide()
        self.cardVendasHoje.hide()
        self.cardFaturamento.hide()
        self.cardProdutos.hide()
        self.cardClientes.hide()
        self.frameUltimasVendas.hide()
        self.managementPage.hide()
        self.configuracoesPage.show()
        self._mark_subnav_button(None)

    def _mark_subnav_button(self, active_button: QPushButton | None) -> None:
        for config in self._management_configs.values():
            button = config["button"]
            if button is active_button:
                button.setStyleSheet(
                    "color: #1a5fa0; background-color: rgba(53,133,200,30); border-bottom: 2px solid #3585c8;"
                )
            else:
                button.setStyleSheet("")

    def _populate_management_page(self, key: str) -> None:
        config = self._management_configs[key]
        error_message = None
        try:
            rows = config["loader"]()
        except Exception as exc:
            rows = []
            error_message = (
                f"Não foi possível consultar {config['title'].lower()} agora.\n\nDetalhes: {exc}"
            )
        self.managementPage.configure(
            title=config["title"],
            hint=config["hint"],
            columns=config["columns"],
            rows=rows,
        )
        self._current_management_key = key
        if error_message:
            mostrar_aviso(self, "Falha ao carregar dados", error_message)

    def _refresh_current_management_page(self) -> None:
        current_key = getattr(self, "_current_management_key", None)
        if current_key:
            self._populate_management_page(current_key)

    def _load_produtos(self) -> List[Dict[str, Any]]:
        from modules.produtos.models.produto_model import ProdutoModel

        return ProdutoModel.listar_resumo()

    def _load_marcas(self) -> List[Dict[str, Any]]:
        from modules.marcas.models.marca_model import MarcaModel

        return MarcaModel.listar()

    def _load_fornecedores(self) -> List[Dict[str, Any]]:
        from modules.fornecedores.models.fornecedor_model import FornecedorModel

        return FornecedorModel.listar_resumo()

    def _load_categorias(self) -> List[Dict[str, Any]]:
        from modules.categorias.models.categoria_model import CategoriaModel

        return CategoriaModel.listar()

    def _load_clientes(self) -> List[Dict[str, Any]]:
        from modules.clientes.models.cliente_model import ClienteModel

        return ClienteModel.listar_resumo()

    def _open_cadastro_produto(self) -> None:
        from modules.produtos.views.cadastro_produto_view import CadastroProdutoView

        self._abrir_cadastro_externo(CadastroProdutoView, "cadastro_produto", admin_view=self)

    def _open_cadastro_fornecedor(self) -> None:
        from modules.fornecedores.views.cadastro_fornecedor_view import CadastroFornecedorView

        self._abrir_cadastro_externo(CadastroFornecedorView, "cadastro_fornecedor", admin_view=self)

    def _open_cadastro_marca(self) -> None:
        from modules.marcas.views.cadastro_marca_view import CadastroMarcaView

        dialog = CadastroMarcaView(self)
        if dialog.exec_():
            self._refresh_current_management_page()

    def _open_cadastro_categoria(self) -> None:
        from modules.categorias.views.cadastro_categoria_view import CadastroCategoriaView

        dialog = CadastroCategoriaView(self)
        if dialog.exec_():
            self._refresh_current_management_page()

    def _open_cadastro_cliente(self) -> None:
        from modules.clientes.views.cadastro_cliente_view import CadastroClienteView

        self._abrir_cadastro_externo(CadastroClienteView, "cadastro_cliente", admin_view=self)

    def _abrir_cadastro_externo(self, view_cls, attr_name: str, **kwargs) -> None:
        self.hide()
        view = view_cls(**kwargs)
        setattr(self, attr_name, view)
        view.show()

    def _obter_registro_selecionado(self, titulo: str, mensagem: str) -> Dict[str, Any] | None:
        row = self.managementPage.selected_row()
        if row:
            return row
        mostrar_info(self, titulo, mensagem)
        return None

    def _obter_contexto_status(self, current_key: str, row: Dict[str, Any]) -> Dict[str, Any] | None:
        if current_key == "produtos":
            from modules.produtos.services.produto_service import ProdutoService

            return {
                "entity_label": "produto",
                "nome": str(row.get("nome") or "produto"),
                "entity_id": row.get("id"),
                "service_call": ProdutoService.alternar_status,
                "invalid_title": "Registro inválido",
            }
        if current_key == "marcas":
            from modules.marcas.services.marca_service import MarcaService

            return {
                "entity_label": "marca",
                "nome": str(row.get("nome_marca") or "marca"),
                "entity_id": row.get("id"),
                "service_call": MarcaService.alternar_status,
                "invalid_title": "Registro inválido",
            }
        if current_key == "categorias":
            from modules.categorias.services.categoria_service import CategoriaService

            return {
                "entity_label": "categoria",
                "nome": str(row.get("nome") or "categoria"),
                "entity_id": row.get("id"),
                "service_call": CategoriaService.alternar_status,
                "invalid_title": "Registro inválido",
            }
        if current_key == "fornecedores":
            from modules.fornecedores.services.fornecedor_service import FornecedorService

            return {
                "entity_label": "fornecedor",
                "nome": str(row.get("nome_fantasia") or "fornecedor"),
                "entity_id": row.get("id_fornecedor"),
                "service_call": FornecedorService.alternar_status,
                "invalid_title": "Registro inválido",
            }
        if current_key == "clientes":
            from modules.clientes.services.cliente_service import ClienteService

            return {
                "entity_label": "cliente",
                "nome": str(row.get("nome") or "cliente"),
                "entity_id": row.get("id"),
                "service_call": ClienteService.alternar_status,
                "invalid_title": "Registro inválido",
            }
        return None

    def _open_ajuste_quantidade(self) -> None:
        if getattr(self, "_current_management_key", None) != "produtos":
            return

        produto = self._obter_registro_selecionado(
            "Selecione um produto",
            "Escolha um produto na tabela antes de ajustar a quantidade.",
        )
        if not produto:
            return

        from modules.produtos.views.ajuste_quantidade_dialog import AjusteQuantidadeDialog

        dialog = AjusteQuantidadeDialog(produto, self)
        if dialog.exec_():
            self._refresh_current_management_page()

    def _abrir_detalhes_produto(self) -> None:
        if getattr(self, "_current_management_key", None) != "produtos":
            return

        produto = self._obter_registro_selecionado(
            "Selecione um produto",
            "Escolha um produto na tabela antes de visualizar os detalhes.",
        )
        if not produto:
            return

        produto_id = produto.get("id")
        if produto_id is None:
            mostrar_aviso(self, "Produto inválido", "Não foi possível identificar o produto selecionado.")
            return

        from modules.produtos.models.produto_model import ProdutoModel
        from modules.produtos.views.detalhes_produto_dialog import DetalhesProdutoDialog

        detalhes = ProdutoModel.buscar_por_id(int(produto_id))
        if not detalhes:
            mostrar_aviso(self, "Produto não encontrado", "Não foi possível carregar os detalhes do produto selecionado.")
            return

        dialog = DetalhesProdutoDialog(detalhes, self)
        dialog.exec_()

    def _toggle_registro_ativo(self) -> None:
        current_key = getattr(self, "_current_management_key", None)
        if current_key not in {"produtos", "marcas", "fornecedores", "categorias", "clientes"}:
            return

        row = self._obter_registro_selecionado(
            "Selecione um registro",
            "Escolha um registro na tabela antes de alterar o status.",
        )
        if not row:
            return

        contexto = self._obter_contexto_status(current_key, row)
        if not contexto:
            return

        entity_label = str(contexto["entity_label"])
        nome = str(contexto["nome"])
        entity_id = contexto["entity_id"]
        service_call = contexto["service_call"]

        if entity_id is None:
            mostrar_aviso(self, str(contexto["invalid_title"]), "Não foi possível identificar o registro selecionado.")
            return

        ativo_atual = str(row.get("ativo") or "N").strip().upper()
        acao = "desativar" if ativo_atual == "S" else "ativar"
        confirmacao = confirmar_acao(
            self,
            "Confirmar alteração",
            f"Deseja {acao} o {entity_label} '{nome}'?",
        )
        if not confirmacao:
            return

        sucesso, mensagem = service_call(entity_id)
        if not sucesso:
            mostrar_aviso(self, "Status não alterado", mensagem)
            return

        mostrar_info(self, "Status atualizado", mensagem)
        self._refresh_current_management_page()

    def _editar_registro(self) -> None:
        current_key = getattr(self, "_current_management_key", None)
        if current_key not in {"produtos", "marcas", "fornecedores", "categorias", "clientes"}:
            return

        row = self._obter_registro_selecionado(
            "Selecione um registro",
            "Escolha um registro na tabela antes de editar.",
        )
        if not row:
            return

        if current_key == "produtos":
            registro_id = row.get("id")
            if registro_id is None:
                mostrar_aviso(self, "Produto inválido", "Não foi possível identificar o produto selecionado para edição.")
                return
            from modules.produtos.views.cadastro_produto_view import CadastroProdutoView

            self._abrir_cadastro_externo(
                CadastroProdutoView,
                "cadastro_produto",
                produto_id=int(registro_id),
                admin_view=self,
            )
            return

        if current_key == "marcas":
            registro_id = row.get("id")
            if registro_id is None:
                mostrar_aviso(self, "Marca inválida", "Não foi possível identificar a marca selecionada.")
                return
            from modules.marcas.views.cadastro_marca_view import CadastroMarcaView

            dialog = CadastroMarcaView(self, marca_id=int(registro_id))
            if dialog.exec_():
                self._refresh_current_management_page()
            return

        if current_key == "categorias":
            registro_id = row.get("id")
            if registro_id is None:
                mostrar_aviso(self, "Categoria inválida", "Não foi possível identificar a categoria selecionada.")
                return
            from modules.categorias.views.cadastro_categoria_view import CadastroCategoriaView

            dialog = CadastroCategoriaView(self, categoria_id=int(registro_id))
            if dialog.exec_():
                self._refresh_current_management_page()
            return

        if current_key == "clientes":
            registro_id = row.get("id")
            if registro_id is None:
                mostrar_aviso(self, "Cliente inválido", "Não foi possível identificar o cliente selecionado.")
                return
            from modules.clientes.views.cadastro_cliente_view import CadastroClienteView

            self._abrir_cadastro_externo(
                CadastroClienteView,
                "cadastro_cliente",
                cliente_id=int(registro_id),
                admin_view=self,
            )
            return

        registro_id = row.get("id_fornecedor")
        if registro_id is None:
            mostrar_aviso(self, "Fornecedor inválido", "Não foi possível identificar o fornecedor selecionado.")
            return
        from modules.fornecedores.views.cadastro_fornecedor_view import CadastroFornecedorView

        self._abrir_cadastro_externo(
            CadastroFornecedorView,
            "cadastro_fornecedor",
            fornecedor_id=int(registro_id),
            admin_view=self,
        )

    def _update_datetime(self) -> None:
        current = QDateTime.currentDateTime()
        self.lblDataHora.setText(current.toString("dd/MM/yyyy  hh:mm:ss"))

    def _load_dashboard_cards(self) -> None:
        from modules.admin.services.dashboard_service import DashboardAdminService

        try:
            resumo = DashboardAdminService.carregar_dashboard()
        except Exception as exc:
            self.lblVendasHojeValor.setText("0")
            self.lblFaturamentoValor.setText("R$ 0,00")
            self.lblProdutosValor.setText("0")
            self.lblClientesValor.setText("0")
            self._atualizar_resumo_estrutura({})
            self._populate_dashboard_sales([])
            mostrar_aviso(
                self,
                "Dashboard indisponível",
                f"Não foi possível carregar os indicadores do dashboard agora.\n\nDetalhes: {exc}",
            )
            return

        self.lblVendasHojeValor.setText(str(resumo["vendas_hoje"]))
        self.lblFaturamentoValor.setText(str(resumo["faturamento_dia"]))
        self.lblProdutosValor.setText(str(resumo["produtos_ativos"]))
        self.lblClientesValor.setText(str(resumo["clientes_ativos"]))
        self._atualizar_resumo_estrutura(resumo)
        self._populate_dashboard_sales(resumo["ultimas_vendas"])
        self._atualizar_acao_caixa_dashboard()

    def _atualizar_resumo_estrutura(self, resumo: Dict[str, Any]) -> None:
        self.lblResumoUsuarios.setText(f"Usuários ativos: {int(resumo.get('usuarios_ativos') or 0)}")
        self.lblResumoPerfis.setText(f"Perfis ativos: {int(resumo.get('perfis_ativos') or 0)}")
        self.lblResumoPdvs.setText(f"PDVs ativos: {int(resumo.get('pdvs_ativos') or 0)}")
        self.lblResumoCaixas.setText(f"Caixas abertos: {int(resumo.get('caixas_abertos') or 0)}")
        self.lblResumoFormasPagamento.setText(
            f"Formas de pagamento: {int(resumo.get('formas_pagamento_ativas') or 0)}"
        )

    def _atualizar_acao_caixa_dashboard(self) -> None:
        from core.caixa_session import CaixaSession
        from modules.venda.services.caixa_service import CaixaService

        usuario = SessionManager.current_user() or {}
        parametros_venda = ConfiguracoesService.carregar_parametros_venda()
        venda_rapida_habilitada = bool(parametros_venda.get("habilitar_venda_rapida_admin", True))
        if not CaixaSession.has_open_caixa():
            CaixaService.restaurar_caixa_aberto(usuario.get("id"))

        if CaixaSession.has_open_caixa():
            if venda_rapida_habilitada:
                self.btnFrenteCaixa.setText("Venda Rápida")
                self.btnFrenteCaixa.setToolTip("Abre o fluxo compacto de venda sem sair do painel admin.")
                self.btnFrenteCaixa.setEnabled(True)
            else:
                self.btnFrenteCaixa.setText("Venda Rápida desabilitada")
                self.btnFrenteCaixa.setToolTip(
                    "A Venda Rápida está desabilitada em Configurações > Parâmetros de Venda."
                )
                self.btnFrenteCaixa.setEnabled(False)
            self.btnFecharCaixaDashboard.show()
            self.btnFecharCaixaDashboard.setToolTip("Abre o fechamento do caixa atual diretamente no painel admin.")
            return

        self.btnFrenteCaixa.setText("Abrir Frente de Caixa")
        self.btnFrenteCaixa.setToolTip("Abre o caixa para habilitar as vendas no contexto administrativo.")
        self.btnFrenteCaixa.setEnabled(True)
        self.btnFecharCaixaDashboard.hide()

    def _populate_dashboard_sales(self, rows: List[Dict[str, Any]]) -> None:
        self.tableUltimasVendas.setRowCount(len(rows))
        headers = self.tableUltimasVendas.horizontalHeader()
        headers.setStretchLastSection(False)

        for row_index, row in enumerate(rows):
            values = (
                str(row.get("numero_venda") or "-"),
                str(row.get("data_hora") or "-"),
                str(row.get("operador") or "-"),
                str(row.get("forma_pagamento") or "-"),
                str(row.get("total") or "R$ 0,00"),
            )
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(value)
                self.tableUltimasVendas.setItem(row_index, column_index, item)

        headers.resizeSection(0, 86)
        headers.resizeSection(1, 120)
        headers.resizeSection(2, 140)
        headers.resizeSection(3, 120)
        headers.setStretchLastSection(True)

    def _open_frente_caixa(self) -> None:
        if not SessionManager.has_permission("vendas.pdv"):
            mostrar_aviso(
                self,
                "Acesso negado",
                "O usuário atual não possui permissão para abrir a frente de caixa.",
            )
            return

        from core.caixa_session import CaixaSession
        from modules.venda.services.caixa_service import CaixaService
        from modules.venda.views.abrir_frente_caixa_dialog import AbrirFrenteCaixaDialog
        from modules.venda.views.venda_rapida_dialog import VendaRapidaDialog

        usuario = SessionManager.current_user() or {}
        parametros_venda = ConfiguracoesService.carregar_parametros_venda()
        venda_rapida_habilitada = bool(parametros_venda.get("habilitar_venda_rapida_admin", True))
        if not CaixaSession.has_open_caixa():
            CaixaService.restaurar_caixa_aberto(usuario.get("id"))

        if not CaixaSession.has_open_caixa():
            confirmar = confirmar_acao(
                self,
                "Abrir caixa",
                "Deseja abrir o caixa agora pelo painel administrativo?\n\n"
                "Depois da abertura, a Venda Rápida ficará disponível.",
            )
            if not confirmar:
                return
            dialog = AbrirFrenteCaixaDialog(self)
            if dialog.exec_() != dialog.Accepted:
                return
            self._atualizar_acao_caixa_dashboard()
            mostrar_info(
                self,
                "Caixa aberto",
                "Caixa aberto com sucesso.",
            )
            return

        if not venda_rapida_habilitada:
            mostrar_info(
                self,
                "Venda Rápida desabilitada",
                "A Venda Rápida está desabilitada em Configurações > Parâmetros de Venda.",
            )
            self._atualizar_acao_caixa_dashboard()
            return

        self.venda_rapida_dialog = VendaRapidaDialog(self)
        self.venda_rapida_dialog.exec_()
        self._load_dashboard_cards()

    def _open_fechamento_caixa_dashboard(self) -> None:
        from core.caixa_session import CaixaSession
        from modules.venda.views.fechar_caixa_dialog import FecharCaixaDialog

        if not CaixaSession.has_open_caixa():
            mostrar_aviso(
                self,
                "Caixa não encontrado",
                "Não há um caixa aberto no momento para encerrar pelo painel administrativo.",
            )
            self._atualizar_acao_caixa_dashboard()
            return

        self.fechar_caixa_dialog = FecharCaixaDialog(self)
        self.fechar_caixa_dialog.exec_()
        self._load_dashboard_cards()

    def _exit(self) -> None:
        from modules.auth.views.selecao_modo_view import SelecaoModoView

        self.hide()
        self.selecao = SelecaoModoView()
        self.selecao.show()

