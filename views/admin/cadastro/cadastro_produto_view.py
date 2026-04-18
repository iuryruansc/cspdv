from ui.admin.cadastros.cadastro_produto import Ui_CadastroProduto
from PyQt5.QtWidgets import QMessageBox, QWidget, QLineEdit, QComboBox
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtCore import QTimer
from services.produto_service import ProdutoService
from models.categoria_model import CategoriaModel

class CadastroProdutoView(QWidget, Ui_CadastroProduto):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Validador para campos de preço (números decimais)
        validador_moeda = QDoubleValidator(0.00, 999999.99, 2, self)
        validador_moeda.setNotation(QDoubleValidator.StandardNotation)
        self.lineEditPrecoCusto.setValidator(validador_moeda)
        self.lineEditPrecoVenda.setValidator(validador_moeda)

        # Validador para quantidade de estoque (números inteiros)
        validador_inteiro = QIntValidator(0, 999999, self)
        self.lineEditQuantidadeEstoque.setValidator(validador_inteiro)

        # Limite de caracteres para campos de texto
        self.lineEditCodigoBarras.setMaxLength(50)
        self.lineEditDescricao.setMaxLength(250)
        self.lineEditNcm.setMaxLength(8)
        self.lineEditCest.setMaxLength(7)

        # Conectar sinais para calcular margem de lucro
        self.lineEditPrecoCusto.textChanged.connect(self._calcular_margem)
        self.lineEditPrecoVenda.textChanged.connect(self._calcular_margem)

        # Conectar sinal para escanear produto
        self.lineEditCodigoBarras.returnPressed.connect(self._scan_produto)

        self.lineEditMargem.setReadOnly(True)

        self.btnVoltar.clicked.connect(self._cancelar)
        self.btnSalvar.clicked.connect(self._salvar_produto)
        self.btnLimpar.clicked.connect(self._limpar_campos)

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


    def _feedback_sucesso(self):
        self.lineEditCodigoBarras.setStyleSheet("""
            QLineEdit {
                border: 2px solid #2ecc71; 
                background-color: #0d2a1d;
            }
        """)
        QTimer.singleShot(500, lambda: self.lineEditCodigoBarras.setStyleSheet(""))

    def _feedback_erro(self):
        self.lineEditCodigoBarras.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e74c3c; 
                background-color: #2d0a0a;
            }
        """)
        QTimer.singleShot(500, lambda: self.lineEditCodigoBarras.setStyleSheet(""))

    def _limpar_campos(self):
        for campo_texto in self.findChildren(QLineEdit):
            if campo_texto.objectName() != "lineEditCodigo":
                campo_texto.clear()

        for combo in self.findChildren(QComboBox):
            combo.setCurrentIndex(0)

        self.lineEditCodigoBarras.setFocus()

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

    def _salvar_produto(self):
        try:
            dados = {
                'codigo_barras': self.lineEditCodigoBarras.text().strip(),
                'descricao': self.lineEditDescricao.text().strip().upper(),
                'ncm': self.lineEditNcm.text().strip(),
                'cest': self.lineEditCest.text().strip(),
                'preco_custo': float(self.lineEditPrecoCusto.text().replace(',', '.') or 0),
                'preco_venda': float(self.lineEditPrecoVenda.text().replace(',', '.') or 0),
                'estoque': float(self.lineEditQuantidadeEstoque.text().replace(',', '.') or 0),
                # Pegamos o ID guardado no combo (supondo que você carregou IDs neles)
                'id_categoria': self.comboCategoria.currentData(), 
                'id_unidade': self.comboUnidade.currentData()
            }
        except ValueError:
            return
        
        sucesso, mensagem = ProdutoService.cadastrar_produto(dados)

        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self._limpar_campos()
        else:
            QMessageBox.warning(self, "Atenção", mensagem)

    def _cancelar(self):
        from views.admin.painel_admin_view import PainelAdminView
        self.close()
        self.painel_admin = PainelAdminView()
        self.painel_admin.show()