from datetime import datetime
from database.data_manager import add_transaction as db_add_transaction, \
                                  load_data, save_data
# Se quiser, importe outras funções do data_manager conforme necessário


def add_transaction(data):
    """
    Adds a new transaction to the database.

    Args:
        data (dict): A dictionary containing transaction details.

    Returns:
        dict: A response indicating success or failure.
    """
    try:
        # Garante que a data esteja no formato correto ou insere a data atual
        if 'data' not in data or not data['data']:
            data['data'] = datetime.now().strftime('%d/%m/%Y')
        else:
            try:
                # Valida o formato informado
                datetime.strptime(data['data'], '%d/%m/%Y')
            except ValueError:
                return {"status": "error", "message": "Data inválida. Use o formato dd/mm/yyyy."}

        db_add_transaction(data)
        return {"status": "success", "message": "Transaction added successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def edit_transaction(id, new_data):
    """
    Edit a transaction by id.

    Args:
        id (str): The unique identifier of the transaction.
        new_data (dict): The new data to update.

    Returns:
        bool: True if edited, False if not found.
    """
    data = load_data()
    for transaction in data.get('transactions', []):
        if transaction.get('id') == id:
            transaction.update(new_data)
            save_data(data)
            return True
    return False


def delete_transaction(id):
    """
    Delete a transaction by id.

    Args:
        id (str): The unique identifier of the transaction.

    Returns:
        bool: True if deleted, False if not found.
    """
    data = load_data()
    original_len = len(data.get('transactions', []))
    data['transactions'] = [t for t in data.get('transactions', []) if t.get('id') != id]
    if len(data['transactions']) < original_len:
        save_data(data)
        return True
    return False

def filter_transactions(transactions, tipo=None, categoria=None, data_inicio=None, data_fim=None):
    filtered = transactions
    date_format = "%d/%m/%Y"

    if tipo:
        filtered = [t for t in filtered if t.get('type', '').lower() == tipo.lower()]

    if categoria:
        filtered = [t for t in filtered if t.get('category', '').lower() == categoria.lower()]

    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, date_format)
            filtered = [t for t in filtered if datetime.strptime(t.get('date', '01/01/1900'), date_format) >= dt_inicio]
        except Exception:
            pass

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, date_format)
            filtered = [t for t in filtered if datetime.strptime(t.get('date', '01/01/1900'), date_format) <= dt_fim]
        except Exception as e:
            print(f"Erro ao converter data_fim: {e}")

    return filtered

def calcular_saldo(transactions):
    """
    Calculates the total balance based on transaction types.

    Args:
        transactions (list): A list of transaction dictionaries.

    Returns:
        float: The total balance.
    """
    saldo = 0.0
    for transaction in transactions:
        try:
            valor = float(transaction.get('valor', 0))
        except (ValueError, TypeError):
            valor = 0.0

        tipo = transaction.get('tipo', '').lower()
        if tipo == 'entrada':
            saldo += valor
        elif tipo == 'saida':
            saldo -= valor

    return saldo
