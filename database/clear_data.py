import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "db.sqlite"

def connect():
    return sqlite3.connect(DB_PATH)

def reset_transactions_table():
    conn = connect()
    cursor = conn.cursor()

    # Apaga todas as transações
    cursor.execute("DELETE FROM transactions")

    # Reinicia o autoincremento (para ID começar do 1 de novo)
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")

    conn.commit()
    conn.close()
    print("Transações apagadas e ID reiniciado.")

reset_transactions_table()
