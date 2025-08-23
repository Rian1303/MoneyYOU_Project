import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from config import LIGHT_THEME, DARK_THEME, JSON_DB_PATH


def set_theme(theme: str):
    """
    Aplica o tema escolhido (light ou dark) e salva no data.json
    :param theme: "light" ou "dark"
    """
    theme_path = LIGHT_THEME if theme == "light" else DARK_THEME

    # Aplica no app
    app = QApplication.instance()
    if app:
        with open(theme_path, "r", encoding="utf-8") as f:
            style = f.read()
            app.setStyleSheet(style)

    # Atualiza no JSON
    if Path(JSON_DB_PATH).exists():
        with open(JSON_DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    data["theme"] = theme

    with open(JSON_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_theme():
    """
    Carrega o último tema salvo no data.json (default = light)
    """
    theme = "light"
    if Path(JSON_DB_PATH).exists():
        with open(JSON_DB_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                theme = data.get("theme", "light")
            except json.JSONDecodeError:
                pass

    set_theme(theme)
