import json
import os
from pathlib import Path

class UserConfigManager:
    def __init__(self, user_id: str, default_config=None):
        self.user_id = user_id
        self.config_path = os.path.join("database", f"{self.user_id}_config.json")
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        self.default_config = default_config or {
            "theme": "light",
            "notifications": True,
            "currency": "BRL"
        }
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Carrega as configurações do usuário, ou retorna padrão se não existir."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[UserConfigManager] Erro ao carregar config: {e}")
        return self.default_config.copy()

    def save_config(self):
        """Salva as configurações do usuário em arquivo JSON."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"[UserConfigManager] Erro ao salvar config: {e}")

    def set_option(self, key: str, value):
        """Atualiza uma opção da configuração e salva."""
        self.config[key] = value
        self.save_config()

    def get_option(self, key: str, default=None):
        """Retorna uma opção da configuração ou default se não existir."""
        if default is None:
            default = self.default_config.get(key)
        return self.config.get(key, default)
