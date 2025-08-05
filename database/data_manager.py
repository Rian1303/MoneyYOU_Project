import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "db.sqlite"

def connect():
    return sqlite3.connect(DB_PATH)

def add_transaction(transaction):
    """
    transaction: dict com keys: user_id, type, amount, category, date, desc
    """
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
    """
    Atualiza uma transação pelo id com os campos em new_data (dict).
    """
    conn = connect()
    cursor = conn.cursor()

    # Montar query dinâmica para UPDATE
    fields = ", ".join([f"{k} = ?" for k in new_data.keys()])
    values = list(new_data.values())
    values.append(id)  # id no WHERE

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
    """
    Retorna lista de dicts com as transações.
    Se user_id for passado, filtra só desse usuário.
    """
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
