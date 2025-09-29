# database/data_manager.py
import os
import sys
import uuid
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore


# ========================
# Caminho do Firebase Key
# ========================
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ========================
# Inicializa Firebase
# ========================
cred_path = resource_path("config/firebase_key.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()


# ========================
# Adicionar transação
# ========================
def add_transaction(transaction: dict) -> str:
    """
    Adiciona uma transação ao Firebase.
    Retorna o ID gerado.
    """

    # Preencher valores padrão
    transaction.setdefault("desc", "Sem descrição")
    transaction.setdefault("amount", 0.0)
    transaction.setdefault("type", "receita")
    transaction.setdefault("date", datetime.now().strftime("%Y-%m-%d"))
    transaction.setdefault("recurrence", "Única")
    transaction.setdefault("currency", "BRL")
    transaction.setdefault("category", "Outros")

    # Gera ID único
    temp_id = str(uuid.uuid4())
    transaction.setdefault("id", temp_id)

    # Salva no Firebase
    doc_ref = db.collection("transactions").add(transaction)
    firebase_id = doc_ref[1].id

    # Atualiza campo id com o ID real do Firebase
    db.collection("transactions").document(firebase_id).update({"id": firebase_id})

    return firebase_id


# ========================
# Editar transação
# ========================
def edit_transaction(doc_id: str, new_data: dict):
    db.collection("transactions").document(doc_id).update(new_data)


# ========================
# Deletar transação
# ========================
def delete_transaction(doc_id: str):
    db.collection("transactions").document(doc_id).delete()


# ========================
# Carregar transações
# ========================
def load_transactions(user_id: str = None):
    docs = list(db.collection("transactions").stream())
    transactions = [doc.to_dict() for doc in docs]

    if user_id:
        transactions = [t for t in transactions if t.get("user_id") == user_id]

    return transactions


# ========================
# Exportar CSV
# ========================
def export_csv(path: str, user_id: str = None):
    import csv
    transactions = load_transactions(user_id)
    if not transactions:
        print("Nenhuma transação para exportar.")
        return
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=transactions[0].keys())
        writer.writeheader()
        for t in transactions:
            writer.writerow(t)
    print(f"Transações exportadas para {path} com sucesso.")


# ========================
# Filtro
# ========================
def filter_transactions(transactions, start_date=None, end_date=None, tipo=None):
    filtered = transactions
    if start_date:
        filtered = [t for t in filtered if t.get("date") >= start_date]
    if end_date:
        filtered = [t for t in filtered if t.get("date") <= end_date]
    if tipo:
        filtered = [t for t in filtered if t.get("type") == tipo]
    return filtered
