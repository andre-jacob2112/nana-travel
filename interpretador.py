import os
import json
from datetime import date

import requests
from dotenv import load_dotenv

from comparador import carregar_passagens, buscar, exibir_combinacoes, converter_data

load_dotenv()
CHAVE = os.getenv("GROQ_API_KEY")
MODELO = "openai/gpt-oss-20b"
ENDERECO = "https://api.groq.com/openai/v1/chat/completions"

CAMPOS = ["origem", "destino", "inicio_ida", "fim_ida",
          "inicio_volta", "fim_volta", "orcamento", "max_escalas"]


def montar_instrucoes(hoje):
    hoje_texto = hoje.strftime("%d/%m/%Y")
    return f"""Você extrai critérios de busca de passagens aéreas de um pedido em português.
Hoje é {hoje_texto}. Datas sem ano referem-se à próxima ocorrência a partir de hoje.

Responda APENAS com um objeto JSON, sem nenhum texto antes ou depois, com estas chaves:
- "origem" e "destino": nomes das cidades
- "inicio_ida", "fim_ida", "inicio_volta", "fim_volta": datas no formato dd/mm/aaaa
- "orcamento": número, o valor total de ida e volta em reais
- "max_escalas": número inteiro

Regras:
- Cada período (ida e volta) tem SEMPRE uma data de início e uma data de fim. Mesmo que o pedido descreva o período de forma vaga, preencha as duas.
- "começo do mês" = dias 1 a 15; "meio do mês" = dias 11 a 20; "fim do mês" ou "final do mês" = dia 16 até o último dia do mês.
- Volta relativa (ex.: "voltar 3 dias depois"): some a duração às DUAS datas da ida. inicio_volta = inicio_ida + duração; fim_volta = fim_ida + duração.
- Escreva as cidades sempre pelo nome completo, nunca abreviado (ex.: "SP" → "São Paulo", "BH" → "Belo Horizonte").
- "voo direto" ou "sem escalas" = 0.
- Se uma informação não aparecer no pedido, use null."""


def chamar_llm(instrucoes, pedido):
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
    if resposta.status_code != 200:
        raise RuntimeError(f"Erro da API ({resposta.status_code}): {resposta.text}")
    return resposta.json()["choices"][0]["message"]["content"]


def limpar_json(texto):
    texto = texto.strip()
    texto = texto.removeprefix("```json").removeprefix("```")
    texto = texto.removesuffix("```")
    return texto.strip()


def interpretar_pedido(pedido, hoje):
    texto = chamar_llm(montar_instrucoes(hoje), pedido)
    return json.loads(limpar_json(texto))


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
    for campo in CAMPOS:
        print(f"  {campo}: {criterios.get(campo)}")

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
        float(criterios["orcamento"]),
        int(criterios["max_escalas"])
    )
    exibir_combinacoes(combinacoes, 5)


if __name__ == "__main__":
    executar_linguagem_natural()