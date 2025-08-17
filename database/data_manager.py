import sqlite3
from pathlib import Path
import sys
import os
import firebase_admin
from firebase_admin import credentials, firestore


def resource_path(relative_path):
    """
    Retorna o caminho correto para arquivos externos,
    funciona no Python normal e no .exe onefile/onedir
    """
    if getattr(sys, 'frozen', False):
        # Se rodando do exe, base é a pasta onde o exe está
        base_path = os.path.dirname(sys.executable)
    else:
        # Python normal
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

cred_path = resource_path("config/firebase_key.json")
cred = credentials.Certificate(cred_path)

# Detecta se o programa está empacotado (PyInstaller)
IS_PACKAGED = getattr(sys, 'frozen', False)

# Se estiver empacotado -> usa Firebase, senão -> SQLite local
USE_FIREBASE = IS_PACKAGED

if USE_FIREBASE:
    # ========================
    # 🔥 Implementação Firebase
    # ========================
    import firebase_admin
    from firebase_admin import credentials, firestore

    # Ajuste o caminho da sua chave Firebase
    cred = credentials.Certificate("config/firebase_key.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    def add_transaction(transaction):
        db.collection("transactions").add(transaction)

    def edit_transaction(doc_id, new_data):
        doc_ref = db.collection("transactions").document(doc_id)
        doc_ref.update(new_data)

    def delete_transaction(doc_id):
        db.collection("transactions").document(doc_id).delete()

    def load_transactions(user_id=None):
        docs = db.collection("transactions").stream()
        transactions = [doc.to_dict() for doc in docs]
        if user_id:
            transactions = [t for t in transactions if t.get("user_id") == user_id]
        # Adiciona o ID do documento para poder editar/deletar
        for t, doc in zip(transactions, db.collection("transactions").stream()):
            t["id"] = doc.id
        return transactions

    def export_csv(path, user_id=None):
        import csv
        transactions = load_transactions(user_id)

        if not transactions:
            print("Nenhuma transação para exportar.")
            return

        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = transactions[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for transaction in transactions:
                writer.writerow(transaction)
        print(f"Transações exportadas para {path} com sucesso.")

else:
    # ========================
    # 💾 Implementação SQLite (modo dev/local)
    # ========================
    DB_PATH = Path(__file__).parent / "db.sqlite"

    def connect():
        return sqlite3.connect(DB_PATH)

    def add_transaction(transaction):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, type, amount, category, date, desc)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            transaction.get('user_id'),
            transaction.get('type'),
            transaction.get('amount'),
            transaction.get('category'),
            transaction.get('date'),
            transaction.get('desc')
        ))
        conn.commit()
        conn.close()

    def edit_transaction(id, new_data):
        conn = connect()
        cursor = conn.cursor()
        fields = ", ".join([f"{k} = ?" for k in new_data.keys()])
        values = list(new_data.values())
        values.append(id)
        query = f"UPDATE transactions SET {fields} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        updated = cursor.rowcount
        conn.close()
        return updated > 0

    def delete_transaction(id):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (id,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        return deleted > 0

    def load_transactions(user_id=None):
        conn = connect()
        cursor = conn.cursor()
        if user_id:
            cursor.execute("""
                SELECT id, user_id, type, amount, category, date, desc 
                FROM transactions 
                WHERE user_id = ? 
                ORDER BY date DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT id, user_id, type, amount, category, date, desc 
                FROM transactions 
                ORDER BY date DESC
            """)
        rows = cursor.fetchall()
        conn.close()
        keys = ['id', 'user_id', 'type', 'amount', 'category', 'date', 'desc']
        return [dict(zip(keys, row)) for row in rows]

    def export_csv(path, user_id=None):
        import csv
        transactions = load_transactions(user_id)

        if not transactions:
            print("Nenhuma transação para exportar.")
            return

        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = transactions[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for transaction in transactions:
                writer.writerow(transaction)
        print(f"Transações exportadas para {path} com sucesso.")
