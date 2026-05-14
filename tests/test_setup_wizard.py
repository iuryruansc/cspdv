"""
    python -m pytest tests/test_setup_wizard.py -v
    python -m pytest tests/test_setup_wizard.py -v -k "TestValidacoes"
    python -m pytest tests/test_setup_wizard.py -v -k "TestGetData"
    python -m pytest tests/test_setup_wizard.py -v -k "TestEndereco"
    python -m pytest tests/test_setup_wizard.py -v -k "TestSetupModel
    python -m pytest tests/test_setup_wizard.py -v -k "TestFluxoWizard"
"""

import sys
import requests
import pytest
from unittest.mock import patch, MagicMock, call

from PyQt5.QtWidgets import QApplication
_app = QApplication.instance() or QApplication(sys.argv)

# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def page_empresa():
    from modules.setup.views.setup_wizard_view import PageEmpresa
    return PageEmpresa()

@pytest.fixture
def page_pdv():
    from modules.setup.views.setup_wizard_view import PagePDV
    return PagePDV()

@pytest.fixture
def page_admin():
    from modules.setup.views.setup_wizard_view import PageAdmin
    return PageAdmin()

@pytest.fixture
def wizard():
    from modules.setup.views.setup_wizard_view import SetupWizardView
    return SetupWizardView()

def _preencher_empresa(page, cnpj='11222333000181'):
    page.f_razao.set_value('Empresa Teste LTDA')
    page.f_cnpj.set_value(cnpj)

def _preencher_admin(page, senha='senha123', confirma=None):
    page.f_nome.set_value('Administrador')
    page.f_login.set_value('admin')
    page.f_senha.set_value(senha)
    page.f_confirma.set_value(confirma if confirma is not None else senha)

# ─────────────────────────────────────────────────────────────────────────────
# TestValidacoes — valida cada página isoladamente
# ─────────────────────────────────────────────────────────────────────────────

class TestValidacoes:

    # ── PageEmpresa ──────────────────────────────────────────────────────────

    def test_empresa_valida(self, page_empresa):
        _preencher_empresa(page_empresa)
        assert page_empresa.validate() is True

    def test_empresa_razao_vazia(self, page_empresa):
        page_empresa.f_cnpj.set_value('11222333000181')
        assert page_empresa.validate() is False

    def test_empresa_razao_curta(self, page_empresa):
        page_empresa.f_razao.set_value('AB')
        page_empresa.f_cnpj.set_value('11222333000181')
        assert page_empresa.validate() is False

    def test_empresa_cnpj_invalido(self, page_empresa):
        page_empresa.f_razao.set_value('Empresa Teste LTDA')
        page_empresa.f_cnpj.set_value('00000000000000')
        assert page_empresa.validate() is False

    def test_empresa_cnpj_digitos_iguais(self, page_empresa):
        page_empresa.f_razao.set_value('Empresa Teste LTDA')
        page_empresa.f_cnpj.set_value('11111111111111')
        assert page_empresa.validate() is False

    def test_empresa_cnpj_curto(self, page_empresa):
        page_empresa.f_razao.set_value('Empresa Teste')
        page_empresa.f_cnpj.set_value('1234')
        assert page_empresa.validate() is False

    def test_empresa_email_invalido(self, page_empresa):
        _preencher_empresa(page_empresa)
        page_empresa.f_email.set_value('emailsemarroba')
        assert page_empresa.validate() is False

    def test_empresa_email_valido(self, page_empresa):
        _preencher_empresa(page_empresa)
        page_empresa.f_email.set_value('contato@empresa.com')
        assert page_empresa.validate() is True

    def test_empresa_email_vazio_permitido(self, page_empresa):
        _preencher_empresa(page_empresa)
        page_empresa.f_email.set_value('')
        assert page_empresa.validate() is True

    def test_empresa_telefone_incompleto(self, page_empresa):
        _preencher_empresa(page_empresa)
        page_empresa.f_telefone.set_value('119')
        assert page_empresa.validate() is False

    def test_empresa_telefone_vazio_permitido(self, page_empresa):
        _preencher_empresa(page_empresa)
        page_empresa.f_telefone.set_value('')
        assert page_empresa.validate() is True

    # ── PagePDV ──────────────────────────────────────────────────────────────

    def test_pdv_valido(self, page_pdv):
        page_pdv.f_id.set_value('PDV-01')
        assert page_pdv.validate() is True

    def test_pdv_identificacao_vazia(self, page_pdv):
        page_pdv.f_id.set_value('')
        assert page_pdv.validate() is False

    # ── PageAdmin ────────────────────────────────────────────────────────────

    def test_admin_valido(self, page_admin):
        _preencher_admin(page_admin)
        assert page_admin.validate() is True

    def test_admin_nome_vazio(self, page_admin):
        _preencher_admin(page_admin)
        page_admin.f_nome.set_value('')
        assert page_admin.validate() is False

    def test_admin_login_vazio(self, page_admin):
        _preencher_admin(page_admin)
        page_admin.f_login.set_value('')
        assert page_admin.validate() is False

    def test_admin_senha_curta(self, page_admin):
        _preencher_admin(page_admin, senha='abc', confirma='abc')
        assert page_admin.validate() is False

    def test_admin_senhas_diferentes(self, page_admin):
        _preencher_admin(page_admin, senha='senha123', confirma='outrasenha')
        assert page_admin.validate() is False

    def test_admin_email_invalido(self, page_admin):
        _preencher_admin(page_admin)
        page_admin.f_email.set_value('naoemail')
        assert page_admin.validate() is False

    def test_admin_email_vazio_permitido(self, page_admin):
        _preencher_admin(page_admin)
        page_admin.f_email.set_value('')
        assert page_admin.validate() is True

