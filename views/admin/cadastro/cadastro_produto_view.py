from ui.admin.cadastros.cadastro_produto import Ui_CadastroProduto
from PyQt5.QtWidgets import QMessageBox, QWidget, QLineEdit, QComboBox
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtCore import QTimer

from services.produto_service import ProdutoService
from models.combo_models import CategoriaModel, MarcaModel, FornecedorModel, UnidadeModel
from utils.combo_loader import popular_combo, combo_id

class CadastroProdutoView(QWidget, Ui_CadastroProduto):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Validadores
        validador_moeda = QDoubleValidator(0.00, 999999.99, 2, self)
        validador_moeda.setNotation(QDoubleValidator.StandardNotation)
        self.lineEditPrecoCusto.setValidator(validador_moeda)
        self.lineEditPrecoVenda.setValidator(validador_moeda)
        validador_inteiro = QIntValidator(0, 999999, self)
        self.lineEditQuantidadeEstoque.setValidator(validador_inteiro)

        # Limite de caracteres
        self.lineEditCodigoBarras.setMaxLength(50)
        self.lineEditDescricao.setMaxLength(250)
        self.lineEditNcm.setMaxLength(8)
        self.lineEditCest.setMaxLength(7)

        # Cálculo da margem de lucro automaticamente
        self.lineEditMargem.setReadOnly(True)
        self.lineEditPrecoCusto.textChanged.connect(self._calcular_margem)
        self.lineEditPrecoVenda.textChanged.connect(self._calcular_margem)

        # Scan por código de barras
        self.lineEditCodigoBarras.returnPressed.connect(self._scan_produto)

        # Botões
        self.btnVoltar.clicked.connect(self._cancelar)
        self.btnSalvar.clicked.connect(self._salvar_produto)
        self.btnLimpar.clicked.connect(self._limpar_campos)

        # Popular combos com dados do banco
        self._popular_combos()

    # Método para popular os combos
    def _popular_combos(self):
        try:
            popular_combo(self.comboCategoria, CategoriaModel.listar_ativas())
            popular_combo(self.comboMarca, MarcaModel.listar_ativas())
            popular_combo(self.comboBox, FornecedorModel.listar_ativos())
            popular_combo(self.comboUnidade, UnidadeModel.listar_ativas())
            popular_combo(self.comboUnidadeTributavel, UnidadeModel.listar_ativas(), 
                          placeholder='Igual à comercial')
        except Exception as e:
            QMessageBox.warning(self, 'Atenção', f'Não foi possível carregar os dados dos combos:\n{e}')
 

    # Método para escanear o código de barras
    def _scan_produto(self):
        codigo = self.lineEditCodigoBarras.text().strip()
        
        if not codigo:
            return
        
        produto, mensagem, sucesso = ProdutoService.validar_e_buscar_por_codigo(codigo)

        if sucesso:
            self._feedback_erro()
            self.lineEditCodigoBarras.clear()
            self.lineEditCodigoBarras.setFocus()
        else:
            if "não localizado" in mensagem:
                self._feedback_sucesso()
                self.lineEditDescricao.setFocus()

    # Método de retorno visual em caso de sucesso no scan
    def _feedback_sucesso(self):
        self.lineEditCodigoBarras.setStyleSheet("""
            QLineEdit {
                border: 2px solid #2ecc71; 
                background-color: #0d2a1d;
            }
        """)
        QTimer.singleShot(500, lambda: self.lineEditCodigoBarras.setStyleSheet(""))

    # Método de retorno visual em caso de erro no scan
    def _feedback_erro(self):
        self.lineEditCodigoBarras.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e74c3c; 
                background-color: #2d0a0a;
            }
        """)
        QTimer.singleShot(500, lambda: self.lineEditCodigoBarras.setStyleSheet(""))

    # Método para limpar os campos do formulário
    def _limpar_campos(self):
        for campo_texto in self.findChildren(QLineEdit):
            if campo_texto.objectName() != "lineEditCodigo":
                campo_texto.clear()

        for combo in self.findChildren(QComboBox):
            combo.setCurrentIndex(0)

        self.checkBoxAtivo.setChecked(True)
        self.lineEditCodigoBarras.setFocus()

    # Método para calcular a margem de lucro automaticamente
    def _calcular_margem(self):
        try:
            custo_texto = self.lineEditPrecoCusto.text().replace(',', '.')
            venda_texto = self.lineEditPrecoVenda.text().replace(',', '.')

            custo = float(custo_texto) if custo_texto else 0.0
            venda = float(venda_texto) if venda_texto else 0.0

            if venda > 0:
                margem = ((venda - custo) / venda) * 100
                self.lineEditMargem.setText(f"{margem:.2f}")
            else:
                self.lineEditMargem.setText("0.00")

        except ValueError:
            self.lineEditMargem.setText("0.00")

    # Método para salvar o produto no banco de dados
    def _salvar_produto(self):
        id_categoria          = combo_id(self.comboCategoria)
        id_marca              = combo_id(self.comboMarca)
        id_fornecedor         = combo_id(self.comboBox)
        id_unidade            = combo_id(self.comboUnidade)
        id_unidade_tributavel = combo_id(self.comboUnidadeTributavel)
        
        erros = []
        if id_categoria is None:
            erros.append('• Categoria')
        if id_marca is None:
            erros.append('• Marca')
        if id_fornecedor is None:
            erros.append('• Fornecedor')
        if id_unidade is None:
            erros.append('• Unidade Comercial')
        if id_unidade_tributavel is None:
            erros.append('• Unidade Tributável')
 
        if erros:
            QMessageBox.warning(
                self, 'Campos obrigatórios',
                'Selecione os seguintes campos:\n' + '\n'.join(erros)
            )
            return
        
        try:
            dados = {
                'codigo_barras': self.lineEditCodigoBarras.text().strip(),
                'nome': self.lineEditDescricao.text().strip().upper(),
                'ncm': self.lineEditNcm.text().strip(),
                'cest': self.lineEditCest.text().strip(),
                'preco_compra': float(self.lineEditPrecoCusto.text().replace(',', '.') or 0),
                'preco_venda': float(self.lineEditPrecoVenda.text().replace(',', '.') or 0),
                'quantidade_estoque': float(self.lineEditQuantidadeEstoque.text().replace(',', '.') or 0),
                'categoria_id': id_categoria,
                'marca_id': id_marca,
                'fornecedor_id': id_fornecedor,
                'unidade_id': id_unidade,
                'unidade_tributavel_id': id_unidade_tributavel,
                'ativo': 'S' if self.checkBoxAtivo.isChecked() else 'N'

            }
        except ValueError:
            return
        
        sucesso, mensagem = ProdutoService.cadastrar_produto(dados)

        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self._limpar_campos()
        else:
            QMessageBox.warning(self, "Atenção", mensagem)

    # Método para cancelar e voltar ao painel admin
    def _cancelar(self):
        from views.admin.painel_admin_view import PainelAdminView
        self.close()
        self.painel_admin = PainelAdminView()
        self.painel_admin.show()