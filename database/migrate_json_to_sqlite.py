# database/migrate_json_to_sqlite.py

import json
import sqlite3
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent
JSON_PATH = BASE_DIR / "data.json"
DB_PATH = BASE_DIR / "db.sqlite"

# Conectar ao banco
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Carregar JSON
with open(JSON_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

# Migrar usuários
user_id_map = {}  # Mapeia username para user_id no banco
for user in data.get("users", []):
    username = user["username"]
    password = user["password"]
    
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()

    # Buscar o ID do usuário inserido
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()[0]
    user_id_map[username] = user_id

# Migrar transações
for transaction in data.get("transactions", []):
    username = transaction.get("username")
    user_id = user_id_map.get(username)

    cursor.execute("""
        INSERT INTO transactions (user_id, type, amount, category, date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        transaction["type"],
        transaction["amount"],
        transaction.get("category", ""),
        transaction["date"]
    ))

# Finalizar
conn.commit()
conn.close()

print("✅ Migração concluída com sucesso.")
