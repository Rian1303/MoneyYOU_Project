import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.login_screen import LoginScreen
from ui.dashboard import DashboardWindow
from ui.register_window import RegisterWindow
import config
from logic.theme_manager import load_theme_qss


class AppController:
    def __init__(self, app: QApplication):
        self.app = app

        # Carregar tema global (dark/light)
        self.apply_theme()

        # Definir ícone global do app
        icon_path = config.ICONS_DIR / "app_icon.png"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))

        # Criar janelas principais
        self.login_window = LoginScreen()
        self.dashboard_window = None
        self.register_window = None

        # Conectar sinais
        self.login_window.login_success.connect(self.show_dashboard)
        self.login_window.open_register.connect(self.show_register)

        # Exibir tela inicial
        self.login_window.show()

    def apply_theme(self):
        """Aplica o tema global configurado pelo usuário."""
        try:
            theme_qss = load_theme_qss()  # Retorna o conteúdo QSS do tema atual
            with open(config.STYLE_PATH, "r", encoding="utf-8") as base_style:
                base_qss = base_style.read()

            # Aplica o tema principal + tema customizado
            self.app.setStyleSheet(base_qss + "\n" + theme_qss)
        except Exception as e:
            print(f"Falha ao carregar tema: {e}")

    def show_dashboard(self, username: str):
        """Fecha o login e abre o painel principal."""
        self.login_window.close()
        self.dashboard_window = DashboardWindow(username)
        self.dashboard_window.show()

    def show_register(self):
        """Abre a janela de registro."""
        self.register_window = RegisterWindow()
        self.register_window.user_registered.connect(self.handle_new_user)
        self.register_window.show()

    def handle_new_user(self, username: str):
        """Executado quando um novo usuário é criado."""
        print(f"Novo usuário registrado: {username}")
        QMessageBox.information(
            self.login_window,
            "Sucesso",
            f"Usuário '{username}' registrado! Agora faça login."
        )
        self.login_window.user_input.setText(username)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = AppController(app)
    sys.exit(app.exec())
