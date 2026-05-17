from unittest.mock import patch

from modules.formas_pagamento.services.forma_pagamento_service import FormaPagamentoService


def test_cadastrar_forma_pagamento_bloqueia_nome_curto():
    sucesso, mensagem = FormaPagamentoService.cadastrar_forma_pagamento(
        {
            "nome": "A",
            "tipo_sefaz": "01",
            "permite_parcelamento": "N",
            "taxa_administrativa": 0,
            "ativo": "S",
        }
    )

    assert sucesso is False
    assert "pelo menos 2 caracteres" in mensagem


def test_cadastrar_forma_pagamento_bloqueia_tipo_sefaz_vazio():
    sucesso, mensagem = FormaPagamentoService.cadastrar_forma_pagamento(
        {
            "nome": "PIX",
            "tipo_sefaz": "",
            "permite_parcelamento": "N",
            "taxa_administrativa": 0,
            "ativo": "S",
        }
    )

    assert sucesso is False
    assert "tipo sefaz" in mensagem.lower()


@patch("modules.formas_pagamento.services.forma_pagamento_service.FormaPagamentoModel.inserir", return_value=5)
@patch("modules.formas_pagamento.services.forma_pagamento_service.FormaPagamentoModel.buscar_por_nome", return_value=None)
def test_cadastrar_forma_pagamento_valida_e_insere(_mock_buscar_por_nome, mock_inserir):
    sucesso, mensagem = FormaPagamentoService.cadastrar_forma_pagamento(
        {
            "nome": "Cartao Debito",
            "tipo_sefaz": "04",
            "permite_parcelamento": "N",
            "taxa_administrativa": 1.5,
            "ativo": "S",
        }
    )

    assert sucesso is True
    assert "sucesso" in mensagem.lower()
    mock_inserir.assert_called_once()


@patch("modules.formas_pagamento.services.forma_pagamento_service.FormaPagamentoModel.buscar_por_id")
@patch("modules.formas_pagamento.services.forma_pagamento_service.FormaPagamentoModel.atualizar_status", return_value=True)
def test_alternar_status_forma_pagamento(mock_atualizar_status, mock_buscar_por_id):
    mock_buscar_por_id.return_value = {"id": 7, "nome": "PIX", "ativo": "S"}

    sucesso, mensagem = FormaPagamentoService.alternar_status(7)

    assert sucesso is True
    assert "desativada" in mensagem.lower()
    mock_atualizar_status.assert_called_once_with(7, "N")
