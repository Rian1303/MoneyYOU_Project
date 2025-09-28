import sys
import os
import sqlite3
from logic.firebase import db  # Cliente Firestore

# Detecta se está rodando empacotado (PyInstaller)
IS_FROZEN = getattr(sys, 'frozen', False)

# Caminho para banco SQLite (apenas dev)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

DB_PATH = resource_path("database/db.sqlite")
MIN_PASSWORD_LENGTH = 4  # Configurável

# -------------------------------
# Conexão SQLite (fallback/dev)
# -------------------------------
def connect():
    return sqlite3.connect(DB_PATH)

# -------------------------------
# Validação de login
# -------------------------------
def validate_login(username: str, password: str) -> bool:
    # Primeiro tenta no Firebase
    doc = db.collection("users").document(username).get()
    if doc.exists:
        return doc.to_dict().get("password") == password

    # Se não existir no Firebase, tenta no SQLite
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None and result[0] == password
    except Exception:
        return False

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

    # Verifica se já existe no Firebase
    if db.collection("users").document(username).get().exists:
        return False, "Usuário já existe."

    # Opcional: verifica no SQLite como fallback
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        exists = cursor.fetchone()
        conn.close()
        if exists:
            return False, "Usuário já existe."
    except Exception:
        pass

    return True, "Cadastro válido."

# -------------------------------
# Registro de usuário
# -------------------------------
def register_user(username: str, password: str) -> None:
    # Firebase principal
    db.collection("users").document(username).set({
        "username": username,
        "password": password
    })
    print(f"[Firebase] Usuário '{username}' adicionado com sucesso.")

    # SQLite fallback (desenvolvimento)
    if not IS_FROZEN:
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[SQLite] Erro ao salvar usuário localmente: {e}")

# -------------------------------
# Sincronização de usuários SQLite → Firebase (opcional)
# -------------------------------
def sync_users_to_firebase():
    try:
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
    except Exception as e:
        print(f"[sync_users_to_firebase] Erro: {e}")
def create_master_user():
    """
    Cria um usuário master padrão:
    - username: master
    - password: master123
    Prioriza Firebase e, se em desenvolvimento, também salva no SQLite.
    """
    username = "master"
    password = "master123"

    # Verifica se já existe no Firebase
    if db.collection("users").document(username).get().exists:
        print("[Firebase] Usuário master já existe.")
    else:
        db.collection("users").document(username).set({
            "username": username,
            "password": password
        })
        print("[Firebase] Usuário master criado: username='master', senha='master123'")

    # SQLite fallback (apenas desenvolvimento)
    if not IS_FROZEN:
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            print("[SQLite] Usuário master criado localmente (dev).")
        except Exception as e:
            print(f"[SQLite] Erro ao criar usuário master localmente: {e}")
