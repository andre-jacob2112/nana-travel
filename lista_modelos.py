import os
import requests
from dotenv import load_dotenv

load_dotenv()
chave = os.getenv("GROQ_API_KEY")

resposta = requests.get(
    "https://api.groq.com/openai/v1/models",
    headers={"Authorization": f"Bearer {chave}"},
    timeout=30
)

for modelo in resposta.json()["data"]:
    print(modelo["id"])