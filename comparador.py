# Nana Travel: lógica de busca

import unicodedata
import csv
import difflib
from datetime import datetime


def ler_orcamento():
    while True:
        texto = input("Qual é o seu orçamento total? Deixe em branco para não ter limite: ").strip()
        if texto == "":
            return None
        try:
            orcamento = float(texto.replace(",", "."))
            if orcamento <= 0:
                print("O orçamento deve ser maior que zero")
            else:
                return orcamento
        except ValueError:
            print("Digite um número válido")


def ler_max_escalas():
    while True:
        try:
            max_escalas = int(input("Qual é o máximo de escalas por trecho? "))
            if max_escalas < 0:
                print("O número de escalas não pode ser negativo")
            else:
                return max_escalas
        except ValueError:
            print("Digite um número inteiro válido")


def ler_quantidade_trechos():
    while True:
        try:
            quantidade = int(input("Quantos trechos tem a viagem? "))
            if quantidade < 2:
                print("Uma viagem com vários trechos precisa de pelo menos 2")
            else:
                return quantidade
        except ValueError:
            print("Digite um número inteiro válido")


def converter_data(texto):
    return datetime.strptime(texto, "%d/%m/%Y").date()


def normalizar(texto):
    decomposto = unicodedata.normalize("NFD", texto)
    resultado = ""
    for caractere in decomposto:
        if not unicodedata.combining(caractere):
            resultado += caractere
    return resultado.lower().strip()


def carregar_passagens(caminho):
    passagens = []
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")
        for linha in leitor:
            oferta = {
                "Companhia": linha["Companhia"],
                "Origem": linha["Origem"],
                "Destino": linha["Destino"],
                "Data": linha["Data"],
                "Preço": float(linha["Preço"].replace(",", ".")),
                "escalas": int(linha["escalas"])
            }
            passagens.append(oferta)
    return passagens


def listar_cidades(passagens):
    cidades = {}
    for oferta in passagens:
        cidades[normalizar(oferta["Origem"])] = oferta["Origem"]
        cidades[normalizar(oferta["Destino"])] = oferta["Destino"]
    return cidades


def encontrar_cidade(nome, cidades):
    return cidades.get(normalizar(nome))


def sugerir_cidade(nome, cidades):
    parecidas = difflib.get_close_matches(normalizar(nome), list(cidades), n=1, cutoff=0.6)
    if parecidas:
        return cidades[parecidas[0]]
    return None


def cidades_desconhecidas(origem, destino, cidades):
    desconhecidas = []
    for nome in [origem, destino]:
        if nome is not None and encontrar_cidade(nome, cidades) is None:
            desconhecidas.append(nome)
    return desconhecidas


def avisar_cidade_desconhecida(nome, cidades):
    sugestao = sugerir_cidade(nome, cidades)
    if sugestao is not None:
        print(f"Não encontrei a cidade \"{nome}\". Você quis dizer {sugestao}?")
    else:
        disponiveis = ", ".join(sorted(cidades.values()))
        print(f"Não encontrei a cidade \"{nome}\". Cidades disponíveis: {disponiveis}")


def ler_cidade(pergunta, cidades):
    while True:
        nome = input(pergunta).strip()
        cidade = encontrar_cidade(nome, cidades)
        if cidade is not None:
            return cidade
        sugestao = sugerir_cidade(nome, cidades)
        if sugestao is not None:
            resposta = input(f"Você quis dizer {sugestao}? (s/n) ").strip().lower()
            if resposta == "s":
                return sugestao
        disponiveis = ", ".join(sorted(cidades.values()))
        print(f"Cidades disponíveis: {disponiveis}")


def ler_data(mensagem):
    while True:
        try:
            data = converter_data(input(mensagem).strip())
            return data
        except ValueError:
            print("Digite uma data válida no formato dd/mm/aaaa")


def ler_periodo(trecho):
    while True:
        data_inicio = ler_data(f"{trecho} - primeira data possível (dd/mm/aaaa): ")
        data_fim = ler_data(f"{trecho} - última data possível (dd/mm/aaaa): ")
        if data_fim < data_inicio:
            print("A última data não pode ser anterior à primeira")
        else:
            return data_inicio, data_fim


def atende_criterios(oferta, origem, destino, data_inicio, data_fim, max_escalas):
    origem_valida = normalizar(oferta["Origem"]) == normalizar(origem)
    destino_valido = normalizar(oferta["Destino"]) == normalizar(destino)
    data_valida = data_inicio <= converter_data(oferta["Data"]) <= data_fim
    escalas_validas = oferta["escalas"] <= max_escalas
    return origem_valida and destino_valido and data_valida and escalas_validas


def filtrar_passagens(passagens, origem, destino, data_inicio, data_fim, max_escalas):
    ofertas_validas = []

    for oferta in passagens:
        if atende_criterios(oferta, origem, destino, data_inicio, data_fim, max_escalas):
            ofertas_validas.append(oferta)

    return ofertas_validas


def obter_total(combinacao):
    return combinacao["Total"]


def somar_precos(ofertas):
    total = 0
    for oferta in ofertas:
        total += oferta["Preço"]
    return total


def montar_roteiros(passagens, trechos, orcamento, max_escalas):
    roteiros = [[]]

    for trecho in trechos:
        candidatos = filtrar_passagens(passagens, trecho["origem"], trecho["destino"],
                                       trecho["inicio"], trecho["fim"], max_escalas)
        novos_roteiros = []
        for roteiro in roteiros:
            for oferta in candidatos:
                if roteiro and converter_data(oferta["Data"]) <= converter_data(roteiro[-1]["Data"]):
                    continue
                total = somar_precos(roteiro) + oferta["Preço"]
                if orcamento is not None and total > orcamento:
                    continue
                novos_roteiros.append(roteiro + [oferta])
        roteiros = novos_roteiros

    return roteiros


