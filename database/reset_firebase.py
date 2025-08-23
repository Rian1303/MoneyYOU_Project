import firebase_admin
from firebase_admin import credentials, firestore

# Carregar credenciais
cred = credentials.Certificate("config/firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# Referência para a coleção
transactions_ref = db.collection("transactions")

# Pega todos os documentos
docs = transactions_ref.stream()

# Deleta um por um
for doc in docs:
    doc.reference.delete()

print("🔥 Todas as transações foram apagadas do Firebase.")
