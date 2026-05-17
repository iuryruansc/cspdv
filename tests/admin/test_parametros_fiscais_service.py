from unittest.mock import patch

from modules.admin.services.configuracoes_service import ConfiguracoesService


def test_salvar_parametros_fiscais_bloqueia_cfop_invalido():
    sucesso, mensagem = ConfiguracoesService.salvar_parametros_fiscais(
        regime_tributario_label="Simples Nacional",
        origem_mercadoria_label="0 - Nacional",
        cfop_venda_padrao="51A2",
        cfop_devolucao_padrao="1202",
        csosn_cst_padrao="102",
        natureza_operacao_padrao="VENDA DE MERCADORIA",
        exigir_ncm_cest_produto=True,
        exigir_unidade_tributavel_produto=True,
    )

    assert sucesso is False
    assert "cfop padrão de venda" in mensagem.lower()


@patch("modules.admin.services.configuracoes_service.ConfiguracoesModel.salvar_parametros_fiscais")
def test_salvar_parametros_fiscais_normaliza_e_persiste(mock_salvar):
    sucesso, mensagem = ConfiguracoesService.salvar_parametros_fiscais(
        regime_tributario_label="Simples Nacional",
        origem_mercadoria_label="0 - Nacional",
        cfop_venda_padrao="5102",
        cfop_devolucao_padrao="1202",
        csosn_cst_padrao="102",
        natureza_operacao_padrao="Venda de mercadoria",
        exigir_ncm_cest_produto=False,
        exigir_unidade_tributavel_produto=False,
    )

    assert sucesso is True
    assert "sucesso" in mensagem.lower()
    mock_salvar.assert_called_once_with(
        regime_tributario_padrao="SIMPLES_NACIONAL",
        origem_mercadoria_padrao="0",
        cfop_venda_padrao="5102",
        cfop_devolucao_padrao="1202",
        csosn_cst_padrao="102",
        natureza_operacao_padrao="VENDA DE MERCADORIA",
        exigir_ncm_cest_produto=False,
        exigir_unidade_tributavel_produto=False,
    )
