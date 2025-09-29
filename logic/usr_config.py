# logic/usr_config.py
import os
import logging

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except Exception as e:
    raise RuntimeError("Instale firebase-admin (pip install firebase-admin) e configure as credenciais.") from e

_log = logging.getLogger(__name__)

# Inicializa Firebase (uma vez)
def _init_firebase():
    if firebase_admin._apps:
        return
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.path.join("config", "firebase_key.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _log.debug("Firebase inicializado com credenciais em %s", cred_path)
    else:
        try:
            firebase_admin.initialize_app()
            _log.debug("Firebase inicializado com Application Default Credentials")
        except Exception:
            _log.exception("Não foi possível inicializar o Firebase.")
            raise

_init_firebase()
_db = firestore.client()


class UserConfigManager:
    """Gerencia leitura/escrita/escuta de configs do usuário."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.doc_ref = _db.collection("usr_config").document(user_id)
        self.config = self.load_config()

    def load_config(self) -> dict:
        doc = self.doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        # Cria padrão se não existir
        default = {
            "theme": "light",
            "currency": "BRL",
            "timezone": "UTC-3",
            "avatar_color": "#7C3AED",
            "show_email": True,
            "show_birthdate": False,
        }
        self.doc_ref.set(default)
        return default

    def update_config(self, new_config: dict):
        """Atualiza config local e no Firebase."""
        self.config.update(new_config)
        self.doc_ref.set(self.config, merge=True)

    def listen_config(self, callback):
        """Cria listener em tempo real. Callback recebe (config_dict)."""
        def _on_snapshot(doc_snapshot, changes, read_time):
            if not doc_snapshot:
                return
            try:
                data = doc_snapshot[0].to_dict()
                callback(data)
            except Exception:
                _log.exception("Erro no snapshot callback")

        registration = self.doc_ref.on_snapshot(_on_snapshot)
        return registration

    # Métodos de conveniência
    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value
        self.update_config({key: value})
    @classmethod
    def set_user_config(cls, user_id: str, new_config: dict):
        instance = cls(user_id)
        instance.update_config(new_config)
