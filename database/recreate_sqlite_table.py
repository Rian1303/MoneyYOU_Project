import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "db.sqlite"

def migrar_descricao_para_desc():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Renomear tabela antiga
    cursor.execute("ALTER TABLE transactions RENAME TO old_transactions;")

    # 2. Criar nova tabela com 'desc' no lugar de 'descricao'
    cursor.execute("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            desc TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL,
            data TEXT NOT NULL,
            tipo_recorrencia INTEGER DEFAULT 0
        );
    """)

    # 3. Copiar os dados da tabela antiga
    cursor.execute("""
        INSERT INTO transactions (id, user_id, desc, valor, tipo, data, tipo_recorrencia)
        SELECT id, user_id, descricao, valor, tipo, data, tipo_recorrencia
        FROM old_transactions;
    """)

    # 4. Apagar tabela antiga
    cursor.execute("DROP TABLE old_transactions;")

    conn.commit()
    conn.close()
    print("Migração concluída: coluna 'descricao' renomeada para 'desc'.")

if __name__ == "__main__":
    migrar_descricao_para_desc()
