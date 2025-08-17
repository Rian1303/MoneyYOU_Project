import sys
import os
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from ui.login_screen import LoginScreen
from ui.dashboard import DashboardWindow
from ui.register_window import RegisterWindow
import config
from logic.auth import create_master_user

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.apply_stylesheet()
        icon_path = config.ICONS_DIR / "app_icon.png"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))

        # Criar janelas
        self.login_window = LoginScreen()
        self.login_window.login_success.connect(self.show_dashboard)
        self.login_window.open_register.connect(self.show_register)

        self.dashboard_window = None
        self.register_window = None

        self.login_window.show()
        sys.exit(self.app.exec())

    def apply_stylesheet(self):
        try:
            with open(config.STYLE_PATH, "r") as f:
                self.app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Falha ao carregar estilo: {e}")

    def show_dashboard(self, username):
        self.login_window.close()
        self.dashboard_window = DashboardWindow(username)
        self.dashboard_window.show()

    def show_register(self):
        if not self.register_window:
            self.register_window = RegisterWindow()
            self.register_window.user_registered.connect(self.handle_new_user)
            self.register_window.show()
        else:
            self.register_window.raise_()
            self.register_window.activateWindow()

    def handle_new_user(self, username, _):
        # Apenas fecha janela após cadastro com sucesso
        self.login_window.show()
        self.register_window.close()
        self.register_window = None

if __name__ == "__main__":
    AppController()
