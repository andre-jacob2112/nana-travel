from datetime import date
from comparador import carregar_passagens, buscar, normalizar

PASSAGENS = carregar_passagens("passagens.csv")


def buscar_dezembro(origem, destino, orcamento, max_escalas):
    return buscar(PASSAGENS, origem, destino,
                  date(2026, 12, 1), date(2026, 12, 16),
                  date(2026, 12, 13), date(2026, 12, 23),
                  orcamento, max_escalas)


def test_melhor_combinacao_dezembro():
    combinacoes = buscar_dezembro("São Paulo", "Recife", 1000, 1)
    assert len(combinacoes) == 9
    melhor = combinacoes[0]
    assert melhor["Total"] == 700
    assert melhor["Ida"]["Companhia"] == "Empresa C"
    assert melhor["Volta"]["Companhia"] == "Empresa L"
    assert melhor["Dias"] == 1


def test_volta_sempre_depois_da_ida():
    combinacoes = buscar_dezembro("São Paulo", "Recife", 1000, 1)
    for combinacao in combinacoes:
        assert combinacao["Dias"] > 0


def test_sem_escalas():
    combinacoes = buscar_dezembro("São Paulo", "Recife", 1000, 0)
    assert len(combinacoes) == 3
    assert combinacoes[0]["Total"] == 750
    assert combinacoes[1]["Total"] == 810
    assert combinacoes[2]["Total"] == 930


def test_orcamento_insuficiente():
    combinacoes = buscar_dezembro("São Paulo", "Recife", 600, 1)
    assert combinacoes == []


def test_virada_de_ano():
    combinacoes = buscar(PASSAGENS, "São Paulo", "Recife",
                         date(2027, 1, 1), date(2027, 1, 10),
                         date(2027, 1, 1), date(2027, 1, 15),
                         1000, 1)
    assert len(combinacoes) == 1
    assert combinacoes[0]["Total"] == 770


def test_cidade_sem_acento_e_maiuscula():
    combinacoes = buscar_dezembro("sao paulo", "RECIFE", 1000, 1)
    assert len(combinacoes) == 9


def test_normalizar():
    assert normalizar("SÃO PAULO") == "sao paulo"


def test_duracao_entre_6_e_7_dias():
    combinacoes = buscar(PASSAGENS, "São Paulo", "Recife",
                         date(2026, 12, 1), date(2026, 12, 16),
                         date(2026, 12, 13), date(2026, 12, 23),
                         1000, 1, 6, 7)
    assert len(combinacoes) == 3
    assert combinacoes[0]["Total"] == 750
    assert combinacoes[1]["Total"] == 800
    assert combinacoes[2]["Total"] == 920
    for combinacao in combinacoes:
        assert 6 <= combinacao["Dias"] <= 7