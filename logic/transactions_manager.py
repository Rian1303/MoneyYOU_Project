# logic/transactions_manager.py

from database.data_manager import load_transactions, add_transaction as save_transaction, delete_transaction
from datetime import datetime
import csv

# -------------------------------
# Obter todas as transações
# -------------------------------
def get_all_transactions(user_id=None, start_date=None, end_date=None):
    """
    Retorna todas as transações, podendo filtrar por:
    - user_id: retorna só transações do usuário
    - start_date e end_date: objetos datetime.date
    """
    transactions = load_transactions()  # pega todas do Firebase/SQLite

    # Filtra por usuário
    if user_id:
        transactions = [t for t in transactions if t.get("user_id") == user_id]

    # Função para converter data de string para datetime.date
    def parse_date(tx):
        d = tx.get("date", "")
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()  # ajuste para o formato que você está salvando
        except:
            return None

    if start_date:
        transactions = [t for t in transactions if parse_date(t) and parse_date(t) >= start_date]
    if end_date:
        transactions = [t for t in transactions if parse_date(t) and parse_date(t) <= end_date]

    return transactions

# -------------------------------
# Adicionar transação
# -------------------------------
def add_transaction(transaction):
    return save_transaction(transaction)

# -------------------------------
# Deletar transação
# -------------------------------
def remove_transaction(tx_id):
    try:
        delete_transaction(tx_id)
        return True
    except Exception as e:
        print(f"[Erro] Não foi possível deletar: {e}")
        return False

# -------------------------------
# Restaurar transação
# -------------------------------
def restore_deleted_transaction(transaction):
    try:
        add_transaction(transaction)
        return True
    except Exception as e:
        print(f"[Erro] Não foi possível restaurar: {e}")
        return False

# -------------------------------
# Exportar CSV
# -------------------------------
def export_transactions_csv(transactions, path):
    if not transactions:
        print("Nenhuma transação para exportar.")
        return False
    try:
        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=transactions[0].keys())
            writer.writeheader()
            for t in transactions:
                writer.writerow(t)
        return True
    except Exception as e:
        print(f"[Erro CSV] {e}")
        return False
