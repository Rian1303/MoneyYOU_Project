from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal
from logic.auth import validate_login

class LoginScreen(QWidget):
    login_success = pyqtSignal(str)
    open_register = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_btn = QPushButton("Login")
        register_btn = QPushButton("Registrar")

        login_btn.clicked.connect(self.check_login)
        register_btn.clicked.connect(self.open_register.emit)

        layout.addWidget(QLabel("Usuário:"))
        layout.addWidget(self.user_input)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.pass_input)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def check_login(self):
        user = self.user_input.text()
        password = self.pass_input.text()

        if validate_login(user, password):
            self.login_success.emit(user)
        else:
            QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")