# ─────────────────────────────────────────────────────────────────────────────
# TestGetData — verifica se as chaves retornadas são as esperadas
# ─────────────────────────────────────────────────────────────────────────────

class TestGetData:

    CHAVES_EMPRESA = {
        'razao_social', 'nome_fantasia', 'cnpj', 'inscricao_estadual',
        'regime_tributario', 'email', 'telefone',
    }
    CHAVES_ENDERECO = {'cep', 'logradouro', 'numero', 'bairro', 'cidade', 'estado'}
    CHAVES_PDV      = {'identificacao', 'descricao'}
    CHAVES_ADMIN    = {'nome_completo', 'login', 'email', 'senha'}

    def test_empresa_retorna_chaves_corretas(self, page_empresa):
        _preencher_empresa(page_empresa)
        assert set(page_empresa.get_data().keys()) == self.CHAVES_EMPRESA

    def test_empresa_cnpj_somente_numeros(self, page_empresa):
        _preencher_empresa(page_empresa, cnpj='11.222.333/0001-81')
        cnpj = page_empresa.get_data()['cnpj']
        assert cnpj.isdigit()
        assert len(cnpj) == 14

    def test_endereco_retorna_chaves_corretas(self):
        from modules.setup.views.setup_wizard_view import PageEndereco
        page = PageEndereco()
        assert set(page.get_data().keys()) == self.CHAVES_ENDERECO

    def test_pdv_retorna_chaves_corretas(self, page_pdv):
        assert set(page_pdv.get_data().keys()) == self.CHAVES_PDV

    def test_pdv_descricao_fallback(self, page_pdv):
        page_pdv.f_id.set_value('CAIXA-02')
        page_pdv.f_desc.set_value('')
        data = page_pdv.get_data()
        assert data['descricao'] == 'CAIXA-02'

    def test_admin_retorna_chaves_corretas(self, page_admin):
        _preencher_admin(page_admin)
        assert set(page_admin.get_data().keys()) == self.CHAVES_ADMIN

    def test_admin_senha_em_texto_claro(self, page_admin):
        _preencher_admin(page_admin, senha='minhaSenha99')
        assert page_admin.get_data()['senha'] == 'minhaSenha99'

# ─────────────────────────────────────────────────────────────────────────────
# TestEndereco — valida e get_data da página de endereço + consulta ViaCEP
# ─────────────────────────────────────────────────────────────────────────────

