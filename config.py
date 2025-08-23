import sys
from pathlib import Path


# Detecta se está rodando como exe ou script
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent  # pasta do exe
else:
    BASE_DIR = Path(__file__).resolve().parent  # pasta do script

# Diretórios e arquivos
DATABASE_DIR = BASE_DIR / "database"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
CONFIG_DIR = BASE_DIR / "config"

STYLE_PATH = ASSETS_DIR / "style.qss"
JSON_DB_PATH = DATABASE_DIR / "data.json"
FIREBASE_KEY_PATH = CONFIG_DIR / "firebase_key.json"
APP_ICON = ICONS_DIR / "app_icon.png"
# ==========================
# Temas (Dark / Light)
# ==========================
LIGHT_THEME = ASSETS_DIR / "light.qss"
DARK_THEME = ASSETS_DIR / "dark.qss"

# Tema padrão (inicial)
APP_THEME = LIGHT_THEME

# ==========================
# Arquivos principais
# ==========================
STYLE_PATH = ASSETS_DIR / "style.qss"
JSON_DB_PATH = DATABASE_DIR / "data.json"
APP_ICON = ICONS_DIR / "app_icon.png"

# ==========================
# Informações do App
# ==========================
APP_INFO = {
    "name": "Financial Organizer",
    "version": "1.0.0",
    "author": "Rian",
    "description": "Organize suas finanças de forma simples e offline"
}

# ==========================
# Configuração de Login de Teste
# ==========================
TEST_USER = {
    "username": "admin",
    "password": "1234"
}

# ==========================
# Usuários para teste
# ==========================
USERS = {
    "admin": "1234"
}

# ==========================
# Regras de senha
# ==========================
MIN_PASSWORD_LENGTH = 4

# ==========================
# Cores Globais (HEX)
# ==========================
COLORS = {
    "background": "#F9FAFB",
    "primary": "#7C3AED",
    "secondary": "#A855F7",
    "text": "#1E1E1E",
    "error": "#EF4444",
    "success": "#10B981"
}

# ==========================
# Categorias Padrão de Transações
# ==========================
DEFAULT_CATEGORIES = {
    "Income": ["Scholarship", "Salary", "Gift", "Other"],
    "Expense": ["Rent", "Food", "Transport", "Bills", "Entertainment", "Other"]
}

# ==========================
# Conversão de Moedas (valores fixos)
# ==========================
CURRENCY_CONVERSION = {
    "BRL_to_USD": 0.19,
    "BRL_to_EUR": 0.17,
    "USD_to_BRL": 5.30,
    "EUR_to_BRL": 6.00
}
