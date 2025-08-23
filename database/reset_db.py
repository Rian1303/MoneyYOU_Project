import sqlite3

# Conectar ao banco
conn = sqlite3.connect("database/db.sqlite")
cursor = conn.cursor()

# Apagar todas as transações
cursor.execute("DELETE FROM transactions;")

# Resetar ID (opcional, só se você usa AUTOINCREMENT e quiser começar do 1 de novo)
cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions';")

conn.commit()
conn.close()

print("🗑️ Todas as transações no SQLite foram deletadas!")
