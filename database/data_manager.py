import sqlite3
from pathlib import Path
import sys
import os
from datetime import datetime

# ========================
# Caminho correto para arquivos
# ========================
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ========================
# Detecta se está empacotado
# ========================
IS_PACKAGED = getattr(sys, 'frozen', False)
USE_FIREBASE = True  # Sempre usamos Firebase como principal

# ========================
# Configuração Firebase
# ========================
import firebase_admin
from firebase_admin import credentials, firestore

cred_path = resource_path("config/firebase_key.json")
cred = credentials.Certificate(cred_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ========================
# Caminho SQLite (backup)
# ========================
DB_PATH = Path(__file__).parent / "db.sqlite"

def connect():
    return sqlite3.connect(DB_PATH, timeout=10)

# ========================
# Adicionar transação
# ========================
def add_transaction(transaction):
    # Preencher valores padrão
    transaction.setdefault("desc", "Sem descrição")
    transaction.setdefault("valor", 0.0)
    transaction.setdefault("tipo", "receita")
    transaction.setdefault("data", datetime.now().strftime("%Y-%m-%d"))
    transaction.setdefault("tipo_recorrencia", 0)

    # 🔥 Firebase (fonte principal)
    doc_ref = db.collection("transactions").add(transaction)

    # 💾 SQLite (backup local)
    try:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, desc, valor, tipo, data, tipo_recorrencia)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                transaction['user_id'],
                transaction['desc'],
                transaction['valor'],
                transaction['tipo'],
                transaction['data'],
                transaction['tipo_recorrencia']
            ))
            conn.commit()
    except Exception as e:
        print(f"[SQLite Backup] Erro ao adicionar transação: {e}")

    return doc_ref[1].id  # retorna ID Firebase

# ========================
# Editar transação (Firebase)
# ========================
def edit_transaction(doc_id, new_data):
    doc_ref = db.collection("transactions").document(doc_id)
    doc_ref.update(new_data)
    # Não atualizamos SQLite, pois é só backup

# ========================
# Deletar transação (Firebase)
# ========================
def delete_transaction(doc_id):
    db.collection("transactions").document(doc_id).delete()
    # SQLite permanece intacto

# ========================
# Carregar transações (apenas Firebase)
# ========================
def load_transactions(user_id=None):
    docs = list(db.collection("transactions").stream())
    transactions = [doc.to_dict() for doc in docs]
    if user_id:
        transactions = [t for t in transactions if t.get("user_id") == user_id]
    for t, doc in zip(transactions, docs):
        t["id"] = doc.id
    return transactions

# ========================
# Exportar CSV (Firebase)
# ========================
def export_csv(path, user_id=None):
    import csv
    transactions = load_transactions(user_id)
    if not transactions:
        print("Nenhuma transação para exportar.")
        return
    with open(path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=transactions[0].keys())
        writer.writeheader()
        for t in transactions:
            writer.writerow(t)
    print(f"Transações exportadas para {path} com sucesso.")

def filter_transactions(transactions, start_date=None, end_date=None, tipo=None):
        filtered = transactions
        if start_date:
            filtered = [t for t in filtered if t.get("data") >= start_date]
        if end_date:
            filtered = [t for t in filtered if t.get("data") <= end_date]
        if tipo:
            filtered = [t for t in filtered if t.get("tipo") == tipo]
        return filtered