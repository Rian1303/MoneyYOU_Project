# ui/transaction_form.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QMessageBox, QDateEdit, QFrame
)
from PyQt6.QtCore import pyqtSignal, QDate, Qt
from datetime import datetime
import uuid

from database.data_manager import add_transaction  # Apenas Firebase agora
from logic.finance_logic import FinanceLogic


class TransactionForm(QWidget):
    transaction_added = pyqtSignal(dict)  # Emite o dict completo após salvar

    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("➕ Adicionar Transação - MoneyYOU")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QWidget { background-color: #F9FAFB; font-family: Arial; font-size: 11pt; }
            QLabel { font-weight: bold; }
            QLineEdit, QComboBox, QDateEdit { padding: 5px; border: 1px solid #ccc; border-radius: 4px; }
            QPushButton { padding: 6px 12px; border-radius: 5px; font-weight: bold; }
            QPushButton#add_btn { background-color: #7C3AED; color: white; }
            QPushButton#cancel_btn { background-color: #A0A0A0; color: white; }
        """)

        # 🔹 FinanceLogic para conversão (mesmo que agora seja apenas Firebase)
        self.finance = FinanceLogic()
        self.user_currency = "BRL"  # Por enquanto fixo; pode puxar da configuração do usuário

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title = QLabel("Adicionar Transação")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Linha separadora
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Descrição
        layout.addWidget(QLabel("Descrição:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Ex: Salário, Aluguel, Presente")
        layout.addWidget(self.desc_input)

        # Tipo
        layout.addWidget(QLabel("Tipo:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["entrada", "saída"])
        self.type_combo.currentTextChanged.connect(self.update_categories)
        layout.addWidget(self.type_combo)

        # Categoria
        layout.addWidget(QLabel("Categoria:"))
        self.category_combo = QComboBox()
        layout.addWidget(self.category_combo)

        # Valor
        layout.addWidget(QLabel(f"Valor ({self.user_currency}):"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Ex: 100.00")
        layout.addWidget(self.amount_input)

        # Data
        layout.addWidget(QLabel("Data:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit)

        # Recorrência
        layout.addWidget(QLabel("Recorrência:"))
        self.recurrence_combo = QComboBox()
        self.recurrence_combo.addItems(["Única", "Diária", "Semanal", "Mensal", "Anual"])
        layout.addWidget(self.recurrence_combo)

        # Botões
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Adicionar")
        self.add_btn.setObjectName("add_btn")
        self.add_btn.clicked.connect(self.add_transaction)

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.update_categories(self.type_combo.currentText())

    def update_categories(self, tipo: str):
        self.category_combo.clear()
        if tipo == "entrada":
            categorias = ["Salário", "Presente", "Outros"]
        else:
            categorias = ["Aluguel", "Alimentação", "Transporte", "Contas", "Lazer", "Outros"]
        self.category_combo.addItems(categorias)

    def add_transaction(self):
        desc = self.desc_input.text().strip()
        tipo = self.type_combo.currentText()
        categoria = self.category_combo.currentText()
        amount_text = self.amount_input.text().strip()
        data = self.date_edit.date().toPyDate()
        recurrence = self.recurrence_combo.currentText()

        # 🔹 Validações
        if not desc:
            QMessageBox.warning(self, "Erro", "Descrição é obrigatória.")
            return
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valor inválido. Informe um número positivo.")
            return

        # 🔹 Converte valor para a moeda atual (mesmo que BRL)
        converted_amount = self.finance.convert_currency(amount, self.user_currency, self.user_currency)

        # 🔹 Cria transação
        transaction = {
            "user_id": self.user_id,
            "desc": desc,
            "type": tipo,
            "category": categoria,
            "amount": converted_amount,
            "date": data.strftime("%d/%m/%Y"),
            "recurrence": recurrence,
            "currency": self.user_currency,
            "id": str(uuid.uuid4())  # ID temporário
        }

        # 🔹 Salva no Firebase
        firebase_id = add_transaction(transaction)
        transaction["id"] = firebase_id

        # 🔹 Emite evento para atualizar Dashboard
        self.transaction_added.emit(transaction)

        # 🔹 Fecha o formulário
        self.close()
