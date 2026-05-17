from unittest.mock import patch

from modules.clientes.services.cliente_service import ClienteService


def test_atualizar_cliente_bloqueia_registro_de_sistema():
    with patch(
        "modules.clientes.services.cliente_service.ClienteModel.buscar_por_id",
        return_value={"id": 1, "nome": "Consumidor Final", "cliente_sistema": "S"},
    ), patch("modules.clientes.services.cliente_service.ClienteModel.atualizar") as mock_atualizar:
        sucesso, mensagem = ClienteService.atualizar_cliente(1, {"nome": "CONSUMIDOR FINAL"})

    assert sucesso is False
    assert "registro do sistema" in mensagem.lower()
    mock_atualizar.assert_not_called()


def test_alternar_status_bloqueia_registro_de_sistema():
    with patch(
        "modules.clientes.services.cliente_service.ClienteModel.buscar_por_id",
        return_value={"id": 1, "nome": "Consumidor Final", "cliente_sistema": "S", "ativo": "S"},
    ), patch("modules.clientes.services.cliente_service.ClienteModel.atualizar_status") as mock_status:
        sucesso, mensagem = ClienteService.alternar_status(1)

    assert sucesso is False
    assert "registro do sistema" in mensagem.lower()
    mock_status.assert_not_called()