class TestEndereco:

    @pytest.fixture
    def page(self):
        from modules.setup.views.setup_wizard_view import PageEndereco
        return PageEndereco()

    def _preencher(self, page):
        page.f_logr.set_value('Rua das Flores')
        page.f_numero.set_value('100')
        page.f_bairro.set_value('Centro')
        page.f_cidade.set_value('São Paulo')
        page.f_estado.set_value('SP')

    # ── validate ─────────────────────────────────────────────────────────────

    def test_endereco_sem_campos_obrigatorios_passa(self, page):
        assert page.validate() is True

    def test_endereco_completamente_preenchido_valido(self, page):
        self._preencher(page)
        page.f_cep.set_value('01310-100')
        assert page.validate() is True

    # ── get_data ─────────────────────────────────────────────────────────────

    def test_retorna_todas_as_chaves(self, page):
        esperadas = {'cep', 'logradouro', 'numero', 'bairro', 'cidade', 'estado'}
        assert set(page.get_data().keys()) == esperadas

    def test_cep_retornado_somente_numeros(self, page):
        page.f_cep.set_value('01310-100')
        cep = page.get_data()['cep']
        assert cep.isdigit() or cep == '', f"CEP deve conter apenas dígitos, recebido: '{cep}'"

    def test_cep_vazio_retorna_string_vazia(self, page):
        cep = page.get_data()['cep']
        assert cep == ''

    def test_campos_retornados_corretamente(self, page):
        self._preencher(page)
        data = page.get_data()
        assert data['logradouro'] == 'Rua das Flores'
        assert data['numero']     == '100'
        assert data['bairro']     == 'Centro'
        assert data['cidade']     == 'São Paulo'
        assert data['estado']     == 'SP'

    def test_estado_vazio_retorna_string_vazia(self, page):
        page.f_estado.set_value('')
        assert page.get_data()['estado'] == ''

    # ── consultar_cep (ViaCEP mockado) ────────────────────────────────────

    @patch('modules.setup.views.setup_wizard_view.requests.get')
    def test_viacep_preenche_campos(self, mock_get, page):
        mock_get.return_value.json.return_value = {
            'logradouro': 'Avenida Paulista',
            'bairro':     'Bela Vista',
            'localidade': 'São Paulo',
            'uf':         'SP',
        }
        page.f_cep.set_value('01310100')
        page.consultar_cep()

        data = page.get_data()
        assert data['logradouro'] == 'Avenida Paulista'
        assert data['bairro']     == 'Bela Vista'
        assert data['cidade']     == 'São Paulo'
        assert data['estado']     == 'SP'

    @patch('modules.setup.views.setup_wizard_view.requests.get')
    def test_viacep_cep_invalido_nao_preenche(self, mock_get, page):
        mock_get.return_value.json.return_value = {'erro': True}
        page.f_logr.set_value('Valor anterior')
        page.f_cep.set_value('00000000')
        page.consultar_cep()

        assert page.get_data()['logradouro'] == 'Valor anterior'

    @patch(
        'modules.setup.views.setup_wizard_view.requests.get',
        side_effect=requests.exceptions.ConnectionError('timeout simulado'),
    )
    def test_viacep_falha_de_rede_nao_propaga(self, mock_get, page):
        page.f_cep.set_value('01310100')
        try:
            page.consultar_cep()
        except requests.exceptions.ConnectionError:
            pytest.fail(
                "consultar_cep() propagou ConnectionError — "
                "verificar se except cobre requests.RequestException"
            )

    @patch('modules.setup.views.setup_wizard_view.requests.get')
    def test_viacep_nao_chamado_com_cep_incompleto(self, mock_get, page):
        page.f_cep.set_value('0131')
        page.consultar_cep()
        mock_get.assert_not_called()

# ─────────────────────────────────────────────────────────────────────────────
# TestSetupModel — testa is_first_run e salvar_tudo com banco mockado
# ─────────────────────────────────────────────────────────────────────────────

