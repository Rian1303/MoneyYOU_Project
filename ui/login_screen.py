from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QGroupBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from logic.auth import validate_login

class LoginScreen(QWidget):
    login_success = pyqtSignal(str)
    open_register = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - MoneyYOU")
        self.setMinimumSize(900, 650)  # Tamanho da dashboard
        self.setup_ui()

    def setup_ui(self):
        # Layout principal (vertical) para centralizar o painel
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Spacer superior para centralizar verticalmente
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Painel de login
        login_box = QGroupBox()
        login_box.setTitle("💰 MoneyYOU Login")
        login_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_box.setStyleSheet("""
            QGroupBox {
                font-size: 16pt;
                font-weight: bold;
                border: 2px solid #7C3AED;
                border-radius: 15px;
                margin-top: 20px;
                background-color: #F9FAFB;
            }
        """)
        login_layout = QVBoxLayout()
        login_layout.setContentsMargins(40, 40, 40, 40)
        login_layout.setSpacing(20)

        # Usuário
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuário")
        login_layout.addWidget(QLabel("Usuário:"))
        login_layout.addWidget(self.user_input)

        # Senha
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Senha")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(QLabel("Senha:"))
        login_layout.addWidget(self.pass_input)

        # Botões
        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.register_btn = QPushButton("Registrar")
        self.login_btn.setStyleSheet("background-color: #7C3AED; color: white; font-weight: bold;")
        self.register_btn.setStyleSheet("background-color: #A855F7; color: white; font-weight: bold;")
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.register_btn)
        login_layout.addLayout(btn_layout)

        login_box.setLayout(login_layout)
        main_layout.addWidget(login_box, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer inferior
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(main_layout)

        # Conexões
        self.login_btn.clicked.connect(self.check_login)
        self.register_btn.clicked.connect(self.open_register.emit)

        # Enter também aciona login
        self.user_input.returnPressed.connect(self.login_btn.click)
        self.pass_input.returnPressed.connect(self.login_btn.click)
        self.login_btn.setDefault(True)

    def check_login(self):
        user = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not user or not password:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        try:
            if validate_login(user, password):
                self.login_success.emit(user)
            else:
                QMessageBox.warning(self, "Erro", "Usuário ou senha inválidos.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao verificar login:\n{str(e)}")
