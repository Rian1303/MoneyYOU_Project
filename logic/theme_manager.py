# theme_manager.py

from pathlib import Path
from config import LIGHT_THEME, DARK_THEME

# Variável global que mantém o tema atual
CURRENT_THEME = "light"  # tema inicial

# Caminho do arquivo QSS carregado
CURRENT_QSS_PATH = LIGHT_THEME

def set_theme(theme_name: str):
    """
    Define o tema global do app.
    Pode ser "light" ou "dark".
    """
    global CURRENT_THEME, CURRENT_QSS_PATH
    theme_name = theme_name.lower()
    if theme_name == "light":
        CURRENT_THEME = "light"
        CURRENT_QSS_PATH = LIGHT_THEME
    elif theme_name == "dark":
        CURRENT_THEME = "dark"
        CURRENT_QSS_PATH = DARK_THEME
    else:
        raise ValueError("Tema inválido. Use 'light' ou 'dark'.")

def get_theme() -> str:
    """
    Retorna o nome do tema atual: "light" ou "dark"
    """
    return CURRENT_THEME

def load_theme_qss() -> str:
    """
    Retorna o conteúdo do arquivo QSS do tema atual
    """
    if not CURRENT_QSS_PATH.exists():
        return ""
    with open(CURRENT_QSS_PATH, "r", encoding="utf-8") as f:
        return f.read()
