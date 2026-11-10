# 🍌 Nana Travel

**Buscador de passagens de ida e volta com datas flexíveis e busca em linguagem natural.**

Você descreve a viagem do seu jeito, por exemplo *"SP pra Recife, ida entre 1 e 16 de dezembro, volta entre 13 e 23, até 1 escala, quero o mais barato possível"*, e o Nana Travel monta e ordena as combinações de ida e volta mais baratas.

> ⚠️ **Projeto de estudo e portfólio.** As passagens são **fictícias** e ficam em um arquivo CSV. O projeto ainda não consulta preços reais.

---

## Exemplo

```
Descreva a viagem que você quer: SP pra Recife, ida entre 1 e 16 de dezembro, volta entre 13 e 23 de dezembro, até 1 escala, quero o mais barato possível

Entendi assim:
  origem: São Paulo
  destino: Recife
  inicio_ida: 01/12/2026
  fim_ida: 16/12/2026
  inicio_volta: 13/12/2026
  fim_volta: 23/12/2026
  max_escalas: 1
  orcamento: None
  dias_min: None
  dias_max: None

Combinações encontradas: 11 (mostrando as 5 mais baratas)
A melhor opção custa R$ 400.00 a menos que a mais cara encontrada

1. Total: R$ 700.00 (melhor preço) | Duração: 1 dia(s)
   Ida:   15/12/2026 | Empresa C | São Paulo → Recife | R$ 500.00 | Escalas: 1
   Volta: 16/12/2026 | Empresa L | Recife → São Paulo | R$ 200.00 | Escalas: 0

2. Total: R$ 750.00 (+R$ 50.00 em relação à melhor) | Duração: 6 dia(s)
   ...
```

---

## O que ele faz

- **Datas flexíveis:** você informa uma janela para a ida e outra para a volta, e o programa testa todos os pares possíveis.
- **Regras de combinação:** a volta sempre depois da ida; orçamento total (opcional); máximo de escalas por trecho; duração mínima e máxima da viagem (opcional).
- **Resultado útil:** ordena pelo menor total e mostra a duração, os 5 melhores resultados e quanto cada opção custa a mais que a melhor.
- **Busca em linguagem natural:** um LLM transforma o pedido em critérios estruturados (JSON), e o programa mostra o que entendeu ("Entendi assim") antes de buscar.
- **Tolerância na digitação:** ignora acentos e maiúsculas ("sao paulo" = "São Paulo") e expande abreviações ("SP", "BH").

---

## Como funciona

```
pedido em português
      │
      ▼
interpretador.py ── LLM via API (Groq) ──► critérios em JSON
      │                                        │
      │                       mostra "Entendi assim" ao usuário
      ▼                                        ▼
comparador.py:  buscar()
   ├─ filtra as idas e as voltas (cidade, data, escalas)
   ├─ combina os pares (volta depois da ida, orçamento, duração)
   └─ ordena pelo total
      │
      ▼
as combinações mais baratas
```

### Decisões de projeto

- **IA só onde ela é necessária.** O LLM apenas **interpreta o texto**. Filtrar, somar preços e comparar datas é trabalho exato, feito por código convencional: mais confiável, rápido, gratuito e testável.
- **Camadas separadas.** `comparador.py` (lógica) não sabe que existe IA. `interpretador.py` (camada de IA) pode trocar de provedor sem mexer na busca. O terminal, os testes e o LLM usam a mesma função `buscar()`.
- **Transparência.** O programa mostra a interpretação do pedido antes de buscar. Se o modelo errar, o usuário percebe.
- **Regras explícitas no prompt.** Expressões vagas viram regras definidas: "começo do mês" = dias 1 a 15; "meio" = 11 a 20; "fim" = 16 ao último dia. Informações ausentes viram `null`, e o programa não inventa valores.
- **Segurança.** A chave da API fica em `.env`, fora do Git.

---

## Avaliação do interpretador (POC)

O critério de sucesso foi definido **antes** de medir: **≥ 90% dos pedidos com todos os campos corretos.**