class TestSetupModel:

    EMPRESA = {
        'razao_social': 'Empresa Teste LTDA', 'nome_fantasia': 'Teste',
        'cnpj': '11222333000181', 'inscricao_estadual': '',
        'regime_tributario': 'Simples Nacional', 'email': '', 'telefone': '',
        'logradouro': 'Rua A', 'numero': '10', 'bairro': 'Centro',
        'cidade': 'São Paulo', 'estado': 'SP', 'cep': '01310100',
    }
    PDV   = {'identificacao': 'PDV-01', 'descricao': 'Caixa Principal'}
    ADMIN = {
        'nome_completo': 'Administrador', 'login': 'admin',
        'email': 'admin@teste.com', 'senha': 'senha123',
    }

    def _make_cursor(self, count=0, lastrowid=1):
        cursor = MagicMock()
        cursor.__enter__ = MagicMock(return_value=cursor)
        cursor.__exit__  = MagicMock(return_value=False)
        cursor.fetchone.return_value = (count,)
        cursor.lastrowid = lastrowid
        return cursor

    @patch('modules.setup.models.setup_model.get_connection')
    def test_is_first_run_true(self, mock_get_conn):
        from modules.setup.models.setup_model import SetupModel
        cursor = self._make_cursor(count=0)
        mock_get_conn.return_value.cursor.return_value = cursor
        assert SetupModel.is_first_run() is True

    @patch('modules.setup.models.setup_model.get_connection')
    def test_is_first_run_false(self, mock_get_conn):
        from modules.setup.models.setup_model import SetupModel
        cursor = self._make_cursor(count=1)
        mock_get_conn.return_value.cursor.return_value = cursor
        assert SetupModel.is_first_run() is False

    @patch('modules.setup.models.setup_model.get_connection')
    def test_salvar_tudo_chama_commit(self, mock_get_conn):
        from modules.setup.models.setup_model import SetupModel
        conn   = mock_get_conn.return_value
        cursor = self._make_cursor(lastrowid=1)
        conn.cursor.return_value = cursor

        SetupModel.salvar_tudo(self.EMPRESA, self.PDV, self.ADMIN)
        conn.commit.assert_called_once()

    @patch('modules.setup.models.setup_model.get_connection')
    def test_salvar_tudo_insere_nas_tabelas_corretas(self, mock_get_conn):
        from modules.setup.models.setup_model import SetupModel
        conn   = mock_get_conn.return_value
        cursor = self._make_cursor(lastrowid=1)
        conn.cursor.return_value = cursor

        SetupModel.salvar_tudo(self.EMPRESA, self.PDV, self.ADMIN)

        sql_calls = ' '.join(
            str(c.args[0]).lower()
            for c in cursor.execute.call_args_list
        )
        for tabela in ['config_empresa', 'pdvs', 'cargos', 'perfis',
                       'permissoes', 'perfil_permissoes', 'funcionarios', 'usuarios']:
            assert tabela in sql_calls, f"INSERT em '{tabela}' não encontrado"

    @patch('modules.setup.models.setup_model.get_connection')
    def test_salvar_tudo_faz_rollback_em_erro(self, mock_get_conn):
        from modules.setup.models.setup_model import SetupModel
        conn   = mock_get_conn.return_value
        cursor = self._make_cursor()
        cursor.execute.side_effect = Exception('Erro simulado')
        conn.cursor.return_value = cursor

        with pytest.raises(Exception, match='Erro simulado'):
            SetupModel.salvar_tudo(self.EMPRESA, self.PDV, self.ADMIN)

        conn.rollback.assert_called_once()
        conn.commit.assert_not_called()

    @patch('modules.setup.models.setup_model.get_connection')
    def test_salvar_tudo_senha_com_bcrypt(self, mock_get_conn):
        from modules.setup.models.setup_model import SetupModel
        conn   = mock_get_conn.return_value
        cursor = self._make_cursor(lastrowid=1)
        conn.cursor.return_value = cursor

        SetupModel.salvar_tudo(self.EMPRESA, self.PDV, self.ADMIN)

        usuario_call = next(
            c for c in cursor.execute.call_args_list
            if 'usuarios' in str(c.args[0]).lower()
        )
        params = usuario_call.args[1]

        assert params['senha_hash'].startswith('$2b$'), "Senha deve ser hash bcrypt começando com $2b$"

        assert params['senha_hash'] != self.ADMIN['senha'], "Senha em texto puro não deve ser enviada ao banco"

        assert self.ADMIN['senha'] not in str(params), \
            "Senha em texto puro não deve estar nos parâmetros do INSERT usuarios"

        assert params.get('senha_hash') != self.ADMIN['senha'], \
            "Coluna senha_hash está recebendo texto puro"

        import bcrypt
        assert bcrypt.checkpw(
            self.ADMIN['senha'].encode('utf-8'),
            params['senha_hash'].encode('utf-8'),
        ), "Hash bcrypt não corresponde à senha original"

    @patch('modules.setup.models.setup_model.get_connection')
    def test_salvar_tudo_fecha_cursor(self, mock_get_conn):
        from modules.setup.models.setup_model import SetupModel
        conn   = mock_get_conn.return_value
        cursor = self._make_cursor(lastrowid=1)
        conn.cursor.return_value = cursor

        SetupModel.salvar_tudo(self.EMPRESA, self.PDV, self.ADMIN)
        cursor.close.assert_called_once()

# ─────────────────────────────────────────────────────────────────────────────
# TestFluxoWizard — testa navegação e integração entre páginas
# ─────────────────────────────────────────────────────────────────────────────

