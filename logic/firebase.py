import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from database.data_manager import load_transactions

def resource_path(relative_path: str) -> str:
    """Obter caminho absoluto do recurso (compatível com PyInstaller)."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Caminho para a chave do Firebase
FIREBASE_KEY_PATH = resource_path("config/firebase_key.json")

# Inicializa Firebase apenas uma vez
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred)
    print("[Firebase] Inicializado com sucesso.")

# Cliente Firestore
db = firestore.client()

def send_transaction_to_firebase(transaction: dict) -> dict:
    """Envia uma transação para o Firestore."""
    try:
        doc_ref = db.collection("transactions").document(str(transaction.get("id")))
        doc_ref.set(transaction)
        return {"status": "success", "message": f"Transação {transaction.get('id')} enviada com sucesso."}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao enviar transação: {e}"}

def sync_transactions_to_firebase(user_id: str) -> dict:
    """Sincroniza todas as transações locais de um usuário para o Firestore."""
    try:
        transactions = load_transactions(user_id=user_id)
        if not transactions:
            return {"status": "warning", "message": "Nenhuma transação para sincronizar."}
        for t in transactions:
            doc_ref = db.collection("transactions").document(str(t["id"]))
            doc_ref.set(t)
        return {"status": "success", "message": f"{len(transactions)} transações sincronizadas."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
