from avaliar_interpretador import comparar_roteiro

ESPERADO = {"trechos": [
    {"origem": "São Paulo", "destino": "Recife", "inicio": "12/12/2026", "fim": "12/12/2026"},
    {"origem": "Recife", "destino": "Goiânia", "inicio": "13/01/2027", "fim": "13/01/2027"},
    {"origem": "Goiânia", "destino": "São Paulo", "inicio": "24/01/2027", "fim": "24/01/2027"},
], "orcamento": 1000, "max_escalas": None}


def copiar_roteiro(roteiro):
    return {"trechos": [dict(trecho) for trecho in roteiro["trechos"]],
            "orcamento": roteiro["orcamento"], "max_escalas": roteiro["max_escalas"]}


def test_roteiros_iguais_nao_tem_diferencas():
    assert comparar_roteiro(ESPERADO, copiar_roteiro(ESPERADO)) == []


def test_numero_de_trechos_diferente_e_uma_diferenca():
    obtido = copiar_roteiro(ESPERADO)
    obtido["trechos"].pop(1)
    assert comparar_roteiro(ESPERADO, obtido) == ["número de trechos: esperado 3, veio 2"]


def test_uma_data_errada_gera_so_essa_diferenca():
    obtido = copiar_roteiro(ESPERADO)
    obtido["trechos"][1]["inicio"] = "14/01/2027"
    assert comparar_roteiro(ESPERADO, obtido) == [
        "trecho 2 inicio: esperado 13/01/2027, veio 14/01/2027"]
