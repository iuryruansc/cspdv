from typing import Any, Dict, List

from PyQt5.QtCore import QDateTime, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QButtonGroup, QMainWindow, QMessageBox, QPushButton, QShortcut

from core.session_manager import SessionManager
from modules.admin.views.widgets import ManagementPageWidget
from ui.admin.painel_admin import Ui_PainelAdmin


class PainelAdminView(QMainWindow, Ui_PainelAdmin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._management_configs: Dict[str, Dict[str, Any]] = {}
        self._setup_user_context()
        self._setup_datetime()
        self._setup_management_area()
        self._setup_navigation()
        self._setup_actions()
        self._setup_shortcuts()
        self._show_dashboard()

    def _setup_user_context(self) -> None:
        usuario = SessionManager.current_user()
        if usuario:
            nome = usuario["nome"].upper()
            self.lblOperadorInfo.setText(f"Operador: {nome}")
            self.lblStatusBar.setText(f"CSPdv - Operador: {nome}  |  Painel Administrativo")
        else:
            self.lblOperadorInfo.setText("Operador: Nao logado")
            self.lblStatusBar.setText("CSPdv - Painel Administrativo")

    def _setup_datetime(self) -> None:
        self._update_datetime()
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_datetime)
        self.timer.start(1000)

    def _setup_management_area(self) -> None:
        self.managementPage = ManagementPageWidget(self.centralWidget)
        self.managementPage.hide()
        self.mainContentVLayout.addWidget(self.managementPage)

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

        for key, config in self._management_configs.items():
            button = config["button"]
            button.clicked.connect(lambda _, target=key: self._show_management_page(target))

    def _setup_actions(self) -> None:
        self.btnAcaoCadProduto.clicked.connect(self._open_cadastro_produto)
        self.btnAcaoBackup.clicked.connect(self._open_cadastro_marca)
        self.btnAcaoConfig.clicked.connect(self._open_cadastro_categoria)
        self.btnAcaoCadFornecedor.clicked.connect(self._open_cadastro_fornecedor)
        self.btnAcaoCadCliente.clicked.connect(self._open_cadastro_cliente)
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
        self.managementPage.hide()
        self.cardVendasHoje.show()
        self.cardFaturamento.show()
        self.cardProdutos.show()
        self.cardClientes.show()
        self.frameUltimasVendas.show()
        self._mark_subnav_button(None)

    def _show_management_page(self, key: str) -> None:
        config = self._management_configs[key]
        self._select_primary_nav(key)
        self.lblSectionTitle.setText(config["section_title"])
        self.btnFrenteCaixa.hide()
        self.cardVendasHoje.hide()
        self.cardFaturamento.hide()
        self.cardProdutos.hide()
        self.cardClientes.hide()
        self.frameUltimasVendas.hide()
        self.managementPage.show()
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
                f"Nao foi possivel consultar {config['title'].lower()} agora.\n\nDetalhes: {exc}"
            )
        self.managementPage.configure(
            title=config["title"],
            hint=config["hint"],
            columns=config["columns"],
            rows=rows,
        )
        self._current_management_key = key
        if error_message:
            QMessageBox.warning(self, "Falha ao carregar dados", error_message)

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

        self.hide()
        self.cadastro_produto = CadastroProdutoView(admin_view=self)
        self.cadastro_produto.show()

    def _open_cadastro_fornecedor(self) -> None:
        from modules.fornecedores.views.cadastro_fornecedor_view import CadastroFornecedorView

        self.hide()
        self.cadastro_fornecedor = CadastroFornecedorView(admin_view=self)
        self.cadastro_fornecedor.show()

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

        self.hide()
        self.cadastro_cliente = CadastroClienteView(admin_view=self)
        self.cadastro_cliente.show()

    def _open_ajuste_quantidade(self) -> None:
        if getattr(self, "_current_management_key", None) != "produtos":
            return

        produto = self.managementPage.selected_row()
        if not produto:
            QMessageBox.information(
                self,
                "Selecione um produto",
                "Escolha um produto na tabela antes de ajustar a quantidade.",
            )
            return

        from modules.produtos.views.ajuste_quantidade_dialog import AjusteQuantidadeDialog

        dialog = AjusteQuantidadeDialog(produto, self)
        if dialog.exec_():
            self._refresh_current_management_page()

    def _abrir_detalhes_produto(self) -> None:
        if getattr(self, "_current_management_key", None) != "produtos":
            return

        produto = self.managementPage.selected_row()
        if not produto:
            QMessageBox.information(
                self,
                "Selecione um produto",
                "Escolha um produto na tabela antes de visualizar os detalhes.",
            )
            return

        produto_id = produto.get("id")
        if produto_id is None:
            QMessageBox.warning(
                self,
                "Produto invalido",
                "Nao foi possivel identificar o produto selecionado.",
            )
            return

        from modules.produtos.models.produto_model import ProdutoModel
        from modules.produtos.views.detalhes_produto_dialog import DetalhesProdutoDialog

        detalhes = ProdutoModel.buscar_por_id(int(produto_id))
        if not detalhes:
            QMessageBox.warning(
                self,
                "Produto nao encontrado",
                "Nao foi possivel carregar os detalhes do produto selecionado.",
            )
            return

        dialog = DetalhesProdutoDialog(detalhes, self)
        dialog.exec_()

    def _toggle_registro_ativo(self) -> None:
        current_key = getattr(self, "_current_management_key", None)
        if current_key not in {"produtos", "marcas", "fornecedores", "categorias", "clientes"}:
            return

        row = self.managementPage.selected_row()
        if not row:
            QMessageBox.information(
                self,
                "Selecione um registro",
                "Escolha um registro na tabela antes de alterar o status.",
            )
            return

        if current_key == "produtos":
            entity_label = "produto"
            nome = str(row.get("nome") or "produto")
            entity_id = row.get("id")
            from modules.produtos.services.produto_service import ProdutoService

            service_call = ProdutoService.alternar_status
        elif current_key == "marcas":
            entity_label = "marca"
            nome = str(row.get("nome_marca") or "marca")
            entity_id = row.get("id")
            from modules.marcas.services.marca_service import MarcaService

            service_call = MarcaService.alternar_status
        elif current_key == "categorias":
            entity_label = "categoria"
            nome = str(row.get("nome") or "categoria")
            entity_id = row.get("id")
            from modules.categorias.services.categoria_service import CategoriaService

            service_call = CategoriaService.alternar_status
        elif current_key == "fornecedores":
            entity_label = "fornecedor"
            nome = str(row.get("nome_fantasia") or "fornecedor")
            entity_id = row.get("id_fornecedor")
            from modules.fornecedores.services.fornecedor_service import FornecedorService

            service_call = FornecedorService.alternar_status
        else:
            entity_label = "cliente"
            nome = str(row.get("nome") or "cliente")
            entity_id = row.get("id")
            from modules.clientes.services.cliente_service import ClienteService

            service_call = ClienteService.alternar_status

        if entity_id is None:
            QMessageBox.warning(self, "Registro invalido", "Nao foi possivel identificar o registro selecionado.")
            return

        ativo_atual = str(row.get("ativo") or "N").strip().upper()
        acao = "desativar" if ativo_atual == "S" else "ativar"
        confirmacao = QMessageBox.question(
            self,
            "Confirmar alteracao",
            f"Deseja {acao} o {entity_label} '{nome}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmacao != QMessageBox.Yes:
            return

        sucesso, mensagem = service_call(entity_id)
        if not sucesso:
            QMessageBox.warning(self, "Status nao alterado", mensagem)
            return

        QMessageBox.information(self, "Status atualizado", mensagem)
        self._refresh_current_management_page()

    def _editar_registro(self) -> None:
        current_key = getattr(self, "_current_management_key", None)
        if current_key not in {"produtos", "marcas", "fornecedores", "categorias", "clientes"}:
            return

        row = self.managementPage.selected_row()
        if not row:
            QMessageBox.information(
                self,
                "Selecione um registro",
                "Escolha um registro na tabela antes de editar.",
            )
            return

        if current_key == "produtos":
            registro_id = row.get("id")
            if registro_id is None:
                QMessageBox.warning(self, "Produto invalido", "Nao foi possivel identificar o produto selecionado para edicao.")
                return
            from modules.produtos.views.cadastro_produto_view import CadastroProdutoView

            self.hide()
            self.cadastro_produto = CadastroProdutoView(produto_id=int(registro_id), admin_view=self)
            self.cadastro_produto.show()
            return

        if current_key == "marcas":
            registro_id = row.get("id")
            if registro_id is None:
                QMessageBox.warning(self, "Marca invalida", "Nao foi possivel identificar a marca selecionada.")
                return
            from modules.marcas.views.cadastro_marca_view import CadastroMarcaView

            dialog = CadastroMarcaView(self, marca_id=int(registro_id))
            if dialog.exec_():
                self._refresh_current_management_page()
            return

        if current_key == "categorias":
            registro_id = row.get("id")
            if registro_id is None:
                QMessageBox.warning(self, "Categoria invalida", "Nao foi possivel identificar a categoria selecionada.")
                return
            from modules.categorias.views.cadastro_categoria_view import CadastroCategoriaView

            dialog = CadastroCategoriaView(self, categoria_id=int(registro_id))
            if dialog.exec_():
                self._refresh_current_management_page()
            return

        if current_key == "clientes":
            registro_id = row.get("id")
            if registro_id is None:
                QMessageBox.warning(self, "Cliente invalido", "Nao foi possivel identificar o cliente selecionado.")
                return
            from modules.clientes.views.cadastro_cliente_view import CadastroClienteView

            self.hide()
            self.cadastro_cliente = CadastroClienteView(cliente_id=int(registro_id), admin_view=self)
            self.cadastro_cliente.show()
            return

        registro_id = row.get("id_fornecedor")
        if registro_id is None:
            QMessageBox.warning(self, "Fornecedor invalido", "Nao foi possivel identificar o fornecedor selecionado.")
            return
        from modules.fornecedores.views.cadastro_fornecedor_view import CadastroFornecedorView

        self.hide()
        self.cadastro_fornecedor = CadastroFornecedorView(fornecedor_id=int(registro_id), admin_view=self)
        self.cadastro_fornecedor.show()

    def _update_datetime(self) -> None:
        current = QDateTime.currentDateTime()
        self.lblDataHora.setText(current.toString("dd/MM/yyyy  hh:mm:ss"))

    def _exit(self) -> None:
        from modules.auth.views.selecao_modo_view import SelecaoModoView

        self.hide()
        self.selecao = SelecaoModoView()
        self.selecao.show()
