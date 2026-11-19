import sys
import time
from datetime import date

from comparador import normalizar, converter_data
from interpretador import interpretar_pedido, interpretar_roteiro

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


# Conjunto de VALIDAÇÃO 2: criado ANTES de mudar o prompt, para medir a mudança sem viés.
CASOS_VALIDACAO_2 = [
    # Escritos por André
    {"pedido": "Quero ir no comecinho de Fevereiro para Recife a partir de Salvador, tenho uns 900 conto",
     "esperado": {"origem": "Salvador", "destino": "Recife", "inicio_ida": "01/02/2027", "fim_ida": "15/02/2027", "inicio_volta": None, "fim_volta": None, "orcamento": 900, "max_escalas": None, "dias_min": None, "dias_max": None}},
    {"pedido": "Quero ir no Final de Março para salvador partindo de Refice, orçamento de 1500 reais",
     "esperado": {"origem": "Recife", "destino": "Salvador", "inicio_ida": "16/03/2027", "fim_ida": "31/03/2027", "inicio_volta": None, "fim_volta": None, "orcamento": 1500, "max_escalas": None, "dias_min": None, "dias_max": None}},
    {"pedido": "Quero ir no dia 13 e voltar no dia 16 de setembro, de sa paulo pra refic, mas acima de 780 fica impossivel pra mim",
     "esperado": {"origem": "São Paulo", "destino": "Recife", "inicio_ida": "13/09/2027", "fim_ida": "13/09/2027", "inicio_volta": "16/09/2027", "fim_volta": "16/09/2027", "orcamento": 780, "max_escalas": None, "dias_min": None, "dias_max": None}},
    {"pedido": "Quero ir pra São Paulo com 500 reais em julho",
     "esperado": {"origem": None, "destino": "São Paulo", "inicio_ida": "01/07/2027", "fim_ida": "31/07/2027", "inicio_volta": None, "fim_volta": None, "orcamento": 500, "max_escalas": None, "dias_min": None, "dias_max": None}},
    {"pedido": "to afim de viajar pelo nordeste mas nem sei pra onde, tenho só 1000 reais",
     "esperado": {"origem": None, "destino": None, "inicio_ida": None, "fim_ida": None, "inicio_volta": None, "fim_volta": None, "orcamento": 1000, "max_escalas": None, "dias_min": None, "dias_max": None}},
    # Fim/final do mês
    {"pedido": "Saindo de Porto Alegre, quero chegar em Natal no final de abril e retornar no fim de maio, gasto até 2.300 reais, aceito 2 conexões",
     "esperado": {"origem": "Porto Alegre", "destino": "Natal", "inicio_ida": "16/04/2027", "fim_ida": "30/04/2027", "inicio_volta": "16/05/2027", "fim_volta": "31/05/2027", "orcamento": 2300, "max_escalas": 2, "dias_min": None, "dias_max": None}},
    {"pedido": "Fim de novembro, de Brasília pra Salvador, só ida, até 650",
     "esperado": {"origem": "Brasília", "destino": "Salvador", "inicio_ida": "16/11/2026", "fim_ida": "30/11/2026", "inicio_volta": None, "fim_volta": None, "orcamento": 650, "max_escalas": None, "dias_min": None, "dias_max": None}},
    {"pedido": "Vou visitar minha mãe em Fortaleza no final de junho, saindo do Rio, e volto no final de julho; sem escala e no máximo 1.700",
     "esperado": {"origem": "Rio de Janeiro", "destino": "Fortaleza", "inicio_ida": "16/06/2027", "fim_ida": "30/06/2027", "inicio_volta": "16/07/2027", "fim_volta": "31/07/2027", "orcamento": 1700, "max_escalas": 0, "dias_min": None, "dias_max": None}},
    # Datas fixas de ida e volta
    {"pedido": "Embarco em Manaus no dia 22 de janeiro com destino a Belo Horizonte e retorno no dia 2 de fevereiro, limite de 1.900 reais, uma escala está ok",
     "esperado": {"origem": "Manaus", "destino": "Belo Horizonte", "inicio_ida": "22/01/2027", "fim_ida": "22/01/2027", "inicio_volta": "02/02/2027", "fim_volta": "02/02/2027", "orcamento": 1900, "max_escalas": 1, "dias_min": None, "dias_max": None}},
    {"pedido": "Curitiba–Recife: ida 7/3, volta 14/3, voo direto, orçamento livre",
     "esperado": {"origem": "Curitiba", "destino": "Recife", "inicio_ida": "07/03/2027", "fim_ida": "07/03/2027", "inicio_volta": "14/03/2027", "fim_volta": "14/03/2027", "orcamento": None, "max_escalas": 0, "dias_min": None, "dias_max": None}},
    # Começo/meio do mês
    {"pedido": "Quero ir de Belém a Goiânia no meio de abril e voltar no começo de maio, R$ 1.250 no máximo",
     "esperado": {"origem": "Belém", "destino": "Goiânia", "inicio_ida": "11/04/2027", "fim_ida": "20/04/2027", "inicio_volta": "01/05/2027", "fim_volta": "15/05/2027", "orcamento": 1250, "max_escalas": None, "dias_min": None, "dias_max": None}},
    {"pedido": "Florianópolis pra Brasília logo no início de março, volta em meados de março, até 980, até duas paradas",
     "esperado": {"origem": "Florianópolis", "destino": "Brasília", "inicio_ida": "01/03/2027", "fim_ida": "15/03/2027", "inicio_volta": "11/03/2027", "fim_volta": "20/03/2027", "orcamento": 980, "max_escalas": 2, "dias_min": None, "dias_max": None}},
    # Duração
    {"pedido": "Quero ficar uma semana em Maceió, saindo de São Paulo entre 8 e 12 de janeiro, até 1.600 reais, sem escalas",
     "esperado": {"origem": "São Paulo", "destino": "Maceió", "inicio_ida": "08/01/2027", "fim_ida": "12/01/2027", "inicio_volta": "15/01/2027", "fim_volta": "19/01/2027", "orcamento": 1600, "max_escalas": 0, "dias_min": 7, "dias_max": 7}},
    # Incompletos
    {"pedido": "Preciso estar em Campo Grande no começo de dezembro, sem escalas",
     "esperado": {"origem": None, "destino": "Campo Grande", "inicio_ida": "01/12/2026", "fim_ida": "15/12/2026", "inicio_volta": None, "fim_volta": None, "orcamento": None, "max_escalas": 0, "dias_min": None, "dias_max": None}},
    {"pedido": "Tenho 800 reais e quero sair de Vitória, qualquer destino serve",
     "esperado": {"origem": "Vitória", "destino": None, "inicio_ida": None, "fim_ida": None, "inicio_volta": None, "fim_volta": None, "orcamento": 800, "max_escalas": None, "dias_min": None, "dias_max": None}},
]


