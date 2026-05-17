from modules.shared.constants import FLAG_NAO, FLAG_SIM, alternar_flag, bool_para_flag, flag_ativa


def test_flag_ativa_respeita_defaults_e_variacoes():
    assert flag_ativa("S") is True
    assert flag_ativa("s") is True
    assert flag_ativa("N") is False
    assert flag_ativa(None, default=FLAG_SIM) is True
    assert flag_ativa(None, default=FLAG_NAO) is False


def test_bool_para_flag_normaliza_booleanos():
    assert bool_para_flag(True) == FLAG_SIM
    assert bool_para_flag(False) == FLAG_NAO


def test_alternar_flag_inverte_estado():
    assert alternar_flag("S") == FLAG_NAO
    assert alternar_flag("N") == FLAG_SIM
