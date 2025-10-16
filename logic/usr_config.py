# logic/usr_config.py
import os
import logging

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except Exception as e:
    raise RuntimeError("Instale firebase-admin (pip install firebase-admin) e configure as credenciais.") from e

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

# Inicializa Firebase (uma vez)
def _init_firebase():
    try:
        if firebase_admin._apps:
            _log.debug("Firebase já inicializado (apps existentes).")
            return
    except Exception:
        # em algumas versões _apps pode não existir; apenas continue
        pass

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.path.join("config", "firebase_key.json")
    try:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _log.debug("Firebase inicializado com credenciais em %s", cred_path)
        else:
            # tenta Default Application Credentials
            firebase_admin.initialize_app()
            _log.debug("Firebase inicializado com Application Default Credentials")
    except Exception:
        _log.exception("Não foi possível inicializar o Firebase com %s.", cred_path)
        raise

_init_firebase()
_db = firestore.client()


class UserConfigManager:
    """Gerencia leitura/escrita/escuta de configs do usuário."""

    def __init__(self, user_id: str):
        if not user_id:
            raise ValueError("user_id não pode ser vazio")
        self.user_id = str(user_id)
        self.doc_ref = _db.collection("usr_config").document(self.user_id)
        self.config = {}
        # carregar a config apenas quando instancia (com logs)
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Carrega a config do Firestore. Se não existir, cria padrão (de forma atômica quando possível)."""
        _log.debug("Carregando config para user_id=%s", self.user_id)
        try:
            doc = self.doc_ref.get()
        except Exception:
            _log.exception("Erro ao obter documento para user_id=%s", self.user_id)
            raise

        if doc.exists:
            data = doc.to_dict() or {}
            _log.debug("Config encontrada para %s: %s", self.user_id, data)
            self.config = data
            return data

        # se não existir, criar padrão de forma segura
        default = {
            "theme": "light",
            "currency": "BRL",
            "timezone": "UTC-3",
            "avatar_color": "#7C3AED",
            "show_email": True,
            "show_birthdate": False,
        }

        _log.debug("Config não encontrada para %s. Tentando criar padrão.", self.user_id)
        try:
            # DocumentReference.create lança se o doc já existir; é atômico
            self.doc_ref.create(default)
            _log.info("Documento padrão criado para user_id=%s", self.user_id)
            self.config = default
            return default
        except Exception as e:
            # se falhar porque já existe (race), re-obter; caso contrário propagar
            _log.debug("create() falhou para %s: %s — tentando ler novamente", self.user_id, e)
            try:
                doc = self.doc_ref.get()
                if doc.exists:
                    data = doc.to_dict() or {}
                    _log.debug("Após erro, config encontrada para %s: %s", self.user_id, data)
                    self.config = data
                    return data
            except Exception:
                _log.exception("Erro ao re-obter documento após create falhar para %s", self.user_id)
                raise
            # se ainda nada, lançar
            _log.error("Não foi possível criar nem ler a config para %s", self.user_id)
            raise RuntimeError("Não foi possível criar nem ler a config do usuário.")

    def update_config(self, new_config: dict):
        """Atualiza config local e no Firebase (merge=True)."""
        if not isinstance(new_config, dict):
            raise ValueError("new_config deve ser um dict")
        _log.debug("Atualizando config localmente para %s: %s", self.user_id, new_config)
        self.config.update(new_config)
        try:
            self.doc_ref.set(self.config, merge=True)
            _log.debug("Config atualizada no Firestore para %s", self.user_id)
        except Exception:
            _log.exception("Erro ao atualizar config no Firestore para %s", self.user_id)
            raise

    def listen_config(self, callback):
        """Cria listener em tempo real. Callback recebe (config_dict)."""
        if not callable(callback):
            raise ValueError("callback deve ser callable")

        def _on_snapshot(doc_snapshot, changes, read_time):
            try:
                # doc_snapshot pode ser um DocumentSnapshot ou uma lista (dependendo da API/version)
                if isinstance(doc_snapshot, (list, tuple)):
                    snap = doc_snapshot[0] if doc_snapshot else None
                else:
                    snap = doc_snapshot
                if not snap:
                    _log.debug("Snapshot vazio recebido para %s", self.user_id)
                    return
                data = snap.to_dict()
                _log.debug("Snapshot recebido para %s: %s", self.user_id, data)
                # atualiza cache local
                self.config = data or {}
                callback(self.config)
            except Exception:
                _log.exception("Erro no snapshot callback para %s", self.user_id)

        registration = self.doc_ref.on_snapshot(_on_snapshot)
        _log.debug("Listener registrado para %s", self.user_id)
        return registration

    # Métodos de conveniência
    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value
        self.update_config({key: value})

    @classmethod
    def set_user_config(cls, user_id: str, new_config: dict):
        """Atualiza a config do usuário diretamente sem instanciar (evita leituras desnecessárias)."""
        if not user_id:
            raise ValueError("user_id não pode ser vazio")
        if not isinstance(new_config, dict):
            raise ValueError("new_config deve ser dict")
        doc_ref = _db.collection("usr_config").document(str(user_id))
        try:
            doc_ref.set(new_config, merge=True)
            _log.debug("set_user_config: atualizado user_id=%s com %s", user_id, new_config)
        except Exception:
            _log.exception("Erro em set_user_config para %s", user_id)
            raise