# Conjunto de ROTEIROS: criado ANTES do prompt de roteiros, para medi-lo sem viés.
# Cada caso tem duas mensagens: m1 (pedido inicial) e m2 (resposta a
# "Gostaria de explorar as possibilidades integrando mais trechos? (s/n)").
# Regras dos valores esperados:
# - a data de ida fica no trecho que chega ao destino original;
# - a data de volta fica no trecho que retorna à origem;
# - o trecho novo fica com a data da m2 ou None;
# - parada sem data ou "data de melhor preço": inicio e fim None;
# - "a partir de <mês>": inicio no dia 1 e fim None;
# - região ou destino não informado: None; sem volta mencionada: sem trecho de volta.
CASOS_ROTEIRO = [
    # Escritos por André
    {"m1": "To afim de ir pra Tóquio em dezembro com orçamento de 1000 saindo de São Paulo e parando em Lisboa no meio",
     "m2": "esse roteiro mesmo",
     "esperado": {"trechos": [
         {"origem": "São Paulo", "destino": "Lisboa", "inicio": None, "fim": None},
         {"origem": "Lisboa", "destino": "Tóquio", "inicio": "01/12/2026", "fim": "31/12/2026"},
     ], "orcamento": 1000, "max_escalas": None}},
    {"m1": "Eu quero uma ida e volta de Fortaleza em janeiro partindo do Rio de Janeiro",
     "m2": "verdade, quero parar em goiania antes, pode ser na data de melhor preço",
     "esperado": {"trechos": [
         {"origem": "Rio de Janeiro", "destino": "Goiânia", "inicio": None, "fim": None},
         {"origem": "Goiânia", "destino": "Fortaleza", "inicio": "01/01/2027", "fim": "31/01/2027"},
         {"origem": "Fortaleza", "destino": "Rio de Janeiro", "inicio": "01/01/2027", "fim": "31/01/2027"},
     ], "orcamento": None, "max_escalas": None}},
    {"m1": "Eu quero ir e voltar de recife partindo de são paulo dia 12/12 e voltando 24/01",
     "m2": "quero parar em goiania dia 13/01 necessariamente",
     "esperado": {"trechos": [
         {"origem": "São Paulo", "destino": "Recife", "inicio": "12/12/2026", "fim": "12/12/2026"},
         {"origem": "Recife", "destino": "Goiânia", "inicio": "13/01/2027", "fim": "13/01/2027"},
         {"origem": "Goiânia", "destino": "São Paulo", "inicio": "24/01/2027", "fim": "24/01/2027"},
     ], "orcamento": None, "max_escalas": None}},
    {"m1": "Acho que to afim de viajar pro nordeste, ve as passagens ai pra mim",
     "m2": "ai, seria legal passar pelo rio tb, já que eu to em sp. Vê com o rio no meio em qualquer data. A viagem toda pode ser a partir de julho msm",
     "esperado": {"trechos": [
         {"origem": "São Paulo", "destino": "Rio de Janeiro", "inicio": "01/07/2027", "fim": None},
         {"origem": "Rio de Janeiro", "destino": None, "inicio": "01/07/2027", "fim": None},
     ], "orcamento": None, "max_escalas": None}},
    # Todas as cidades já na m1
    {"m1": "Saio de BH dia 5 de março pra Salvador, dia 12 sigo pra Recife e dia 20 volto pra BH, até 2500 reais, no máximo 1 escala",
     "m2": "isso, pode buscar",
     "esperado": {"trechos": [
         {"origem": "Belo Horizonte", "destino": "Salvador", "inicio": "05/03/2027", "fim": "05/03/2027"},
         {"origem": "Salvador", "destino": "Recife", "inicio": "12/03/2027", "fim": "12/03/2027"},
         {"origem": "Recife", "destino": "Belo Horizonte", "inicio": "20/03/2027", "fim": "20/03/2027"},
     ], "orcamento": 2500, "max_escalas": 1}},
    {"m1": "curitba pra floripa no começo de janeiro, depois porto alegre no fim de janeiro, e de lá volto pra curitiba em fevereiro, só voo direto",
     "m2": "sim, é isso, e no máximo 900 reais",
     "esperado": {"trechos": [
         {"origem": "Curitiba", "destino": "Florianópolis", "inicio": "01/01/2027", "fim": "15/01/2027"},
         {"origem": "Florianópolis", "destino": "Porto Alegre", "inicio": "16/01/2027", "fim": "31/01/2027"},
         {"origem": "Porto Alegre", "destino": "Curitiba", "inicio": "01/02/2027", "fim": "28/02/2027"},
     ], "orcamento": 900, "max_escalas": 0}},
    # Parada nova com data na m2
    {"m1": "Quero ir de Porto Alegre para Natal, ida entre 3 e 7 de fevereiro, volta entre 20 e 24 de fevereiro, até 2200, até 1 escala",
     "m2": "quero parar em Salvador antes, saindo daqui dia 1º de fevereiro",
     "esperado": {"trechos": [
         {"origem": "Porto Alegre", "destino": "Salvador", "inicio": "01/02/2027", "fim": "01/02/2027"},
         {"origem": "Salvador", "destino": "Natal", "inicio": "03/02/2027", "fim": "07/02/2027"},
         {"origem": "Natal", "destino": "Porto Alegre", "inicio": "20/02/2027", "fim": "24/02/2027"},
     ], "orcamento": 2200, "max_escalas": 1}},
    {"m1": "SP pra Fortaleza dia 8 de janeiro, volto no meio de fevereiro, até 1800",
     "m2": "na volta quero ficar uns dias em brasilia, indo pra lá no fim de janeiro",
     "esperado": {"trechos": [
         {"origem": "São Paulo", "destino": "Fortaleza", "inicio": "08/01/2027", "fim": "08/01/2027"},
         {"origem": "Fortaleza", "destino": "Brasília", "inicio": "16/01/2027", "fim": "31/01/2027"},
         {"origem": "Brasília", "destino": "São Paulo", "inicio": "11/02/2027", "fim": "20/02/2027"},
     ], "orcamento": 1800, "max_escalas": None}},
    # Parada nova sem data na m2
    {"m1": "Manaus para São Paulo entre 10 e 15 de abril, só ida, até 1500",
     "m2": "quero passar por Belém antes, qualquer dia",
     "esperado": {"trechos": [
         {"origem": "Manaus", "destino": "Belém", "inicio": None, "fim": None},
         {"origem": "Belém", "destino": "São Paulo", "inicio": "10/04/2027", "fim": "15/04/2027"},
     ], "orcamento": 1500, "max_escalas": None}},
    {"m1": "Ida e volta Recife–Lisboa, ida em março, volta em abril, até 6000, até 1 escala",
     "m2": "dá pra incluir Madri na volta? a data tanto faz",
     "esperado": {"trechos": [
         {"origem": "Recife", "destino": "Lisboa", "inicio": "01/03/2027", "fim": "31/03/2027"},
         {"origem": "Lisboa", "destino": "Madri", "inicio": None, "fim": None},
         {"origem": "Madri", "destino": "Recife", "inicio": "01/04/2027", "fim": "30/04/2027"},
     ], "orcamento": 6000, "max_escalas": 1}},
    # Quatro trechos
    {"m1": "Goiânia pro Rio dia 2/12, depois salvdor dia 6, e volto pra Goiânia dia 15/12, até 3000 no total, sem escala",
     "m2": "quero incluir Recife entre Salvador e a volta, dia 10/12",
     "esperado": {"trechos": [
         {"origem": "Goiânia", "destino": "Rio de Janeiro", "inicio": "02/12/2026", "fim": "02/12/2026"},
         {"origem": "Rio de Janeiro", "destino": "Salvador", "inicio": "06/12/2026", "fim": "06/12/2026"},
         {"origem": "Salvador", "destino": "Recife", "inicio": "10/12/2026", "fim": "10/12/2026"},
         {"origem": "Recife", "destino": "Goiânia", "inicio": "15/12/2026", "fim": "15/12/2026"},
     ], "orcamento": 3000, "max_escalas": 0}},
    # m2 diz "sim" sem acrescentar cidade
    {"m1": "Quero ir de Belo Horizonte para Porto Alegre no fim de maio e voltar no meio de junho, até 1300",
     "m2": "sim, quero!",
     "esperado": {"trechos": [
         {"origem": "Belo Horizonte", "destino": "Porto Alegre", "inicio": "16/05/2027", "fim": "31/05/2027"},
         {"origem": "Porto Alegre", "destino": "Belo Horizonte", "inicio": "11/06/2027", "fim": "20/06/2027"},
     ], "orcamento": 1300, "max_escalas": None}},
]

