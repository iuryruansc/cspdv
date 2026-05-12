import sys

from PyQt5.QtWidgets import QApplication

from modules.venda.views.pos_pagamento_dialog import PosPagamentoDialog

_app = QApplication.instance() or QApplication(sys.argv)


def _venda_base(**overrides):
    venda = {
        "numero_venda": "V-1001",
        "data_hora_venda": "11/05/2026 21:45:10",
        "cliente_nome": "Consumidor Final",
        "subtotal": 18.0,
        "desconto_total": 2.0,
        "total": 16.0,
        "troco": 4.0,
        "valor_em_aberto": 0.0,
        "status": "CONCLUIDA",
        "itens": [
            {"nome": "Refrigerante Zero 2L", "quantidade": 2, "total": 12.0},
            {"nome": "Agua sem Gas", "quantidade": 1, "total": 6.0},
        ],
        "pagamentos": [
            {"forma": "Dinheiro", "valor": 20.0},
        ],
    }
    venda.update(overrides)
    return venda


class TestPosPagamentoDialog:
    def test_monta_cupom_com_itens_pagamento_e_totais(self):
        dialog = PosPagamentoDialog(venda_data=_venda_base())

        texto = dialog.textCupom.toPlainText()

        assert "DOCUMENTO NÃO FISCAL" in texto
        assert "COMPROVANTE DE VENDA" in texto
        assert "Refrigerante Zero 2L" in texto
        assert "Agua sem Gas" in texto
        assert "Subtotal:" in texto
        assert "Desconto:" in texto
        assert "Total:" in texto
        assert "PAGAMENTOS" in texto
        assert "Dinheiro" in texto
        assert "Troco:" in texto
        assert "Obrigado pela preferência." in texto

    def test_mantem_vencimento_original_quando_ja_esta_formatado(self):
        dialog = PosPagamentoDialog(
            venda_data=_venda_base(
                valor_em_aberto=5.5,
                data_vencimento="20/05/2026",
                status="CONCLUIDA_COM_PENDENCIA",
            )
        )

        texto = dialog.textCupom.toPlainText()

        assert "Em aberto:" in texto
        assert "Vencimento: 20/05/2026" in texto
        assert "Status: CONCLUIDA COM PENDENCIA" in texto

    def test_converte_vencimento_iso_para_formato_brasileiro(self):
        dialog = PosPagamentoDialog(
            venda_data=_venda_base(
                valor_em_aberto=5.5,
                data_vencimento="2026-05-20",
                status="CONCLUIDA_COM_PENDENCIA",
            )
        )

        texto = dialog.textCupom.toPlainText()

        assert "Vencimento: 20/05/2026" in texto

    def test_acoes_atualizam_resultado(self):
        dialog = PosPagamentoDialog(venda_data=_venda_base())

        dialog._acao_imprimir()
        assert dialog.resultado == "imprimir"

        dialog = PosPagamentoDialog(venda_data=_venda_base())
        dialog._acao_sem_impressao()
        assert dialog.resultado == "sem_impressao"

        dialog = PosPagamentoDialog(venda_data=_venda_base())
        dialog._acao_sair()
        assert dialog.resultado == "sair"
