import sqlite3
import os

# Caminho absoluto para o banco de dados correto
base_dir = os.path.dirname(os.path.abspath(__file__))  # pasta onde está este script
sqlite_path = os.path.join(base_dir, "db.sqlite")  # banco na mesma pasta
# Se o script NÃO está na mesma pasta que o banco:
# sqlite_path = os.path.join(base_dir, "..", "database", "db.sqlite")

print(f"📂 Usando banco de dados: {sqlite_path}")

conn = sqlite3.connect(sqlite_path)
cursor = conn.cursor()

# Lista de colunas a criar
colunas_novas = [
    ("email", "TEXT"),
    ("created_at", "TEXT"),
    ("last_login", "TEXT")
]

# Adiciona cada coluna se não existir
for nome, tipo in colunas_novas:
    try:
        cursor.execute(f"ALTER TABLE users ADD COLUMN {nome} {tipo}")
        print(f"✅ Coluna '{nome}' criada")
    except sqlite3.OperationalError:
        print(f"ℹ️ Coluna '{nome}' já existe")

conn.commit()
conn.close()

print("🎯 Banco de dados atualizado com sucesso!")
