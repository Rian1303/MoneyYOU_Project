# transactions_manager.py

from logic.transactions import load_transactions, add_transaction
from logic.firebase import sync_transactions_to_firebase
from datetime import datetime
import csv

def get_transactions(start_date=None, end_date=None):
    """
    Retorna lista de transações filtradas por período (opcional).
    start_date e end_date devem ser objetos datetime ou None.
    """
    transactions = load_transactions()
    if start_date or end_date:
        filtered = []
        for t in transactions:
            try:
                t_date = datetime.strptime(t['date'], "%Y-%m-%d")
            except Exception as e:
                print(f"Erro ao ler data da transação {t.get('id')}: {e}")
                continue
            if (not start_date or t_date >= start_date) and (not end_date or t_date <= end_date):
                filtered.append(t)
        return filtered
    return transactions

def remove_transaction(transaction_id):
    """
    Deleta transação local e sincroniza com Firebase.
    Retorna True se sucesso, False se falhou.
    """
    transactions = load_transactions()
    transaction_to_delete = next((t for t in transactions if t['id'] == transaction_id), None)
    if not transaction_to_delete:
        return False

    try:
        transactions.remove(transaction_to_delete)
        sync_transactions_to_firebase(transactions)
        return True
    except Exception as e:
        print(f"Erro ao deletar transação: {e}")
        return False

def restore_deleted_transaction(transaction):
    """
    Restaura transação local e sincroniza com Firebase.
    """
    transactions = load_transactions()
    try:
        transactions.append(transaction)
        sync_transactions_to_firebase(transactions)
        return True
    except Exception as e:
        print(f"Erro ao restaurar transação: {e}")
        return False

def export_transactions_csv(transactions, file_path):
    """
    Exporta lista de transações para CSV.
    """
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'date', 'category', 'amount', 'description', 'type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for t in transactions:
                writer.writerow(t)
        return True
    except Exception as e:
        print(f"Erro ao exportar CSV: {e}")
        return False

def prepare_chart_data(transactions):
    """
    Prepara dados para gráfico (ex.: total por categoria).
    Retorna dict {categoria: soma valores}.
    """
    chart_data = {}
    for t in transactions:
        cat = t.get('category', 'Outros')
        amount = t.get('amount', 0)
        chart_data[cat] = chart_data.get(cat, 0) + amount
    return chart_data
