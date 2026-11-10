import time
from datetime import date

from comparador import normalizar, converter_data
from interpretador import interpretar_pedido

HOJE = date(2026, 11, 10)
META_PERCENTUAL = 0.9
PAUSA = 15

CASOS = [
    {"pedido": "Quero ir de São Paulo para Recife entre 1 e 10 de dezembro e voltar entre 15 e 20 de dezembro, até 1000 reais, no máximo 1 escala",
     "esperado": {"origem": "São Paulo", "destino": "Recife", "inicio_ida": "01/12/2026", "fim_ida": "10/12/2026", "inicio_volta": "15/12/2026", "fim_volta": "20/12/2026", "orcamento": 1000, "max_escalas": 1}},
    {"pedido": "SP pra Recife, ida começo de dezembro, volta meio de dezembro, até R$ 1.200, voo direto",
     "esperado": {"origem": "São Paulo", "destino": "Recife", "inicio_ida": "01/12/2026", "fim_ida": "15/12/2026", "inicio_volta": "11/12/2026", "fim_volta": "20/12/2026", "orcamento": 1200, "max_escalas": 0}},
    {"pedido": "Viagem Rio de Janeiro para Salvador, ida fim de dezembro, volta começo de janeiro, orçamento 1500, até 2 escalas",
     "esperado": {"origem": "Rio de Janeiro", "destino": "Salvador", "inicio_ida": "16/12/2026", "fim_ida": "31/12/2026", "inicio_volta": "01/01/2027", "fim_volta": "15/01/2027", "orcamento": 1500, "max_escalas": 2}},
    {"pedido": "Saindo de Recife para São Paulo no meio de janeiro, voltando no fim de janeiro, gasto máximo de 800 reais, sem escalas",
     "esperado": {"origem": "Recife", "destino": "São Paulo", "inicio_ida": "11/01/2027", "fim_ida": "20/01/2027", "inicio_volta": "16/01/2027", "fim_volta": "31/01/2027", "orcamento": 800, "max_escalas": 0}},
    {"pedido": "Quero ir pra Salvador saindo de BH entre 5 e 8 de dezembro, voltar entre 12 e 14 de dezembro, até 900, uma escala no máximo",
     "esperado": {"origem": "Belo Horizonte", "destino": "Salvador", "inicio_ida": "05/12/2026", "fim_ida": "08/12/2026", "inicio_volta": "12/12/2026", "fim_volta": "14/12/2026", "orcamento": 900, "max_escalas": 1}},
    {"pedido": "Quero ir de São Paulo para Recife",
     "esperado": {"origem": "São Paulo", "destino": "Recife", "inicio_ida": None, "fim_ida": None, "inicio_volta": None, "fim_volta": None, "orcamento": None, "max_escalas": None}},
    {"pedido": "De São Paulo a Recife, ida entre 1 e 5 de dezembro, volta entre 10 e 15 de dezembro, sem escalas",
     "esperado": {"origem": "São Paulo", "destino": "Recife", "inicio_ida": "01/12/2026", "fim_ida": "05/12/2026", "inicio_volta": "10/12/2026", "fim_volta": "15/12/2026", "orcamento": None, "max_escalas": 0}},
    {"pedido": "Ida de São Paulo para Recife entre 1 e 5 de dezembro, volta uma semana depois, até 1000 reais, 1 escala no máximo",
     "esperado": {"origem": "São Paulo", "destino": "Recife", "inicio_ida": "01/12/2026", "fim_ida": "05/12/2026", "inicio_volta": "08/12/2026", "fim_volta": "12/12/2026", "orcamento": 1000, "max_escalas": 1}},
    {"pedido": "Porto Alegre para Florianópolis, ida entre 10 e 12 de janeiro, voltar 3 dias depois, até 600 reais, voo direto",
     "esperado": {"origem": "Porto Alegre", "destino": "Florianópolis", "inicio_ida": "10/01/2027", "fim_ida": "12/01/2027", "inicio_volta": "13/01/2027", "fim_volta": "15/01/2027", "orcamento": 600, "max_escalas": 0}},
    {"pedido": "Quero sair de Curitiba no comecinho de dezembro e ir para Fortaleza, voltando no fim do mês, posso gastar uns 2 mil, aceito até duas escalas",
     "esperado": {"origem": "Curitiba", "destino": "Fortaleza", "inicio_ida": "01/12/2026", "fim_ida": "15/12/2026", "inicio_volta": "16/12/2026", "fim_volta": "31/12/2026", "orcamento": 2000, "max_escalas": 2}},
    {"pedido": "qero ir de sao paulo pra recif entre 2 e 6 de dezembro, volta de 9 a 13 de dezembro, ate mil reais, max 1 escala",
     "esperado": {"origem": "São Paulo", "destino": "Recife", "inicio_ida": "02/12/2026", "fim_ida": "06/12/2026", "inicio_volta": "09/12/2026", "fim_volta": "13/12/2026", "orcamento": 1000, "max_escalas": 1}},
    {"pedido": "Até 1300 reais, sem escalas, volta entre 20 e 25 de dezembro, ida entre 10 e 15 de dezembro, de Brasília para Manaus",
     "esperado": {"origem": "Brasília", "destino": "Manaus", "inicio_ida": "10/12/2026", "fim_ida": "15/12/2026", "inicio_volta": "20/12/2026", "fim_volta": "25/12/2026", "orcamento": 1300, "max_escalas": 0}},
    {"pedido": "Natal para Recife, ida somente no dia 1º de dezembro, volta somente no dia 3 de dezembro, até 500, sem escala",
     "esperado": {"origem": "Natal", "destino": "Recife", "inicio_ida": "01/12/2026", "fim_ida": "01/12/2026", "inicio_volta": "03/12/2026", "fim_volta": "03/12/2026", "orcamento": 500, "max_escalas": 0}},
    {"pedido": "Ida e volta São Paulo e Lisboa, ida entre 5 e 10 de março, volta entre 20 e 25 de março, até 5000 reais, no máximo 1 escala",
     "esperado": {"origem": "São Paulo", "destino": "Lisboa", "inicio_ida": "05/03/2027", "fim_ida": "10/03/2027", "inicio_volta": "20/03/2027", "fim_volta": "25/03/2027", "orcamento": 5000, "max_escalas": 1}},
    {"pedido": "Belém para São Paulo, ida no meio de fevereiro, volta no fim de fevereiro, até 1100, até 1 escala",
     "esperado": {"origem": "Belém", "destino": "São Paulo", "inicio_ida": "11/02/2027", "fim_ida": "20/02/2027", "inicio_volta": "16/02/2027", "fim_volta": "28/02/2027", "orcamento": 1100, "max_escalas": 1}},
    {"pedido": "Quero viajar de Goiânia para Recife, ida entre 10 e 12 de dezembro, até 950 reais",
     "esperado": {"origem": "Goiânia", "destino": "Recife", "inicio_ida": "10/12/2026", "fim_ida": "12/12/2026", "inicio_volta": None, "fim_volta": None, "orcamento": 950, "max_escalas": None}},
    {"pedido": "SP para o Rio, ida dia 20 de dezembro, volta dia 27 de dezembro, orçamento de R$ 450,50, voo direto",
     "esperado": {"origem": "São Paulo", "destino": "Rio de Janeiro", "inicio_ida": "20/12/2026", "fim_ida": "20/12/2026", "inicio_volta": "27/12/2026", "fim_volta": "27/12/2026", "orcamento": 450.5, "max_escalas": 0}},
    {"pedido": "Vou de Salvador a Recife: ida entre o dia 3 e o dia 7 de janeiro, volta duas semanas depois, até 700, até 1 escala",
     "esperado": {"origem": "Salvador", "destino": "Recife", "inicio_ida": "03/01/2027", "fim_ida": "07/01/2027", "inicio_volta": "17/01/2027", "fim_volta": "21/01/2027", "orcamento": 700, "max_escalas": 1}},
    {"pedido": "Recife pra São Paulo, ida no fim de novembro, volta no começo de dezembro, até 1000, sem escalas",
     "esperado": {"origem": "Recife", "destino": "São Paulo", "inicio_ida": "16/11/2026", "fim_ida": "30/11/2026", "inicio_volta": "01/12/2026", "fim_volta": "15/12/2026", "orcamento": 1000, "max_escalas": 0}},
    {"pedido": "Quero ir pra Recife saindo de São Paulo, ida entre 1 e 10 de dezembro, volta entre 13 e 23 de dezembro, até 1000, aceito até três escalas",
     "esperado": {"origem": "São Paulo", "destino": "Recife", "inicio_ida": "01/12/2026", "fim_ida": "10/12/2026", "inicio_volta": "13/12/2026", "fim_volta": "23/12/2026", "orcamento": 1000, "max_escalas": 3}},
]