CONJUNTOS = {
    "teste": CASOS,
    "validacao": CASOS_VALIDACAO,
    "validacao2": CASOS_VALIDACAO_2,
}


def campo_correto(campo, esperado, obtido):
    if esperado is None:
        return obtido is None
    if obtido is None:
        return False
    try:
        if campo in ("origem", "destino"):
            return normalizar(str(obtido)) == normalizar(esperado)
        if campo in ("inicio_ida", "fim_ida", "inicio_volta", "fim_volta", "inicio", "fim"):
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

    imprimir_resumo(pedidos_corretos, len(casos), campos_corretos, total_campos, falhas_de_api)


def comparar_roteiro(esperado, obtido):
    diferencas = []
    trechos_esperados = esperado["trechos"]
    trechos_obtidos = obtido.get("trechos") or []

    if len(trechos_obtidos) != len(trechos_esperados):
        diferencas.append(f"número de trechos: esperado {len(trechos_esperados)}, veio {len(trechos_obtidos)}")
    else:
        for numero, (trecho_esperado, trecho_obtido) in enumerate(
                zip(trechos_esperados, trechos_obtidos), start=1):
            for campo in ("origem", "destino", "inicio", "fim"):
                valor_esperado = trecho_esperado[campo]
                valor = trecho_obtido.get(campo)
                if not campo_correto(campo, valor_esperado, valor):
                    diferencas.append(f"trecho {numero} {campo}: esperado {valor_esperado}, veio {valor}")

    for campo in ("orcamento", "max_escalas"):
        valor_esperado = esperado[campo]
        valor = obtido.get(campo)
        if not campo_correto(campo, valor_esperado, valor):
            diferencas.append(f"{campo}: esperado {valor_esperado}, veio {valor}")

    return diferencas


