import sys
import os
import sqlite3
from logic.firebase import db  # Cliente Firestore

# Detecta se está rodando empacotado (PyInstaller)
IS_FROZEN = getattr(sys, 'frozen', False)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

DB_PATH = resource_path("database/db.sqlite")
MIN_PASSWORD_LENGTH = 4  # Configurável


# -------------------------------
# Função de conexão SQLite (apenas no desenvolvimento)
# -------------------------------
def connect():
    if IS_FROZEN:
        raise RuntimeError("SQLite desativado no modo produção (usando apenas Firebase)")
    return sqlite3.connect(DB_PATH)


# -------------------------------
# Criar usuário master (apenas dev)
# -------------------------------
def create_master_user():
    if IS_FROZEN:
        print("[Aviso] create_master_user ignorado no modo produção.")
        return

    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("SELECT 1 FROM users WHERE username = ?", ("master",))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("master", "master123"))
        print("Usuário master criado: username='master', senha='master123'")
    else:
        print("Usuário master já existe.")
    conn.commit()
    conn.close()


# -------------------------------
# Validação de login
# -------------------------------
def validate_login(username: str, password: str) -> bool:
    if IS_FROZEN:
        # Produção → consulta no Firebase
        doc = db.collection("users").document(username).get()
        if doc.exists:
            return doc.to_dict().get("password") == password
        return False

    # Desenvolvimento → consulta no SQLite
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None and result[0] == password


# -------------------------------
# Validação de cadastro
# -------------------------------
def validate_registration(username: str, password: str, confirm_password: str) -> (bool, str):
    if not username or not password or not confirm_password:
        return False, "Preencha todos os campos."

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres."

    if password != confirm_password:
        return False, "As senhas não conferem."

    if IS_FROZEN:
        # Produção → verificar no Firebase
        if db.collection("users").document(username).get().exists:
            return False, "Usuário já existe."
        return True, "Cadastro válido."

    # Desenvolvimento → verificar no SQLite
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone()
    conn.close()
    if exists:
        return False, "Usuário já existe."
    return True, "Cadastro válido."


# -------------------------------
# Registro de usuário
# -------------------------------
def register_user(username: str, password: str) -> None:
    if IS_FROZEN:
        # Produção → apenas Firebase
        db.collection("users").document(username).set({
            "username": username,
            "password": password  # ⚠ Idealmente usar hash
        })
        print(f"[Firebase] Usuário '{username}' adicionado com sucesso.")
        return

    # Desenvolvimento → SQLite + Firebase
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        db.collection("users").document(username).set({
            "username": username,
            "password": password
        })
        print(f"[Firebase] Usuário '{username}' adicionado com sucesso.")
    except sqlite3.IntegrityError:
        raise ValueError("Usuário já existe.")
    finally:
        conn.close()


# -------------------------------
# Sincronização de usuários (dev)
# -------------------------------
def sync_users_to_firebase():
    if IS_FROZEN:
        print("[Aviso] sync_users_to_firebase ignorado no modo produção.")
        return

    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users")
    all_users = cursor.fetchall()
    conn.close()

    count = 0
    for username, password in all_users:
        db.collection("users").document(username).set({
            "username": username,
            "password": password
        })
        count += 1
        print(f"[Firebase] Usuário '{username}' sincronizado.")
    print(f"[Firebase] Total de {count} usuários sincronizados.")
