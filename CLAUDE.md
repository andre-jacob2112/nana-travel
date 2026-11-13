# Nana Travel: instruções para o Claude Code

## Contexto
Comparador de passagens aéreas em Python, projeto de portfólio de um programador iniciante.
O autor precisa entender e saber explicar cada mudança. Responda sempre em português.

## Arquivos
- `comparador.py`: lógica de busca (`buscar`, `buscar_roteiro`, `montar_roteiros`) e entrada pelo terminal (`executar_terminal`).
- `interpretador.py`: busca em linguagem natural via LLM (Groq, modelo `openai/gpt-oss-20b`).
- `passagens.csv`: ofertas fictícias, separador `;`, codificação UTF-8.
- `test_comparador.py`: testes com pytest.
- `avaliar_interpretador.py`: avaliação de acurácia do interpretador (faz chamadas pagas por cota à API).

## Comandos
- Testes: `python -m pytest -v`
- Terminal: `python comparador.py`
- Linguagem natural: `python interpretador.py`

## Convenções
- Chaves das ofertas: `"Companhia"`, `"Origem"`, `"Destino"`, `"Data"` (dd/mm/aaaa), `"Preço"`, `"escalas"`.
- Chaves dos resultados: `"Trechos"` / `"Ida"` / `"Volta"`, `"Total"`, `"Dias"`.
- Orçamento `None` significa sem limite.
- Comparações de cidades sempre usam `normalizar` (sem acento e em minúsculas).
- A lógica (`buscar...`) não usa `input` nem `print`; a entrada e a saída ficam nas funções de terminal.

## Como trabalhar
1. Antes de editar, explique o plano em poucas linhas.
2. Depois de editar, explique cada bloco alterado: o que faz e por quê, com um exemplo do que daria errado sem ele.
3. Rode `python -m pytest -v` depois de cada mudança e informe quantos testes passaram.
4. Nunca altere um valor esperado de teste só para fazer o teste passar.
5. Não altere o prompt do `interpretador.py` sem pedido explícito: toda mudança no prompt exige nova avaliação.
6. Não rode `avaliar_interpretador.py` sem pedido explícito (consome a cota da API).
7. Não faça commit nem push: o autor faz isso. Sugira a mensagem do commit.
8. Ao terminar, faça um relatório curto: arquivos alterados, funções criadas ou mudadas, resultado dos testes e o que ficou pendente.

## Segurança
- Nunca leia, exiba ou edite o `.env`. A chave da API fica só nele.
- Nunca escreva uma chave real em nenhum arquivo. Em exemplos, use `gsk_***`.
- Não rode comandos de terminal que mostrem o conteúdo do `.env`.