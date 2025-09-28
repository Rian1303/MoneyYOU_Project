from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QMessageBox, QDateEdit
)
from PyQt6.QtCore import pyqtSignal, QDate
from datetime import datetime
import uuid

from database.data_manager import add_transaction  # Salva no Firebase + SQLite
from logic.usr_config import UserConfigManager
from logic.finance_logic import FinanceLogic


class TransactionForm(QWidget):
    transaction_added = pyqtSignal(dict)  # Emite o dict completo

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Adicionar Transação")
        self.setMinimumWidth(350)

        # 🔹 Configuração do usuário
        self.config_manager = UserConfigManager(user_id)
        self.user_currency = self.config_manager.get("currency") or "BRL"

        # 🔹 FinanceLogic para conversão de moeda
        self.finance = FinanceLogic()

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Descrição
        layout.addWidget(QLabel("Descrição:"))
        self.desc_input = QLineEdit()
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

        # Botão adicionar
        add_btn = QPushButton("Adicionar")
        add_btn.clicked.connect(self.add_transaction)
        layout.addWidget(add_btn)

        self.setLayout(layout)
        self.update_categories(self.type_combo.currentText())

    def update_categories(self, tipo):
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

        # 🔹 Converte valor para a moeda atual (se necessário)
        converted_amount = self.finance.convert_currency(amount, self.user_currency, self.user_currency)

        # 🔹 Gera ID temporário
        transaction_id = str(uuid.uuid4())

        transaction = {
            "id": transaction_id,
            "user_id": self.user_id,
            "desc": desc,
            "type": tipo,
            "category": categoria,
            "amount": converted_amount,
            "date": data.strftime("%d/%m/%Y"),
            "recurrence": recurrence,
            "currency": self.user_currency
        }

        # 🔹 Salva no Firebase + SQLite
        firebase_id = add_transaction(transaction)
        transaction["id"] = firebase_id

        # 🔹 Emite para atualizar o Dashboard
        self.transaction_added.emit(transaction)

        # Fecha o form
        self.close()

    def closeEvent(self, event):
        event.accept()
