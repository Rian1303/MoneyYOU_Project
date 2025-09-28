# logic/usr_config.py
import os
import threading
import logging

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except Exception as e:
    raise RuntimeError("Instale firebase-admin (pip install firebase-admin) e configure as credenciais.") from e

_log = logging.getLogger(__name__)

# Inicializa o app Firebase (somente uma vez)
def _init_firebase():
    if firebase_admin._apps:
        return
    # Tenta pegar credenciais de ambiente, depois arquivo padrão config/firebase_key.json
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.path.join("config", "firebase_key.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _log.debug("Firebase inicializado com credenciais em %s", cred_path)
    else:
        # tenta init default (se estiver rodando em ambiente com ADC)
        try:
            firebase_admin.initialize_app()
            _log.debug("Firebase inicializado com Application Default Credentials")
        except Exception as e:
            _log.exception("Não foi possível inicializar o Firebase. Coloque o arquivo de chave em config/firebase_key.json ou defina GOOGLE_APPLICATION_CREDENTIALS.")
            raise

_init_firebase()
_db = firestore.client()


class UserConfigManager:
    """Gerencia leitura/escrita/escuta de configs do usuário na collection 'usr_config'."""

    @staticmethod
    def get_user_config(user_id: str) -> dict:
        doc_ref = _db.collection("usr_config").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        # cria padrão
        default = {
            "theme": "light",
            "currency": "BRL",
            "timezone": "UTC-3",
            "avatar_color": "#7C3AED",
            "show_email": True,
            "show_birthdate": False,
        }
        doc_ref.set(default)
        return default

    @staticmethod
    def update_user_config(user_id: str, new_config: dict):
        doc_ref = _db.collection("usr_config").document(user_id)
        doc_ref.set(new_config, merge=True)

    @staticmethod
    def listen_user_config(user_id: str, callback):
        """
        Cria listener em tempo real. callback recebe (config_dict).
        Retorna o registration (precisa ser guardado para cancelar depois).
        """
        doc_ref = _db.collection("usr_config").document(user_id)

        def _on_snapshot(doc_snapshot, changes, read_time):
            if not doc_snapshot:
                return
            try:
                data = doc_snapshot[0].to_dict()
                # callback pode ser chamado em thread separada
                callback(data)
            except Exception:
                _log.exception("Erro no snapshot callback")

        registration = doc_ref.on_snapshot(_on_snapshot)
        return registration
