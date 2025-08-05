import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "db.sqlite"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE transactions ADD COLUMN desc TEXT")
    print("Coluna 'desc' adicionada com sucesso.")
except sqlite3.OperationalError as e:
    print("Erro ou coluna já existe:", e)

conn.commit()
conn.close()
