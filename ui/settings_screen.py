from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from logic.theme_manager import set_theme, load_theme
from PyQt6.QtCore import pyqtSignal

class SettingsScreen(QWidget):
    # Signal que vai emitir o tema selecionado: "light" ou "dark"
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None, current_theme="light"):
        super().__init__(parent)
        self.current_theme = current_theme

        layout = QVBoxLayout(self)

        # Título
        title = QLabel("⚙️ Configurações")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Seção de Login (ilustrativa)
        login_label = QLabel("🔑 Login e Conta (em breve)")
        layout.addWidget(login_label)

        # Seção de Idioma (ilustrativa)
        lang_label = QLabel("🌍 Idioma (em breve)")
        layout.addWidget(lang_label)

        # Seção de Moeda (ilustrativa)
        currency_label = QLabel("💰 Moeda (em breve)")
        layout.addWidget(currency_label)

        # Seção de Preferências (tema já funcionando)
        pref_label = QLabel("🎨 Preferências")
        layout.addWidget(pref_label)

        # Botões de Tema
        theme_layout = QHBoxLayout()
        self.light_btn = QPushButton("Modo Claro")
        self.dark_btn = QPushButton("Modo Escuro")

        self.light_btn.clicked.connect(lambda: self.change_theme("light"))
        self.dark_btn.clicked.connect(lambda: self.change_theme("dark"))

        theme_layout.addWidget(self.light_btn)
        theme_layout.addWidget(self.dark_btn)
        layout.addLayout(theme_layout)

        # Define o tema inicial
        self.apply_theme(current_theme)

        layout.addStretch()

    def change_theme(self, theme_name):
        set_theme(theme_name)  # Atualiza o tema no sistema
        self.apply_theme(theme_name)
        self.theme_changed.emit(theme_name)  # Notifica o Dashboard

    def apply_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet("background-color: #1E1E1E; color: #F9FAFB;")
        else:
            self.setStyleSheet("background-color: #F9FAFB; color: #1E1E1E;")
