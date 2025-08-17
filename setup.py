import sys
import os
from cx_Freeze import setup, Executable

APP_NAME = "MoneyYOU"
MAIN_SCRIPT = "main.py"

# Caminho para a pasta platforms do PyQt6
PYQT6_PLATFORMS_DIR = os.path.join(
    sys.prefix, "Lib", "site-packages", "PyQt6", "Qt6", "plugins", "platforms"
)

if not os.path.exists(PYQT6_PLATFORMS_DIR):
    raise FileNotFoundError(f"A pasta de plataformas do PyQt6 não foi encontrada: {PYQT6_PLATFORMS_DIR}")

build_exe_options = {
    "packages": ["PyQt6", "firebase_admin", "os", "sys", "json", "requests"],
    "include_files": [
        ("config/firebase_key.json", "config/firebase_key.json"),
        ("database/data.json", "database/data.json"),
        ("assets", "assets"),
        (PYQT6_PLATFORMS_DIR, "PyQt6/Qt/plugins/platforms"),
    ],
    "include_msvcr": True,
}

executables = [
    Executable(
        MAIN_SCRIPT,
        base="Win32GUI",  # sem terminal
        icon="assets/icons/app_icon.png"
    )
]

setup(
    name=APP_NAME,
    version="1.0",
    description="Sistema de Controle Financeiro MoneyYOU",
    options={"build_exe": build_exe_options},
    executables=executables
)
