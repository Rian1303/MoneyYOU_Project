import sys
import os
import sqlite3
import hashlib
import datetime
from typing import Tuple
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
MIN_PASSWORD_LENGTH = 6

# -------------------------------
# Funções auxiliares
# -------------------------------
def connect():
    return sqlite3.connect(DB_PATH)

def hash_password(password: str) -> str:
    """Gera hash SHA-256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verifica senha comparando com hash"""
    return hash_password(password) == hashed

# -------------------------------
# Validação de login
# -------------------------------
def validate_login(username: str, password: str) -> bool:
    hashed = hash_password(password)

    # Firebase
    doc = db.collection("users").document(username).get()
    if doc.exists:
        return verify_password(password, doc.to_dict().get("password"))

    # SQLite fallback
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result is not None and verify_password(password, result[0])
    except Exception:
        return False

# -------------------------------
# Validação de registro
# -------------------------------
def validate_registration(username: str, password: str, confirm_password: str, email: str) -> Tuple[bool, str]:
    if not username or not password or not confirm_password or not email:
        return False, "Preencha todos os campos."
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres."
    if password != confirm_password:
        return False, "As senhas não conferem."
    if "@" not in email or "." not in email:
        return False, "Email inválido."

    # Verifica Firebase
    if db.collection("users").document(username).get().exists:
        return False, "Usuário já existe."
    # Verifica SQLite
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ? OR email = ?", (username, email))
        exists = cursor.fetchone()
        conn.close()
        if exists:
            return False, "Usuário ou email já existem."
    except Exception:
        pass

    return True, "Cadastro válido."

# -------------------------------
# Registro de usuário
# -------------------------------
def register_user(username: str, password: str, email: str, role: str = "user") -> bool:
    hashed = hash_password(password)
    user_data = {
        "username": username,
        "email": email,
        "password": hashed,
        "role": role,
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    try:
        # Firebase
        db.collection("users").document(username).set(user_data)
        print(f"[Firebase] Usuário '{username}' criado.")

        # SQLite
        if not IS_FROZEN:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TEXT
                )
            """)
            cursor.execute("""
                INSERT OR IGNORE INTO users (username, email, password, role, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, hashed, role, user_data["created_at"]))
            conn.commit()
            conn.close()
        return True
    except Exception as e:
        print(f"[register_user] Erro: {e}")
        return False

# -------------------------------
# Mudar senha
# -------------------------------
def change_password(username: str, email: str, new_password: str) -> bool:
    if len(new_password) < MIN_PASSWORD_LENGTH:
        return False

    hashed = hash_password(new_password)

    try:
        # Firebase
        doc_ref = db.collection("users").document(username)
        doc = doc_ref.get()
        if doc.exists:
            user_data = doc.to_dict()
            if user_data.get("email") != email:
                print("[Firebase] Email não confere.")
                return False
            doc_ref.update({"password": hashed})
            print(f"[Firebase] Senha do usuário '{username}' atualizada.")
        else:
            print(f"[Firebase] Usuário '{username}' não encontrado.")

        # SQLite
        if not IS_FROZEN:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE username = ? AND email = ?",
                           (hashed, username, email))
            conn.commit()
            conn.close()
        return True
    except Exception as e:
        print(f"[change_password] Erro: {e}")
        return False

# -------------------------------
# Criar usuário master
# -------------------------------
def create_master_user():
    register_user("master", "master123", "master@moneyyou.com", role="admin")
