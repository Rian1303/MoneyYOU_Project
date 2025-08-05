import sqlite3
from pathlib import Path

from pathlib import Path
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # Quando empacotado pelo PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

DB_PATH = resource_path("database/db.sqlite")
MIN_PASSWORD_LENGTH = 4  # Ajuste conforme seu config

def connect():
    return sqlite3.connect(DB_PATH)

def create_master_user():
    conn = connect()
    cursor = conn.cursor()

    # Tente criar tabela users se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Verifica se o usuário master já existe
    cursor.execute("SELECT 1 FROM users WHERE username = ?", ("master",))
    if cursor.fetchone() is None:
        # Se não existir, cria o usuário master com senha padrão
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("master", "master123"))
        print("Usuário master criado: username='master', senha='master123'")
    else:
        print("Usuário master já existe.")

    conn.commit()
    conn.close()

def validate_login(username: str, password: str) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return False  # Usuário não encontrado
    stored_password = result[0]

    # Atenção: comparar strings exatas
    return stored_password == password

def validate_registration(username: str, password: str, confirm_password: str) -> (bool, str):
    """
    Valida dados do cadastro: campos preenchidos, senha mínima, senhas iguais e usuário não existente.
    Retorna tupla (bool, mensagem).
    """
    if not username or not password or not confirm_password:
        return False, "Preencha todos os campos."

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres."

    if password != confirm_password:
        return False, "As senhas não conferem."

    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone()
    conn.close()

    if exists:
        return False, "Usuário já existe."

    return True, "Cadastro válido."

def register_user(username: str, password: str) -> None:
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("Usuário já existe.")
    conn.close()