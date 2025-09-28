import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Caminhos para temas (assumindo que você tenha esses paths em config.py)
try:
    from config import LIGHT_THEME, DARK_THEME
except ImportError:
    LIGHT_THEME = Path("assets/light.qss")
    DARK_THEME = Path("assets/dark.qss")


class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self.config = {"theme": "light"}  # padrão

        # Carregar config.json
        self.load_config()

        # Carregar chave da OpenAI
        self.load_openai_key()

    # ------------------- Config JSON -------------------
    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {"theme": "light"}

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    # ------------------- Tema -------------------
    def get_theme(self):
        return self.config.get("theme", "light")

    def set_theme(self, theme):
        if theme not in ["light", "dark"]:
            theme = "light"
        self.config["theme"] = theme
        self.save_config()

    def get_theme_path(self):
        return DARK_THEME if self.get_theme() == "dark" else LIGHT_THEME

    # ------------------- OpenAI -------------------
    def load_openai_key(self):
        """
        Procura e carrega a chave da OpenAI no ambiente.
        Procura primeiro em logic/openai_key.env, depois em config/openai_key.env.
        """
        # Pastas possíveis
        possible_paths = [
            Path(__file__).parent / "openai_key.env",           # logic/
            Path(__file__).resolve().parent.parent / "config" / "openai_key.env",  # config/
        ]

        for path in possible_paths:
            if path.exists():
                load_dotenv(path)
                print(f"[DEBUG] Carregando chave da OpenAI de: {path}")
                break

        # Confirma se a chave está no ambiente
        if os.getenv("OPENAI_API_KEY"):
            print("[DEBUG] OPENAI_API_KEY carregada com sucesso:", os.getenv("OPENAI_API_KEY")[:8], "...")
        else:
            print("⚠️ Nenhuma chave OPENAI_API_KEY encontrada. Verifique o arquivo openai_key.env.")

    def get_openai_key(self) -> str:
        """
        Retorna a chave da OpenAI carregada do ambiente
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ Chave da OpenAI não encontrada. Verifique o arquivo openai_key.env")
        return api_key
