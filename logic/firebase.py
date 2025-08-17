import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
from database.data_manager import load_transactions
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from database.data_manager import resource_path

# pega o caminho certo do JSON (funciona normal + empacotado)
cred_path = resource_path("config/firebase_key.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
def resource_path(relative_path):
    """Obter o caminho absoluto do recurso, funcionando no EXE criado pelo PyInstaller."""
    try:
        # PyInstaller cria uma pasta temporária e define esta variável
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Caminho para o arquivo JSON da chave
FIREBASE_KEY_PATH = resource_path("config/firebase_key.json")

# Inicializa o Firebase uma única vez
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred)

# Cliente do Firestore
db = firestore.client()

def send_transaction_to_firebase(transaction: dict) -> None:
    """
    Envia uma transação para o Firestore.
    """
    try:
        doc_ref = db.collection("transactions").document()
        doc_ref.set(transaction)
    except Exception as e:
        print(f"[Firebase] Erro ao enviar transação: {e}")

def sync_transactions_to_firebase(user_id):
    """
    Envia todas as transações locais do usuário para o Firestore.
    """
    try:
        db = firestore.client()
        transactions = load_transactions(user_id=user_id)

        for t in transactions:
            doc_ref = db.collection("transactions").document(str(t["id"]))
            doc_ref.set(t)

        return {"status": "success", "message": "Transações sincronizadas"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
