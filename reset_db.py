import sqlite3
import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Caminho para o arquivo JSON da chave Firebase
FIREBASE_KEY_PATH = resource_path("config/firebase_key.json")

# Inicializa Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Caminho para banco SQLite
DB_PATH = resource_path("database/db.sqlite")

def reset_sqlite_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Apaga dados da tabela users e transactions
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM transactions")

    # Opcional: reinicia o contador AUTOINCREMENT
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")

    conn.commit()
    conn.close()
    print("SQLite: tabelas 'users' e 'transactions' resetadas.")

def reset_firestore_collections():
    # Função para apagar todos os documentos de uma coleção
    def delete_collection(coll_ref, batch_size=100):
        docs = coll_ref.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            print(f"Apagando doc {doc.id} da coleção {coll_ref.id}")
            doc.reference.delete()
            deleted += 1

        if deleted >= batch_size:
            return delete_collection(coll_ref, batch_size)

    delete_collection(db.collection("users"))
    delete_collection(db.collection("transactions"))
    print("Firestore: coleções 'users' e 'transactions' resetadas.")

if __name__ == "__main__":
    reset_sqlite_tables()
    reset_firestore_collections()
    print("Reset completo realizado com sucesso.")
