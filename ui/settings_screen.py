# ui/settings_screen.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QCheckBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from logic.usr_config import UserConfigManager
from logic.finance_logic import FinanceLogic
from logic.theme_manager import set_theme, get_theme

class SettingsScreen(QWidget):
    theme_changed = pyqtSignal(str)
    config_changed = pyqtSignal(str, object)  # (chave, valor)

    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id
        self.finance = FinanceLogic()
        # Cria instância do config do usuário
        self.user_config = UserConfigManager(self.user_id)

        self.init_ui()
        self.load_from_config(self.user_config.config)

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("⚙️ Configurações")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)

        # Tema
        tbox = QHBoxLayout()
        self.light_btn = QPushButton("Modo Claro")
        self.dark_btn = QPushButton("Modo Escuro")
        self.light_btn.clicked.connect(lambda: self.on_theme_change("light"))
        self.dark_btn.clicked.connect(lambda: self.on_theme_change("dark"))
        tbox.addWidget(self.light_btn)
        tbox.addWidget(self.dark_btn)
        layout.addLayout(tbox)

        # Moeda
        layout.addWidget(QLabel("💰 Moeda padrão"))
        self.currency_cb = QComboBox()
        self.currency_cb.addItems(["BRL", "USD", "EUR", "JPY"])
        self.currency_cb.currentTextChanged.connect(self.on_currency_change)
        layout.addWidget(self.currency_cb)

        # Timezone
        layout.addWidget(QLabel("⏱️ Fuso horário"))
        self.tz_cb = QComboBox()
        self.tz_cb.addItems(["UTC-5", "UTC-3", "UTC+0", "UTC+1", "UTC+9"])
        self.tz_cb.currentTextChanged.connect(self.on_timezone_change)
        layout.addWidget(self.tz_cb)

        # Mostrar email/data
        self.show_email_chk = QCheckBox("Mostrar email no perfil")
        self.show_email_chk.stateChanged.connect(lambda _: self.on_flag_change("show_email", self.show_email_chk.isChecked()))
        layout.addWidget(self.show_email_chk)

        self.show_birth_chk = QCheckBox("Mostrar data de nascimento")
        self.show_birth_chk.stateChanged.connect(lambda _: self.on_flag_change("show_birthdate", self.show_birth_chk.isChecked()))
        layout.addWidget(self.show_birth_chk)

        layout.addStretch()
        self.setLayout(layout)

    def load_from_config(self, cfg: dict):
        # preencher controles com config existente
        theme = cfg.get("theme", get_theme())
        currency = self.user_config.get("currency", "BRL")
        tz = cfg.get("timezone", "UTC-3")
        show_email = bool(cfg.get("show_email", True))
        show_birth = bool(cfg.get("show_birthdate", False))

        # Selecionar sem disparar handlers demais:
        idx = self.currency_cb.findText(currency)
        if idx >= 0:
            self.currency_cb.setCurrentIndex(idx)
        idx = self.tz_cb.findText(tz)
        if idx >= 0:
            self.tz_cb.setCurrentIndex(idx)
        self.show_email_chk.setChecked(show_email)
        self.show_birth_chk.setChecked(show_birth)

        # aplica tema visual imediato
        set_theme(theme)

    # handlers
    def on_theme_change(self, theme_name: str):
        self.user_config.set("theme", theme_name)
        self.theme_changed.emit(theme_name)
        self.config_changed.emit("theme", theme_name)

    def on_currency_change(self, new_currency: str):
        self.user_config.set("currency", new_currency)
        self.config_changed.emit("currency", new_currency)

    def on_timezone_change(self, new_tz: str):
        self.user_config.set("timezone", new_tz)
        self.config_changed.emit("timezone", new_tz)

    def on_flag_change(self, key: str, value):
        self.user_config.set(key, value)
        self.config_changed.emit(key, value)
