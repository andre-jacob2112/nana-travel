import os
import requests
from dotenv import load_dotenv

load_dotenv()
chave = os.getenv("GROQ_API_KEY")

resposta = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {chave}"},
    json={
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": "Responda apenas: a conexão funcionou!"}]
    },
    timeout=30
)

print("Status:", resposta.status_code)
dados = resposta.json()
print(dados["choices"][0]["message"]["content"])