def avaliar_roteiros(casos):
    pedidos_corretos = 0
    campos_corretos = 0
    total_campos = 0
    falhas_de_api = 0

    for numero, caso in enumerate(casos, start=1):
        try:
            obtido = interpretar_roteiro(caso["m1"], caso["m2"], HOJE)
        except (RuntimeError, ValueError) as erro:
            print(f"{numero:2}. ⚠️  ERRO: {erro}")
            falhas_de_api += 1
            time.sleep(PAUSA)
            continue

        esperado = caso["esperado"]
        diferencas = comparar_roteiro(esperado, obtido)

        # Campos do caso: 4 por trecho esperado (origem, destino, inicio, fim) + orcamento e max_escalas.
        campos_do_caso = 4 * len(esperado["trechos"]) + 2
        total_campos += campos_do_caso
        if len(obtido.get("trechos") or []) == len(esperado["trechos"]):
            campos_corretos += campos_do_caso - len(diferencas)
        else:
            # Número de trechos errado: todos os campos de trecho contam como errados;
            # só orcamento e max_escalas podem estar certos.
            erros_fora_dos_trechos = len(diferencas) - 1
            campos_corretos += 2 - erros_fora_dos_trechos

        if diferencas:
            print(f"{numero:2}. ❌ {caso['m1']} | {caso['m2']}")
            for diferenca in diferencas:
                print(f"      {diferenca}")
        else:
            pedidos_corretos += 1
            print(f"{numero:2}. ✅ {caso['m1']} | {caso['m2']}")

        time.sleep(PAUSA)

    imprimir_resumo(pedidos_corretos, len(casos), campos_corretos, total_campos, falhas_de_api)


def imprimir_resumo(pedidos_corretos, total, campos_corretos, total_campos, falhas_de_api):
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
    if len(sys.argv) > 1:
        nome = sys.argv[1]
        if nome == "roteiro":
            avaliar_roteiros(CASOS_ROTEIRO)
        elif nome in CONJUNTOS:
            avaliar(CONJUNTOS[nome])
        else:
            print(f"Conjunto desconhecido: {nome}. Opções: {', '.join(CONJUNTOS)}, roteiro")
            sys.exit(1)
    else:
        escolha = input("Qual conjunto? (1 = teste, 2 = validação): ").strip()
        if escolha == "2":
            avaliar(CASOS_VALIDACAO)
        else:
            avaliar(CASOS)