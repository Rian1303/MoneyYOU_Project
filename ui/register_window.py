from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal
from logic.auth import register_user as auth_register_user  # Função para registrar no banco

class RegisterWindow(QWidget):
    user_registered = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registrar Novo Usuário")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_confirm_input = QLineEdit()
        self.pass_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

        register_btn = QPushButton("Registrar")
        register_btn.clicked.connect(self.register_user)

        layout.addWidget(QLabel("Novo usuário:"))
        layout.addWidget(self.user_input)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.pass_input)
        layout.addWidget(QLabel("Confirmar senha:"))
        layout.addWidget(self.pass_confirm_input)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def register_user(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text()
        password_confirm = self.pass_confirm_input.text()

        if not username:
            QMessageBox.warning(self, "Erro", "Usuário não pode ser vazio.")
            return
        if password != password_confirm:
            QMessageBox.warning(self, "Erro", "As senhas não coincidem.")
            return
        if len(password) < 4:
            QMessageBox.warning(self, "Erro", "Senha deve ter no mínimo 4 caracteres.")
            return

        try:
            auth_register_user(username, password)
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
            return

        QMessageBox.information(self, "Sucesso", "Usuário registrado com sucesso!")
        self.user_registered.emit(username, password)
        self.close()
