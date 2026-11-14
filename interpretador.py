import os
import json
import time
from datetime import date

import requests
from dotenv import load_dotenv

from comparador import (carregar_passagens, buscar, exibir_combinacoes, converter_data,
                        listar_cidades, cidades_desconhecidas, avisar_cidade_desconhecida)

load_dotenv()
CHAVE = os.getenv("GROQ_API_KEY")
MODELO = "openai/gpt-oss-20b"
ENDERECO = "https://api.groq.com/openai/v1/chat/completions"

CAMPOS = ["origem", "destino", "inicio_ida", "fim_ida",
          "inicio_volta", "fim_volta", "max_escalas"]
CAMPOS_OPCIONAIS = ["orcamento", "dias_min", "dias_max"]


def montar_instrucoes(hoje):
    hoje_texto = hoje.strftime("%d/%m/%Y")
    return f"""Você extrai critérios de busca de passagens aéreas de um pedido em português.
Hoje é {hoje_texto}. Datas sem ano referem-se à próxima ocorrência a partir de hoje.

Responda APENAS com um objeto JSON, sem nenhum texto antes ou depois, com estas chaves:
- "origem" e "destino": nomes das cidades
- "inicio_ida", "fim_ida", "inicio_volta", "fim_volta": datas no formato dd/mm/aaaa
- "orcamento": número, o valor total de ida e volta em reais
- "max_escalas": número inteiro
- "dias_min" e "dias_max": números inteiros, a duração mínima e máxima da viagem em dias

Regras:
- Cada período (ida e volta) tem SEMPRE uma data de início e uma data de fim. Mesmo que o pedido descreva o período de forma vaga, preencha as duas.
- "começo do mês" = dias 1 a 15; "meio do mês" = dias 11 a 20; "fim do mês" ou "final do mês" = dia 16 até o último dia do mês.
- Volta relativa (ex.: "voltar 3 dias depois", "ficar uma semana"): some a duração às DUAS datas da ida. inicio_volta = inicio_ida + duração; fim_volta = fim_ida + duração.
- Duração da viagem: se o pedido indicar quanto tempo a pessoa quer ficar, preencha "dias_min" e "dias_max". Duração exata (ex.: "uma semana", "3 dias depois") = os dois iguais. Faixa (ex.: "entre 5 e 7 dias") = 5 e 7. Sem duração no pedido = null nos dois.
- Escreva as cidades sempre pelo nome completo, nunca abreviado (ex.: "SP" → "São Paulo", "BH" → "Belo Horizonte").
- "voo direto" ou "sem escalas" = 0.
- Se uma informação não aparecer no pedido, use null."""


def chamar_llm(instrucoes, pedido):
    for tentativa in range(3):
        resposta = requests.post(
            ENDERECO,
            headers={"Authorization": f"Bearer {CHAVE}"},
            json={
                "model": MODELO,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": instrucoes},
                    {"role": "user", "content": pedido}
                ]
            },
            timeout=30
        )
        if resposta.status_code == 429:
            time.sleep(20)
            continue
        if resposta.status_code != 200:
            raise RuntimeError(f"Erro da API ({resposta.status_code}): {resposta.text}")
        return resposta.json()["choices"][0]["message"]["content"]

    raise RuntimeError("Limite de uso da API atingido 3 vezes seguidas. Tente de novo em alguns minutos.")


def limpar_json(texto):
    texto = texto.strip()
    texto = texto.removeprefix("```json").removeprefix("```")
    texto = texto.removesuffix("```")
    return texto.strip()


def interpretar_pedido(pedido, hoje):
    texto = chamar_llm(montar_instrucoes(hoje), pedido)
    return json.loads(limpar_json(texto))


def converter_inteiro(valor):
    if valor is None:
        return None
    return int(valor)


def converter_decimal(valor):
    if valor is None:
        return None
    return float(valor)


def campos_faltando(criterios):
    faltando = []
    for campo in CAMPOS:
        if criterios.get(campo) is None:
            faltando.append(campo)
    return faltando


def executar_linguagem_natural():
    passagens = carregar_passagens("passagens.csv")
    pedido = input("Descreva a viagem que você quer: ")

    try:
        criterios = interpretar_pedido(pedido, date.today())
    except (RuntimeError, ValueError) as erro:
        print("Não consegui interpretar o pedido:", erro)
        return

    print("\nEntendi assim:")
    for campo in CAMPOS + CAMPOS_OPCIONAIS:
        print(f"  {campo}: {criterios.get(campo)}")

    cidades = listar_cidades(passagens)
    desconhecidas = cidades_desconhecidas(criterios.get("origem"), criterios.get("destino"), cidades)
    if desconhecidas:
        for nome in desconhecidas:
            print()
            avisar_cidade_desconhecida(nome, cidades)
        return

    faltando = campos_faltando(criterios)
    if faltando:
        print("\nFaltou informar:", ", ".join(faltando))
        return

    print()
    combinacoes = buscar(
        passagens,
        criterios["origem"],
        criterios["destino"],
        converter_data(criterios["inicio_ida"]),
        converter_data(criterios["fim_ida"]),
        converter_data(criterios["inicio_volta"]),
        converter_data(criterios["fim_volta"]),
        converter_decimal(criterios.get("orcamento")),
        int(criterios["max_escalas"]),
        converter_inteiro(criterios.get("dias_min")),
        converter_inteiro(criterios.get("dias_max"))
    )
    exibir_combinacoes(combinacoes, 5)


if __name__ == "__main__":
    executar_linguagem_natural()