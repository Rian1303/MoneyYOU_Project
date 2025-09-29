# ui/update_pass.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from logic.auth import change_password, MIN_PASSWORD_LENGTH

class UpdatePasswordWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Redefinir Senha - MoneyYOU")
        self.setMinimumSize(450, 350)
        self.setStyleSheet("background-color: #F9FAFB;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Título
        title = QLabel("🔒 Redefinir Senha")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #7C3AED;")
        layout.addWidget(title)

        # Username
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Digite seu username")
        self.user_input.setStyleSheet("padding: 8px; font-size: 12pt; border-radius: 5px; border: 1px solid #A855F7;")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.user_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Digite seu email cadastrado")
        self.email_input.setStyleSheet("padding: 8px; font-size: 12pt; border-radius: 5px; border: 1px solid #A855F7;")
        layout.addWidget(QLabel("Email cadastrado:"))
        layout.addWidget(self.email_input)

        # Nova senha
        self.new_pass_input = QLineEdit()
        self.new_pass_input.setPlaceholderText("Nova senha")
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setStyleSheet("padding: 8px; font-size: 12pt; border-radius: 5px; border: 1px solid #A855F7;")
        layout.addWidget(QLabel("Nova Senha:"))
        layout.addWidget(self.new_pass_input)

        # Confirmar senha
        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setPlaceholderText("Confirme a nova senha")
        self.confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pass_input.setStyleSheet("padding: 8px; font-size: 12pt; border-radius: 5px; border: 1px solid #A855F7;")
        layout.addWidget(QLabel("Confirmar Senha:"))
        layout.addWidget(self.confirm_pass_input)

        # Mostrar senha
        self.show_pass_checkbox = QCheckBox("Mostrar senhas")
        self.show_pass_checkbox.setStyleSheet("font-size: 10pt; color: #1E1E1E;")
        self.show_pass_checkbox.stateChanged.connect(self.toggle_show_password)
        layout.addWidget(self.show_pass_checkbox)

        # Botões
        btn_layout = QHBoxLayout()
        self.update_btn = QPushButton("Atualizar")
        self.cancel_btn = QPushButton("Cancelar")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #7C3AED; color: white; font-weight: bold; padding: 8px; border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #A855F7;
            }
        """)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981; color: white; font-weight: bold; padding: 8px; border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Conexões
        self.update_btn.clicked.connect(self.attempt_update)
        self.cancel_btn.clicked.connect(self.close)

    def toggle_show_password(self, state):
        if state == Qt.CheckState.Checked.value:
            self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)

    def attempt_update(self):
        username = self.user_input.text().strip()
        email = self.email_input.text().strip()
        new_pass = self.new_pass_input.text().strip()
        confirm_pass = self.confirm_pass_input.text().strip()

        if not username or not email or not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Erro", "As senhas não coincidem.")
            return

        if len(new_pass) < MIN_PASSWORD_LENGTH:
            QMessageBox.warning(self, "Erro", f"A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres.")
            return

        success = change_password(username, email, new_pass)
        if success:
            QMessageBox.information(self, "Sucesso", "Senha atualizada com sucesso.")
            self.close()
        else:
            QMessageBox.critical(self, "Erro", "Falha ao atualizar senha. Verifique username/email.")