# Conjunto de VALIDAÇÃO: pedidos novos, nunca usados para ajustar o prompt.
CASOS_VALIDACAO = [
    {"pedido": "Partindo de Fortaleza rumo a São Paulo, embarque entre 4 e 9 de dezembro, retorno entre 14 e 18 de dezembro, teto de 1.400 reais, tolero 1 conexão",
     "esperado": {"origem": "Fortaleza", "destino": "São Paulo", "inicio_ida": "04/12/2026", "fim_ida": "09/12/2026", "inicio_volta": "14/12/2026", "fim_volta": "18/12/2026", "orcamento": 1400, "max_escalas": 1, "dias_min": None, "dias_max": None}},
    {"pedido": "Quero passar 10 dias em Salvador saindo de Curitiba, indo em algum momento da primeira quinzena de janeiro, máximo R$ 1.800, só voo direto",
     "esperado": {"origem": "Curitiba", "destino": "Salvador", "inicio_ida": "01/01/2027", "fim_ida": "15/01/2027", "inicio_volta": "11/01/2027", "fim_volta": "25/01/2027", "orcamento": 1800, "max_escalas": 0, "dias_min": 10, "dias_max": 10}},
    {"pedido": "Floripa para Porto Alegre, ida no finalzinho de janeiro, volta no começo de fevereiro, até 700 reais, 2 escalas no máximo",
     "esperado": {"origem": "Florianópolis", "destino": "Porto Alegre", "inicio_ida": "16/01/2027", "fim_ida": "31/01/2027", "inicio_volta": "01/02/2027", "fim_volta": "15/02/2027", "orcamento": 700, "max_escalas": 2, "dias_min": None, "dias_max": None}},
    {"pedido": "De Recife pra Natal, saio dia 12 de dezembro e volto dia 19, até 400, direto",
     "esperado": {"origem": "Recife", "destino": "Natal", "inicio_ida": "12/12/2026", "fim_ida": "12/12/2026", "inicio_volta": "19/12/2026", "fim_volta": "19/12/2026", "orcamento": 400, "max_escalas": 0, "dias_min": None, "dias_max": None}},
    {"pedido": "Belo Horizonte para Rio de Janeiro, ida entre 20 e 24 de dezembro, volta entre 24 e 30 de dezembro, ficando entre 4 e 6 dias, até 900 reais, aceito uma escala",
     "esperado": {"origem": "Belo Horizonte", "destino": "Rio de Janeiro", "inicio_ida": "20/12/2026", "fim_ida": "24/12/2026", "inicio_volta": "24/12/2026", "fim_volta": "30/12/2026", "orcamento": 900, "max_escalas": 1, "dias_min": 4, "dias_max": 6}},
    {"pedido": "Manaus → Belém. Ida: meados de fevereiro. Volta: fim de fevereiro. Orçamento: R$ 950. Escalas: no máximo 1.",
     "esperado": {"origem": "Manaus", "destino": "Belém", "inicio_ida": "11/02/2027", "fim_ida": "20/02/2027", "inicio_volta": "16/02/2027", "fim_volta": "28/02/2027", "orcamento": 950, "max_escalas": 1, "dias_min": None, "dias_max": None}},
    {"pedido": "Preciso de uma passagem de ida e volta para Lisboa saindo de São Paulo, com até uma escala, gastando no máximo 6 mil",
     "esperado": {"origem": "São Paulo", "destino": "Lisboa", "inicio_ida": None, "fim_ida": None, "inicio_volta": None, "fim_volta": None, "orcamento": 6000, "max_escalas": 1, "dias_min": None, "dias_max": None}},
    {"pedido": "rj pra sp, vou dia 5/12 e volto 8/12, max 350 conto, sem conexão",
     "esperado": {"origem": "Rio de Janeiro", "destino": "São Paulo", "inicio_ida": "05/12/2026", "fim_ida": "05/12/2026", "inicio_volta": "08/12/2026", "fim_volta": "08/12/2026", "orcamento": 350, "max_escalas": 0, "dias_min": None, "dias_max": None}},
    {"pedido": "Ida de Salvador para Fortaleza no começo de janeiro, voltando 5 dias depois, até mil e quinhentos reais, até 1 escala",
     "esperado": {"origem": "Salvador", "destino": "Fortaleza", "inicio_ida": "01/01/2027", "fim_ida": "15/01/2027", "inicio_volta": "06/01/2027", "fim_volta": "20/01/2027", "orcamento": 1500, "max_escalas": 1, "dias_min": 5, "dias_max": 5}},
    {"pedido": "Goiânia para Brasília: ida entre 26 e 30 de novembro, volta entre 1 e 4 de dezembro, até 300 reais, sem escala, viagem de no mínimo 3 dias",
     "esperado": {"origem": "Goiânia", "destino": "Brasília", "inicio_ida": "26/11/2026", "fim_ida": "30/11/2026", "inicio_volta": "01/12/2026", "fim_volta": "04/12/2026", "orcamento": 300, "max_escalas": 0, "dias_min": 3, "dias_max": None}},
    # Escrito por André, sem acesso ao prompt
    {"pedido": "tava pensando em sair daqui de bh na primeira metade de setembro pra voltar só no finalzinho de outubro la de salvador",
     "esperado": {"origem": "Belo Horizonte", "destino": "Salvador", "inicio_ida": "01/09/2027", "fim_ida": "15/09/2027", "inicio_volta": "16/10/2027", "fim_volta": "31/10/2027", "orcamento": None, "max_escalas": None, "dias_min": None, "dias_max": None}},
]


