# Comparador de passagens

import unicodedata
import csv
from datetime import datetime

def ler_orcamento():
    while True:
        try:
            orcamento = float(input("Qual é o seu orçamento total (ida + volta)? ").replace(",", "."))
            if orcamento <= 0:
                print("O orçamento deve ser maior que zero")
            else:
                return orcamento
        except ValueError:
            print("Digite um número válido")


def ler_max_escalas():
    while True:
        try:
            max_escalas = int(input("Qual é o máximo de escalas? "))
            if max_escalas < 0:
                print("O número de escalas não pode ser negativo")
            else:
                return max_escalas
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
    return resultado.lower()


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


def combinar_ida_volta(idas, voltas, orcamento):
    combinacoes = []

    for ida in idas:
        for volta in voltas:
            data_ida = converter_data(ida["Data"])
            data_volta = converter_data(volta["Data"])
            total = ida["Preço"] + volta["Preço"]
            dias = (data_volta - data_ida).days
            if data_volta > data_ida and total <= orcamento:
                combinacoes.append({"Ida": ida, "Volta": volta, "Total": total, "Dias": dias})

    return combinacoes


def buscar(passagens, origem, destino, inicio_ida, fim_ida, inicio_volta, fim_volta, orcamento, max_escalas):
    idas = filtrar_passagens(passagens, origem, destino, inicio_ida, fim_ida, max_escalas)
    voltas = filtrar_passagens(passagens, destino, origem, inicio_volta, fim_volta, max_escalas)
    combinacoes = combinar_ida_volta(idas, voltas, orcamento)
    combinacoes.sort(key=obter_total)
    return combinacoes


def formatar_trecho(oferta):
    return f"{oferta['Data']} | {oferta['Companhia']} | {oferta['Origem']} → {oferta['Destino']} | R$ {oferta['Preço']:.2f} | Escalas: {oferta['escalas']}"


def exibir_combinacoes(combinacoes, limite):
    if combinacoes:
        melhor = combinacoes[0]
        mais_cara = combinacoes[-1]
        economia = mais_cara["Total"] - melhor["Total"]
        quantidade = min(limite, len(combinacoes))

        print(f"Combinações encontradas: {len(combinacoes)} (mostrando as {quantidade} mais baratas)")
        print(f"A melhor opção custa R$ {economia:.2f} a menos que a mais cara encontrada")
        print()

        for numero, combinacao in enumerate(combinacoes[:limite], start=1):
            diferenca = combinacao["Total"] - melhor["Total"]
            if diferenca == 0:
                comparacao = "melhor preço"
            else:
                comparacao = f"+R$ {diferenca:.2f} em relação à melhor"

            print(f"{numero}. Total: R$ {combinacao['Total']:.2f} ({comparacao}) | Duração: {combinacao['Dias']} dia(s)")
            print(f"   Ida:   {formatar_trecho(combinacao['Ida'])}")
            print(f"   Volta: {formatar_trecho(combinacao['Volta'])}")
            print()
    else:
        print("Nenhuma combinação atende aos critérios")


def executar_terminal():
    passagens = carregar_passagens("passagens.csv")

    origem = input("Origem: ").strip()
    destino = input("Destino: ").strip()
    inicio_ida, fim_ida = ler_periodo("Ida")
    inicio_volta, fim_volta = ler_periodo("Volta")
    orcamento = ler_orcamento()
    max_escalas = ler_max_escalas()

    combinacoes = buscar(passagens, origem, destino, inicio_ida, fim_ida, inicio_volta, fim_volta, orcamento, max_escalas)
    exibir_combinacoes(combinacoes, 5)


if __name__ == "__main__":
    executar_terminal()