def buscar_roteiro(passagens, trechos, orcamento, max_escalas, dias_min=None, dias_max=None):
    resultados = []

    for roteiro in montar_roteiros(passagens, trechos, orcamento, max_escalas):
        dias = (converter_data(roteiro[-1]["Data"]) - converter_data(roteiro[0]["Data"])).days
        duracao_valida = (dias_min is None or dias >= dias_min) and (dias_max is None or dias <= dias_max)
        if duracao_valida:
            resultados.append({"Trechos": roteiro, "Total": somar_precos(roteiro), "Dias": dias})

    resultados.sort(key=obter_total)
    return resultados


def buscar(passagens, origem, destino, inicio_ida, fim_ida, inicio_volta, fim_volta, orcamento, max_escalas, dias_min=None, dias_max=None):
    trechos = [
        {"origem": origem, "destino": destino, "inicio": inicio_ida, "fim": fim_ida},
        {"origem": destino, "destino": origem, "inicio": inicio_volta, "fim": fim_volta}
    ]
    roteiros = buscar_roteiro(passagens, trechos, orcamento, max_escalas, dias_min, dias_max)

    combinacoes = []
    for roteiro in roteiros:
        combinacoes.append({
            "Ida": roteiro["Trechos"][0],
            "Volta": roteiro["Trechos"][1],
            "Total": roteiro["Total"],
            "Dias": roteiro["Dias"]
        })
    return combinacoes


def formatar_trecho(oferta):
    return f"{oferta['Data']} | {oferta['Companhia']} | {oferta['Origem']} → {oferta['Destino']} | R$ {oferta['Preço']:.2f} | Escalas: {oferta['escalas']}"


def exibir_resumo(resultados, limite):
    if len(resultados) == 1:
        print("Combinação encontrada: 1")
    else:
        quantidade = min(limite, len(resultados))
        economia = resultados[-1]["Total"] - resultados[0]["Total"]
        print(f"Combinações encontradas: {len(resultados)} (mostrando as {quantidade} mais baratas)")
        print(f"A melhor opção custa R$ {economia:.2f} a menos que a mais cara encontrada")
    print()


def descrever_preco(resultado, melhor):
    diferenca = resultado["Total"] - melhor["Total"]
    if diferenca == 0:
        return "melhor preço"
    return f"+R$ {diferenca:.2f} em relação à melhor"


def exibir_combinacoes(combinacoes, limite):
    if not combinacoes:
        print("Nenhuma combinação atende aos critérios")
        return

    exibir_resumo(combinacoes, limite)
    melhor = combinacoes[0]
    for numero, combinacao in enumerate(combinacoes[:limite], start=1):
        print(f"{numero}. Total: R$ {combinacao['Total']:.2f} ({descrever_preco(combinacao, melhor)}) | Duração: {combinacao['Dias']} dia(s)")
        print(f"   Ida:   {formatar_trecho(combinacao['Ida'])}")
        print(f"   Volta: {formatar_trecho(combinacao['Volta'])}")
        print()


def exibir_roteiros(roteiros, limite):
    if not roteiros:
        print("Nenhum roteiro atende aos critérios")
        return

    exibir_resumo(roteiros, limite)
    melhor = roteiros[0]
    for numero, roteiro in enumerate(roteiros[:limite], start=1):
        print(f"{numero}. Total: R$ {roteiro['Total']:.2f} ({descrever_preco(roteiro, melhor)}) | Duração: {roteiro['Dias']} dia(s)")
        for posicao, oferta in enumerate(roteiro["Trechos"], start=1):
            print(f"   Trecho {posicao}: {formatar_trecho(oferta)}")
        print()


def executar_ida_e_volta(passagens):
    cidades = listar_cidades(passagens)
    origem = ler_cidade("Origem: ", cidades)
    destino = ler_cidade("Destino: ", cidades)
    inicio_ida, fim_ida = ler_periodo("Ida")
    inicio_volta, fim_volta = ler_periodo("Volta")
    orcamento = ler_orcamento()
    max_escalas = ler_max_escalas()

    combinacoes = buscar(passagens, origem, destino, inicio_ida, fim_ida, inicio_volta, fim_volta, orcamento, max_escalas)
    exibir_combinacoes(combinacoes, 5)


def executar_varios_trechos(passagens):
    cidades = listar_cidades(passagens)
    quantidade = ler_quantidade_trechos()
    trechos = []
    for numero in range(1, quantidade + 1):
        print(f"\nTrecho {numero}")
        origem = ler_cidade("Origem: ", cidades)
        destino = ler_cidade("Destino: ", cidades)
        inicio, fim = ler_periodo(f"Trecho {numero}")
        trechos.append({"origem": origem, "destino": destino, "inicio": inicio, "fim": fim})

    print()
    orcamento = ler_orcamento()
    max_escalas = ler_max_escalas()

    roteiros = buscar_roteiro(passagens, trechos, orcamento, max_escalas)
    exibir_roteiros(roteiros, 5)


def executar_terminal():
    passagens = carregar_passagens("passagens.csv")
    tipo = input("Tipo de viagem (1 = ida e volta, 2 = vários trechos): ").strip()
    if tipo == "2":
        executar_varios_trechos(passagens)
    else:
        executar_ida_e_volta(passagens)


if __name__ == "__main__":
    executar_terminal()