def campo_correto(campo, esperado, obtido):
    if esperado is None:
        return obtido is None
    if obtido is None:
        return False
    try:
        if campo in ("origem", "destino"):
            return normalizar(str(obtido)) == normalizar(esperado)
        if campo in ("inicio_ida", "fim_ida", "inicio_volta", "fim_volta"):
            return converter_data(str(obtido)) == converter_data(esperado)
        return float(obtido) == float(esperado)
    except ValueError:
        return False


def avaliar(casos):
    pedidos_corretos = 0
    campos_corretos = 0
    total_campos = 0
    falhas_de_api = 0

    for numero, caso in enumerate(casos, start=1):
        try:
            obtido = interpretar_pedido(caso["pedido"], HOJE)
        except (RuntimeError, ValueError) as erro:
            print(f"{numero:2}. ⚠️  ERRO: {erro}")
            falhas_de_api += 1
            time.sleep(PAUSA)
            continue

        erros = []
        for campo in caso["esperado"]:
            esperado = caso["esperado"][campo]
            valor = obtido.get(campo)
            total_campos += 1
            if campo_correto(campo, esperado, valor):
                campos_corretos += 1
            else:
                erros.append(f"{campo}: esperado {esperado}, veio {valor}")

        if erros:
            print(f"{numero:2}. ❌ {caso['pedido']}")
            for erro in erros:
                print(f"      {erro}")
        else:
            pedidos_corretos += 1
            print(f"{numero:2}. ✅ {caso['pedido']}")

        time.sleep(PAUSA)

    total = len(casos)
    print()
    print(f"Pedidos 100% corretos: {pedidos_corretos}/{total}")
    print(f"Campos corretos: {campos_corretos}/{total_campos}")
    print(f"Falhas de API: {falhas_de_api}")
    if falhas_de_api > 0:
        print("Rodada INVÁLIDA: houve falhas de API, então o critério não pode ser avaliado. Rode de novo.")
    elif pedidos_corretos >= META_PERCENTUAL * total:
        print(f"Critério de sucesso (≥ {META_PERCENTUAL:.0%}): ATINGIDO")
    else:
        print(f"Critério de sucesso (≥ {META_PERCENTUAL:.0%}): NÃO atingido")


if __name__ == "__main__":
    escolha = input("Qual conjunto? (1 = teste, 2 = validação): ").strip()
    if escolha == "2":
        avaliar(CASOS_VALIDACAO)
    else:
        avaliar(CASOS)