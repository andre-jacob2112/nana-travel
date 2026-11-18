from datetime import date
from interpretador import ajustar_periodo

HOJE = date(2026, 11, 10)


def test_periodo_inteiro_no_passado_vai_para_ano_seguinte():
    assert ajustar_periodo("01/07/2026", "31/07/2026", HOJE) == ("01/07/2027", "31/07/2027")


def test_dia_unico_no_passado_vai_para_ano_seguinte():
    assert ajustar_periodo("13/09/2026", "13/09/2026", HOJE) == ("13/09/2027", "13/09/2027")


def test_periodo_que_contem_hoje_comeca_hoje():
    assert ajustar_periodo("01/11/2026", "15/11/2026", HOJE) == ("10/11/2026", "15/11/2026")


def test_periodo_futuro_no_mesmo_mes_nao_muda():
    assert ajustar_periodo("16/11/2026", "30/11/2026", HOJE) == ("16/11/2026", "30/11/2026")


def test_periodo_no_ano_seguinte_nao_muda():
    assert ajustar_periodo("01/02/2027", "15/02/2027", HOJE) == ("01/02/2027", "15/02/2027")


def test_sem_datas_continua_sem_datas():
    assert ajustar_periodo(None, None, HOJE) == (None, None)
