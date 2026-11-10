# Exercício 1: filtrar uma lista de preços
precos = [850, 620, 1100]
precos[1] = 590
precos[2] = 980
precos.append(720)

orcamento = 590
max_escalas = 1

menor_preco = min(precos)

precos_no_orcamento = []

for preco in precos:
    if preco <= orcamento:
        precos_no_orcamento.append(preco)

print(precos_no_orcamento)

# Exercício 2: avaliar preço e escalas de uma passagem
passagem = {
    "Companhia": "Companhia Exemplo",
    "Preço": 590,
    "escalas": 1
}

print(passagem["Preço"])

passagem["Preço"] = 550
passagem["escalas"] = 2

if passagem["Preço"] <= orcamento and passagem["escalas"] <= max_escalas:
    print("Esta passagem atende aos critérios")
else:
    print("Esta passagem não atende a um ou aos dois critérios")

#Exercício 3: representar várias passagens

passagens = [
    {"Companhia": "Empresa A", "Preço": 550, "escalas": 0},
    {"Companhia": "Empresa B", "Preço": 720, "escalas": 1},
    {"Companhia": "Empresa C", "Preço": 500, "escalas": 1}
]

ofertas_validas = []

for oferta in passagens:
    if oferta["Preço"] <= orcamento and oferta["escalas"] <= max_escalas:
        ofertas_validas.append(oferta)

print(ofertas_validas)

def obter_preco(oferta):
    return oferta["Preço"]

preco_empresa_c = obter_preco(passagens[2])
print(preco_empresa_c)

ofertas_ordenadas = sorted(ofertas_validas, key=obter_preco)
print(ofertas_ordenadas)