| Versão do prompt | Conjunto de desenvolvimento (20 pedidos) | Observação |
|---|---|---|
| v1 | 16/20 (80%) | Regras ambíguas: períodos vagos pela metade, volta relativa somada à data errada, abreviações não expandidas |
| v2 | 18/20 (90%) | Regras explícitas e definição de quinzenas |
| v2 + duração | 20/20 e 19/20 | Duas rodadas, para medir a estabilidade |

| Conjunto de **validação** (11 pedidos novos, nunca usados para ajustar o prompt) | Resultado |
|---|---|
| Rodada 1 | 9/11 (82%) |
| Rodada 2 | 9/11 (82%) |

**Conclusão:** o prompt atinge 95–100% nos casos usados para desenvolvê-lo, mas **cerca de 82% em pedidos novos**. A meta de 90% **não foi atingida na validação**, e a diferença indica **sobreajuste** do prompt ao conjunto de desenvolvimento.

**Erros encontrados:**
- **Sistemático:** com datas fixas de ida e volta, o modelo deduz uma duração (ex.: 7 dias). Isso diverge da especificação, mas não muda o resultado da busca.
- **Instável:** às vezes o "fim do mês" começa no dia 21 em vez do dia 16, mesmo com temperatura 0.

Um próximo ciclo de melhoria exigiria um **novo** conjunto de validação, para não ajustar o prompt usando a própria validação.

---

## Como rodar

**Requisitos:** Python 3.10 ou superior e uma chave gratuita da [Groq](https://console.groq.com).

```bash
# 1. Instalar as dependências
python -m pip install -r requirements.txt

# 2. Configurar a chave: copie o .env.example para .env e coloque a sua chave
#    GROQ_API_KEY=sua_chave_aqui

# 3a. Busca em linguagem natural
python interpretador.py

# 3b. Busca pelo terminal, pergunta por pergunta (não usa IA)
python comparador.py

# 4. Testes automatizados da lógica de busca
python -m pytest -v

# 5. Avaliação de acurácia do interpretador (usa a API; leva alguns minutos)
python avaliar_interpretador.py
```

---

## Estrutura

| Arquivo | Papel |
|---|---|
| `comparador.py` | Lógica de busca: carrega o CSV, filtra, combina, ordena e exibe |
| `interpretador.py` | Busca em linguagem natural: prompt, chamada à API com retry e conversão dos critérios |
| `passagens.csv` | Passagens fictícias (o "contrato de dados") |
| `test_comparador.py` | Testes automatizados da lógica (pytest) |
| `avaliar_interpretador.py` | Avaliação de acurácia: conjuntos de desenvolvimento e validação |
| `testar_api.py`, `listar_modelos.py` | Diagnóstico da conexão com a API |

---

## Limitações conhecidas

- Os dados são **fictícios**; não há integração com fontes reais de preços.
- Ida e volta são tratadas como **duas passagens só de ida**. Na vida real, a passagem de ida e volta comprada junto pode sair mais barata.
- Só há roteiros de ida e volta (sem viagens por várias cidades).
- O interpretador acerta **cerca de 82%** dos pedidos novos (veja a avaliação).
- O plano gratuito da API tem limite de tokens por minuto, e por isso a avaliação usa pausas entre os pedidos.
- Os testes da lógica dependem do conteúdo de `passagens.csv`.

## Próximos passos

- Viagens com várias cidades (a viagem como uma lista de trechos).
- Nova iteração do prompt, com um conjunto de validação novo.
- Fonte de dados reais de passagens, respeitando os termos de uso.
- Interface visual.

## Sobre o desenvolvimento

Projeto desenvolvido como trilha de aprendizado em Python, com o Claude (IA da Anthropic) como mentor: a IA explicou os conceitos e forneceu parte do código; eu apliquei, executei, depurei os erros, tomei as decisões de especificação (regras de datas, escolha do provedor gratuito, critérios de sucesso) e conduzi a avaliação da POC.