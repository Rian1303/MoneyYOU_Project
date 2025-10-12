from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox,
    QCheckBox, QHBoxLayout, QStackedWidget, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont

from logic.usr_config import UserConfigManager
from logic.finance_logic import FinanceLogic
from logic.theme_manager import set_theme, get_theme
from logic.customize import Customize


class SettingsScreen(QWidget):
    # 🔹 Sinais para integração com o resto do app
    theme_changed = pyqtSignal(str)
    config_changed = pyqtSignal(str, object)  # (chave, valor)

    def __init__(self, user_id: str = "default_user"):
        super().__init__()
        self.user_id = user_id
        self.finance = FinanceLogic()
        self.user_config = UserConfigManager(self.user_id)

        self.setFont(Customize.app_font(10))
        self.init_ui()
        self.load_from_config(self.user_config.config)

    # ======================
    # UI
    # ======================
    def init_ui(self):
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # === Barra lateral ===
        self.sidebar = QListWidget()
        self.sidebar.addItem(QListWidgetItem("🎨 Aparência"))
        self.sidebar.addItem(QListWidgetItem("💰 Finanças"))
        self.sidebar.addItem(QListWidgetItem("⏱️ Tempo"))
        self.sidebar.setMaximumWidth(150)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: none;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #7C3AED;
                color: white;
            }
        """)
        layout.addWidget(self.sidebar)

        # === Área de conteúdo ===
        self.pages = QStackedWidget()
        layout.addWidget(self.pages)

        # === Páginas ===
        self.appearance_page = self._build_appearance_tab()
        self.finance_page = self._build_finance_tab()
        self.time_page = self._build_time_tab()

        self.pages.addWidget(self.appearance_page)
        self.pages.addWidget(self.finance_page)
        self.pages.addWidget(self.time_page)

        # Lógica: mudar página ao clicar na barra lateral
        self.sidebar.currentRowChanged.connect(self._animate_page_change)

    # ======================
    # Páginas de Configuração
    # ======================

    def _build_appearance_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("🎨 Aparência")
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

        layout.addStretch()
        return page

    def _build_finance_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("💰 Finanças")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Moeda padrão"))
        self.currency_cb = QComboBox()
        self.currency_cb.addItems(["BRL", "USD", "EUR", "JPY"])
        self.currency_cb.currentTextChanged.connect(self.on_currency_change)
        layout.addWidget(self.currency_cb)

        layout.addStretch()
        return page

    def _build_time_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("⏱️ Tempo e exibição")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Fuso horário"))
        self.tz_cb = QComboBox()
        self.tz_cb.addItems(["UTC-5", "UTC-3", "UTC+0", "UTC+1", "UTC+9"])
        self.tz_cb.currentTextChanged.connect(self.on_timezone_change)
        layout.addWidget(self.tz_cb)

        self.show_email_chk = QCheckBox("Mostrar email no perfil")
        self.show_email_chk.stateChanged.connect(
            lambda _: self.on_flag_change("show_email", self.show_email_chk.isChecked())
        )
        layout.addWidget(self.show_email_chk)

        self.show_birth_chk = QCheckBox("Mostrar data de nascimento")
        self.show_birth_chk.stateChanged.connect(
            lambda _: self.on_flag_change("show_birthdate", self.show_birth_chk.isChecked())
        )
        layout.addWidget(self.show_birth_chk)

        layout.addStretch()
        return page

    # ======================
    # Lógica de Configuração
    # ======================

    def load_from_config(self, cfg: dict):
        theme = cfg.get("theme", get_theme())
        currency = self.user_config.get("currency", "BRL")
        tz = cfg.get("timezone", "UTC-3")
        show_email = bool(cfg.get("show_email", True))
        show_birth = bool(cfg.get("show_birthdate", False))

        idx = self.currency_cb.findText(currency)
        if idx >= 0:
            self.currency_cb.setCurrentIndex(idx)
        idx = self.tz_cb.findText(tz)
        if idx >= 0:
            self.tz_cb.setCurrentIndex(idx)
        self.show_email_chk.setChecked(show_email)
        self.show_birth_chk.setChecked(show_birth)

        set_theme(theme)

    # === Ações ===
    def on_theme_change(self, theme_name: str):
        self.user_config.set("theme", theme_name)
        Customize.apply_theme(theme_name)
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

    # === Animação suave na troca de aba ===
    def _animate_page_change(self, index):
        self.pages.setCurrentIndex(index)
        animation = QPropertyAnimation(self.pages, b"windowOpacity")
        animation.setDuration(250)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()
