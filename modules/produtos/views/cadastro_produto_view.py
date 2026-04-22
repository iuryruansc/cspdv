from pathlib import Path
import shutil
import uuid

from PyQt5.QtCore import QRegularExpression, QTimer, Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QPixmap, QRegularExpressionValidator
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget, QLineEdit, QComboBox

from modules.shared.models.combo_models import (
    CategoriaModel,
    FornecedorModel,
    MarcaModel,
    UnidadeModel,
)
from modules.produtos.services.produto_service import ProdutoService
from ui.admin.cadastros.cadastro_produto import Ui_CadastroProduto
from utils.combo_loader import popular_combo, combo_id
from utils.form_validation_mixin import ValidacaoFormMixin

class CadastroProdutoView(QWidget, Ui_CadastroProduto, ValidacaoFormMixin):
    MEDIA_PRODUTOS_DIR = Path(__file__).resolve().parents[3] / "media" / "produtos"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._imagem_produto_path = None

        self._configurar_validadores()
        self.registrar_estilos([
            self.lineEditCodigoBarras,
            self.lineEditDescricao,
            self.lineEditNcm,
            self.lineEditCest,
            self.lineEditPrecoCusto,
            self.lineEditPrecoVenda,
            self.lineEditQuantidadeEstoque,
            self.comboCategoria,
            self.comboMarca,
            self.comboBox,
            self.comboUnidade,
            self.comboUnidadeTributavel,
        ])
        self.conectar_limpeza_em_tempo_real()

        self.lineEditMargem.setReadOnly(True)
        self.lineEditPrecoCusto.textChanged.connect(self._calcular_margem)
        self.lineEditPrecoVenda.textChanged.connect(self._calcular_margem)
        self.lineEditCodigoBarras.returnPressed.connect(self._scan_produto)

        self.btnVoltar.clicked.connect(self._cancelar)
        self.btnSalvar.clicked.connect(self._salvar_produto)
        self.btnLimpar.clicked.connect(self._limpar_campos)
        self.btnSelecionarImagem.clicked.connect(self._selecionar_imagem)
        self.btnRemoverImagem.clicked.connect(self._remover_imagem)

        self._popular_combos()
        self._atualizar_preview_imagem()

    def _configurar_validadores(self):
        validador_moeda = QDoubleValidator(0.00, 999999.99, 2, self)
        validador_moeda.setNotation(QDoubleValidator.StandardNotation)
        self.lineEditPrecoCusto.setValidator(validador_moeda)
        self.lineEditPrecoVenda.setValidator(validador_moeda)

        self.lineEditQuantidadeEstoque.setValidator(QIntValidator(0, 999999, self))

        self.lineEditCodigoBarras.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^[0-9A-Za-z\-]{0,50}$"), self)
        )
        self.lineEditNcm.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^\d{0,8}$"), self)
        )
        self.lineEditCest.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^\d{0,7}$"), self)
        )

        self.lineEditCodigoBarras.setMaxLength(50)
        self.lineEditDescricao.setMaxLength(250)
        self.lineEditNcm.setMaxLength(8)
        self.lineEditCest.setMaxLength(7)

    def _popular_combos(self):
        try:
            popular_combo(self.comboCategoria, CategoriaModel.listar_ativas())
            popular_combo(self.comboMarca, MarcaModel.listar_ativas())
            popular_combo(self.comboBox, FornecedorModel.listar_ativos())
            popular_combo(self.comboUnidade, UnidadeModel.listar_ativas())
            popular_combo(
                self.comboUnidadeTributavel,
                UnidadeModel.listar_ativas(),
                placeholder="Igual a comercial",
            )
        except Exception as e:
            QMessageBox.warning(self, "Atencao", f"Nao foi possivel carregar os dados dos combos:\n{e}")

    def _scan_produto(self):
        codigo = self.lineEditCodigoBarras.text().strip()
        if not codigo:
            return

        produto, mensagem, sucesso = ProdutoService.validar_e_buscar_por_codigo(codigo)
        if sucesso:
            self._feedback_erro()
            self.lineEditCodigoBarras.clear()
            self.lineEditCodigoBarras.setFocus()
        elif "nao localizado" in mensagem.lower():
            self._feedback_sucesso()
            self.lineEditDescricao.setFocus()

    def _feedback_sucesso(self):
        self.lineEditCodigoBarras.setStyleSheet(
            "QLineEdit { border: 2px solid #2ecc71; background-color: #edf9f0; }"
        )
        QTimer.singleShot(500, lambda: self.limpar_erro_widget(self.lineEditCodigoBarras))

    def _feedback_erro(self):
        self.lineEditCodigoBarras.setStyleSheet(
            "QLineEdit { border: 2px solid #e74c3c; background-color: #fff2f2; }"
        )
        QTimer.singleShot(500, lambda: self.limpar_erro_widget(self.lineEditCodigoBarras))

    def _limpar_campos(self):
        self.limpar_erros()

        for campo_texto in self.findChildren(QLineEdit):
            if campo_texto.objectName() != "lineEditCodigo":
                campo_texto.clear()

        for combo in self.findChildren(QComboBox):
            combo.setCurrentIndex(0)

        self.checkBoxAtivo.setChecked(True)
        self._imagem_produto_path = None
        self._atualizar_preview_imagem()
        self.lineEditCodigoBarras.setFocus()

    def _selecionar_imagem(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecionar imagem do produto", "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.webp)",
        )
        if not caminho:
            return
        self._imagem_produto_path = caminho
        self._atualizar_preview_imagem()

    def _remover_imagem(self):
        self._imagem_produto_path = None
        self._atualizar_preview_imagem()

    def _atualizar_preview_imagem(self):
        self.lineEditImagemProduto.setText(self._imagem_produto_path or "")

        if not self._imagem_produto_path:
            self.lblPreviewImagem.setText("Nenhuma imagem selecionada")
            self.lblPreviewImagem.setPixmap(QPixmap())
            return

        pixmap = QPixmap(self._imagem_produto_path)
        if pixmap.isNull():
            self.lblPreviewImagem.setText("Nao foi possivel carregar a imagem")
            self.lblPreviewImagem.setPixmap(QPixmap())
            return

        self.lblPreviewImagem.setText("")
        self.lblPreviewImagem.setPixmap(
            pixmap.scaled(self.lblPreviewImagem.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def _copiar_imagem_para_media(self):
        if not self._imagem_produto_path:
            return None

        origem = Path(self._imagem_produto_path)
        if not origem.exists():
            raise FileNotFoundError("A imagem selecionada nao foi encontrada.")

        self.MEDIA_PRODUTOS_DIR.mkdir(parents=True, exist_ok=True)
        extensao = origem.suffix.lower() or ".png"
        nome_arquivo = f"{uuid.uuid4().hex}{extensao}"
        destino = self.MEDIA_PRODUTOS_DIR / nome_arquivo
        shutil.copy2(origem, destino)
        return str(Path("media") / "produtos" / nome_arquivo)

    def _calcular_margem(self):
        try:
            custo = float(self.lineEditPrecoCusto.text().replace(",", ".") or 0)
            venda = float(self.lineEditPrecoVenda.text().replace(",", ".") or 0)
            margem = ((venda - custo) / venda * 100) if venda > 0 else 0.0
            self.lineEditMargem.setText(f"{margem:.2f}")
        except ValueError:
            self.lineEditMargem.setText("0.00")

    def _salvar_produto(self):
        self.limpar_erros()

        id_categoria = combo_id(self.comboCategoria)
        id_marca = combo_id(self.comboMarca)
        id_fornecedor = combo_id(self.comboBox)
        id_unidade = combo_id(self.comboUnidade)
        id_unidade_tributavel = combo_id(self.comboUnidadeTributavel)

        codigo_barras = self.lineEditCodigoBarras.text().strip()
        nome = self.lineEditDescricao.text().strip().upper()
        ncm = self.lineEditNcm.text().strip()
        cest = self.lineEditCest.text().strip()
        preco_custo_texto = self.lineEditPrecoCusto.text().replace(",", ".")
        preco_venda_texto = self.lineEditPrecoVenda.text().replace(",", ".")
        quantidade_texto = self.lineEditQuantidadeEstoque.text().replace(",", ".")

        erros = []
        if not nome:
            erros.append("Descricao do Produto: preencha o nome do produto.")
            self.marcar_invalido(self.lineEditDescricao)
        if not codigo_barras:
            erros.append("Codigo de Barras: preencha um codigo de barras.")
            self.marcar_invalido(self.lineEditCodigoBarras)
        if id_categoria is None:
            erros.append("Categoria: selecione uma categoria.")
            self.marcar_invalido(self.comboCategoria)
        if id_marca is None:
            erros.append("Marca: selecione uma marca.")
            self.marcar_invalido(self.comboMarca)
        if id_fornecedor is None:
            erros.append("Fornecedor: selecione um fornecedor.")
            self.marcar_invalido(self.comboBox)
        if id_unidade is None:
            erros.append("Unidade Comercial: selecione uma unidade.")
            self.marcar_invalido(self.comboUnidade)
        if id_unidade_tributavel is None:
            erros.append("Unidade Tributavel: selecione uma unidade tributavel.")
            self.marcar_invalido(self.comboUnidadeTributavel)
        if ncm and len(ncm) != 8:
            erros.append("NCM: informe os 8 digitos do codigo fiscal.")
            self.marcar_invalido(self.lineEditNcm)
        if cest and len(cest) != 7:
            erros.append("CEST: informe os 7 digitos do codigo.")
            self.marcar_invalido(self.lineEditCest)
        if codigo_barras and len(codigo_barras) < 8:
            erros.append("Codigo de Barras: use ao menos 8 caracteres.")
            self.marcar_invalido(self.lineEditCodigoBarras)
        if not preco_venda_texto:
            erros.append("Preco de Venda: informe um valor maior que zero.")
            self.marcar_invalido(self.lineEditPrecoVenda)

        if erros:
            QMessageBox.warning(self, "Revise os campos", "Corrija os seguintes pontos:\n" + "\n".join(erros))
            return

        try:
            imagem_path = self._copiar_imagem_para_media()
            dados = {
                "codigo_barras": codigo_barras,
                "nome": nome,
                "ncm": ncm,
                "cest": cest,
                "preco_compra": float(preco_custo_texto or 0),
                "preco_venda": float(preco_venda_texto or 0),
                "quantidade_estoque": float(quantidade_texto or 0),
                "categoria_id": id_categoria,
                "marca_id": id_marca,
                "fornecedor_id": id_fornecedor,
                "unidade_id": id_unidade,
                "unidade_tributavel_id": id_unidade_tributavel,
                "ativo": "S" if self.checkBoxAtivo.isChecked() else "N",
                "imagem_path": imagem_path,
            }
        except FileNotFoundError as e:
            QMessageBox.warning(self, "Imagem invalida", str(e))
            return
        except OSError as e:
            QMessageBox.warning(self, "Erro ao copiar imagem", f"Nao foi possivel salvar a imagem:\n{e}")
            return
        except ValueError:
            QMessageBox.warning(self, "Valores invalidos", "Revise preco de custo, preco de venda e estoque inicial.")
            return

        sucesso, mensagem = ProdutoService.cadastrar_produto(dados)
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self._limpar_campos()
        else:
            if "nome do produto" in mensagem.lower():
                self.marcar_invalido(self.lineEditDescricao)
            if "preco de venda" in mensagem.lower():
                self.marcar_invalido(self.lineEditPrecoVenda)
            if "codigo de barras" in mensagem.lower() or "codigo do produto" in mensagem.lower():
                self.marcar_invalido(self.lineEditCodigoBarras)
            if "categoria" in mensagem.lower():
                self.marcar_invalido(self.comboCategoria)
            if "marca" in mensagem.lower():
                self.marcar_invalido(self.comboMarca)
            if "fornecedor" in mensagem.lower():
                self.marcar_invalido(self.comboBox)
            QMessageBox.warning(self, "Atencao", mensagem)

    def _cancelar(self):
        from modules.admin.views.painel_admin_view import PainelAdminView

        self.close()
        self.painel_admin = PainelAdminView()
        self.painel_admin.show()

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if self._imagem_produto_path:
            self._atualizar_preview_imagem()
