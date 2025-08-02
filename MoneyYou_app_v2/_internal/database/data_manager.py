import json
from config import JSON_DB_PATH  # Usa o caminho do config.py
import csv

def load_data():
    """
    Load data from the database JSON file.
    Returns a dict. If file doesn't exist or is inválid, returns empty dict.
    """
    try:
        with open(JSON_DB_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Arquivo {JSON_DB_PATH} não encontrado. Retornando dados vazios.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON em {JSON_DB_PATH}. Retornando dados vazios.")
        return {}

def save_data(data):
    """
    Save data to the database JSON file.
    """
    try:
        with open(JSON_DB_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Erro ao salvar dados: {e}")

def add_transaction(transaction):
    """
    Add a transaction dict to the transactions list and save.
    """
    data = load_data()
    data.setdefault('transactions', []).append(transaction)
    save_data(data)

def edit_transaction(id, new_data):
    """
    Update transaction with given id using new_data dict.
    """
    data = load_data()
    for transaction in data.get('transactions', []):
        if transaction.get('id') == id:
            transaction.update(new_data)
            save_data(data)
            return True  # sucesso
    return False  # não encontrado

def delete_transaction(id):
    """
    Remove transaction with given id.
    """
    data = load_data()
    original_len = len(data.get('transactions', []))
    data['transactions'] = [t for t in data.get('transactions', []) if t.get('id') != id]
    if len(data['transactions']) < original_len:
        save_data(data)
        return True
    return False

def export_csv(path):
    """
    Export all transactions to a CSV file at given path.
    """
    data = load_data()
    transactions = data.get('transactions', [])

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
