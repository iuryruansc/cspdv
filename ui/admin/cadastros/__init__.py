"""Subpacote de cadastros da camada de UI administrativa."""
from .cadastro_categoria import Ui_CadastroCategoria
from .cadastro_fornecedor import Ui_CadastroFornecedor
from .cadastro_lote import Ui_CadastroLote
from .cadastro_marca import Ui_CadastroMarca
from .cadastro_produto import Ui_CadastroProduto

__all__ = [
    "Ui_CadastroCategoria",
    "Ui_CadastroFornecedor",
    "Ui_CadastroLote",
    "Ui_CadastroMarca",
    "Ui_CadastroProduto",
]