class TestFluxoWizard:
    def _preencher_todas_as_paginas(self, wiz):
        wiz.pages[1].f_razao.set_value('Empresa Teste LTDA')
        wiz.pages[1].f_cnpj.set_value('11222333000181')
        wiz.pages[3].f_id.set_value('PDV-01')
        wiz.pages[4].f_nome.set_value('Administrador')
        wiz.pages[4].f_login.set_value('admin')
        wiz.pages[4].f_senha.set_value('senha123')
        wiz.pages[4].f_confirma.set_value('senha123')

    def test_pagina_inicial_e_zero(self, wizard):
        assert wizard._current == 0

    def test_avancar_incrementa_pagina(self, wizard):
        pagina_antes = wizard._current
        wizard._avancar()
        assert wizard._current == pagina_antes + 1
        assert wizard.stack.currentIndex() == wizard._current

    def test_avancar_sequencial_todas_as_paginas(self, wizard):
        self._preencher_todas_as_paginas(wizard)
        for esperado in range(1, len(wizard.pages) - 1):
            wizard._avancar()
            assert wizard._current == esperado, f"Esperado página {esperado}, atual {wizard._current}"

    def test_btn_avancar_visivel_em_todas_as_paginas(self, wizard):
        for i in range(len(wizard.pages) - 1):
            wizard._current = i
            wizard._atualizar_ui()
            assert not wizard.btn_avancar.isHidden(), \
                f"btn_avancar ocultado na página {i}"

    def test_voltar_decrementa_pagina(self, wizard):
        wizard._current = 2
        wizard._atualizar_ui()
        pagina_antes = wizard._current
        wizard._voltar()
        assert wizard._current == pagina_antes - 1
        assert wizard.stack.currentIndex() == wizard._current

    def test_voltar_oculto_na_primeira_pagina(self, wizard):
        wizard._current = 0
        wizard._atualizar_ui()
        assert wizard.btn_voltar.isHidden()

    def test_voltar_visivel_a_partir_da_segunda_pagina(self, wizard):
        for i in range(1, len(wizard.pages)):
            wizard._current = i
            wizard._atualizar_ui()
            assert not wizard.btn_voltar.isHidden(), \
                f"btn_voltar ocultado na página {i}"

    def test_nao_volta_alem_da_primeira(self, wizard):
        wizard._current = 0
        wizard._voltar()
        assert wizard._current == 0
        assert wizard.stack.currentIndex() == 0

    def test_nao_avanca_com_validacao_falha(self, wizard):
        wizard._current = 1
        wizard._atualizar_ui()
        wizard._avancar()
        assert wizard._current == 1

    def test_avanca_com_dados_validos(self, wizard):
        wizard._current = 1
        wizard._atualizar_ui()
        wizard.pages[1].f_razao.set_value('Empresa Teste LTDA')
        wizard.pages[1].f_cnpj.set_value('11222333000181')
        wizard._avancar()
        assert wizard._current == 2

    def test_dados_coletados_na_pagina_conclusao(self, wizard):
        self._preencher_todas_as_paginas(wizard)
        wizard._current = len(wizard.pages) - 2
        wizard._avancar()
        assert wizard._current == len(wizard.pages) - 1
        assert wizard._dados_empresa.get('razao_social') == 'Empresa Teste LTDA'
        assert wizard._dados_pdv.get('identificacao') == 'PDV-01'
        assert wizard._dados_admin.get('login') == 'admin'

    def test_foi_concluido_falso_antes_salvar(self, wizard):
        assert wizard.foi_concluido() is False

    @patch('modules.setup.views.setup_wizard_view.SetupModel.salvar_tudo')
    def test_salvar_chama_model(self, mock_salvar, wizard):
        self._preencher_todas_as_paginas(wizard)
        wizard._current = len(wizard.pages) - 1
        wizard._atualizar_ui()
        wizard._salvar()
        mock_salvar.assert_called_once()

    @patch('modules.setup.views.setup_wizard_view.SetupModel.salvar_tudo')
    def test_foi_concluido_verdadeiro_apos_salvar(self, mock_salvar, wizard):
        self._preencher_todas_as_paginas(wizard)
        wizard._current = len(wizard.pages) - 1
        wizard._salvar()
        assert wizard.foi_concluido() is True

    @patch(
        'modules.setup.views.setup_wizard_view.SetupModel.salvar_tudo',
        side_effect=Exception('Erro de banco'),
    )
    def test_erro_no_salvar_nao_marca_concluido(self, mock_salvar, wizard):
        self._preencher_todas_as_paginas(wizard)
        wizard._current = len(wizard.pages) - 1
        wizard._salvar()
        assert wizard.foi_concluido() is False

    @patch('modules.setup.views.setup_wizard_view.SetupModel.salvar_tudo')
    def test_recoleta_dados_antes_de_salvar(self, mock_salvar, wizard):
        self._preencher_todas_as_paginas(wizard)
        wizard._current = len(wizard.pages) - 2
        wizard._avancar()
        wizard.pages[4].f_login.set_value('novo_login')
        wizard._salvar()
        assert wizard._dados_admin['login'] == 'novo_login'
