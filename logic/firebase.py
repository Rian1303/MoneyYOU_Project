import os
import sys
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from database.data_manager import load_transactions


def resource_path(relative_path: str) -> str:
    """
    Obter o caminho absoluto do recurso, funcionando no EXE criado pelo PyInstaller.
    """
    try:
        # PyInstaller cria uma pasta temporária e define esta variável
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Caminho para o arquivo JSON da chave do Firebase
FIREBASE_KEY_PATH = resource_path("config/firebase_key.json")


def initialize_firebase():
    """
    Inicializa o Firebase apenas uma vez.
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred)


# Inicializa o Firebase ao importar o módulo
initialize_firebase()

# Cliente Firestore global
db = firestore.client()


def send_transaction_to_firebase(transaction: dict) -> None:
    """
    Envia uma única transação para o Firestore.
    """
    try:
        doc_ref = db.collection("transactions").document(str(transaction.get("id")))
        doc_ref.set(transaction)
        print(f"[Firebase] Transação {transaction.get('id')} enviada com sucesso.")
    except Exception as e:
        print(f"[Firebase] Erro ao enviar transação: {e}")


def sync_transactions_to_firebase(user_id: str) -> dict:
    """
    Envia todas as transações locais de um usuário para o Firestore.
    """
    try:
        transactions = load_transactions(user_id=user_id)

        for t in transactions:
            doc_ref = db.collection("transactions").document(str(t["id"]))
            doc_ref.set(t)

        return {"status": "success", "message": f"{len(transactions)} transações sincronizadas."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
