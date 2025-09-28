import os
from openai import OpenAI
from dotenv import load_dotenv

# carrega a chave
load_dotenv("config/openai_key.env")
print("Chave carregada:", os.getenv("OPENAI_API_KEY")[:10], "...")

# inicializa cliente
client = OpenAI()

# faz um teste de requisição
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Diga apenas: teste ok"}]
)

print("Resposta:", resp.choices[0].message.content)
