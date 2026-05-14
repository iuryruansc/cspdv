import sys
from datetime import datetime
from unittest.mock import patch

from PyQt5.QtWidgets import QApplication

from modules.financeiro.views.comprovante_recebimento_dialog import ComprovanteRecebimentoDialog

_app = QApplication.instance() or QApplication(sys.argv)

def _conta_base(**overrides):
    conta = {
        "id": 12,
        "venda_id": 45,
        "cliente": "Iury Santos",
        "observacao": "Pagamento parcial da venda",
        "status": "PARCIALMENTE_RECEBIDA",
    }
    conta.update(overrides)
    return conta

def _recebimento_base(**overrides):
    recebimento = {
        "conta_id": 12,
        "venda_id": 45,
        "forma_pagamento": "Dinheiro",
        "valor_recebido": 25.50,
        "valor_aberto": 10.00,
        "status": "PARCIALMENTE_RECEBIDA",
        "data_recebimento": datetime(2026, 5, 12, 10, 45),
    }
    recebimento.update(overrides)
    return recebimento

class TestComprovanteRecebimentoDialog:
    def test_monta_texto_com_dados_principais(self):
        dialog = ComprovanteRecebimentoDialog(
            conta=_conta_base(),
            recebimento=_recebimento_base(),
            operador_nome="Iury",
            caixa_label="PDV-01 - Caixa Principal",
        )

        texto = dialog.textComprovante.toPlainText()

        assert "COMPROVANTE DE RECEBIMENTO" in texto
        assert "12/05/2026 10:45" in texto
        assert "Operador  : Iury" in texto
        assert "Caixa     : PDV-01 - Caixa Principal" in texto
        assert "Conta     : #12" in texto
        assert "Venda     : #45" in texto
        assert "Cliente   : Iury Santos" in texto
        assert "Forma     : Dinheiro" in texto
        assert "Recebido  :" in texto and "25,50" in texto
        assert "Saldo     :" in texto and "10,00" in texto

    @patch("modules.financeiro.views.comprovante_recebimento_dialog.mostrar_info")
    def test_copiar_comprovante_envia_texto_para_area_de_transferencia(self, mock_info):
        dialog = ComprovanteRecebimentoDialog(
            conta=_conta_base(),
            recebimento=_recebimento_base(),
            operador_nome="Iury",
            caixa_label="PDV-01 - Caixa Principal",
        )

        dialog._copiar_comprovante()

        clipboard_text = QApplication.clipboard().text()
        assert "COMPROVANTE DE RECEBIMENTO" in clipboard_text
        assert "Conta     : #12" in clipboard_text
        mock_info.assert_called_once()
