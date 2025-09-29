from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from logic.auth import validate_registration, register_user

class RegisterWindow(QWidget):
    user_registered = pyqtSignal(str)  # Sinal que emite o username registrado

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar - MoneyYOU")
        self.setMinimumSize(400, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("Criar Conta")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)

        # Campos
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.user_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Senha")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.pass_input)

        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setPlaceholderText("Confirmar Senha")
        self.confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Confirmar Senha:"))
        layout.addWidget(self.confirm_pass_input)

        # Botões
        btn_layout = QHBoxLayout()
        self.register_btn = QPushButton("Registrar")
        self.cancel_btn = QPushButton("Cancelar")
        self.register_btn.setStyleSheet("background-color: #7C3AED; color: white; font-weight: bold;")
        self.cancel_btn.setStyleSheet("background-color: #A855F7; color: white; font-weight: bold;")
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.register_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Conexões
        self.register_btn.clicked.connect(self.attempt_register)
        self.cancel_btn.clicked.connect(self.close)

    def attempt_register(self):
        username = self.user_input.text().strip()
        email = self.email_input.text().strip()
        password = self.pass_input.text().strip()
        confirm = self.confirm_pass_input.text().strip()

        valid, msg = validate_registration(username, password, confirm, email)
        if not valid:
            QMessageBox.warning(self, "Erro", msg)
            return

        try:
            register_user(username, password, email)
            QMessageBox.information(self, "Sucesso", "Usuário registrado com sucesso!")
            self.user_registered.emit(username)  # emite o sinal
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao registrar usuário: {str(e)}")
