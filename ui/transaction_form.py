from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

class TransactionForm(QWidget):
    transaction_added = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adicionar Transação")
        self.setMinimumWidth(300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Descrição
        layout.addWidget(QLabel("Descrição:"))
        self.desc_input = QLineEdit()
        layout.addWidget(self.desc_input)

        # Tipo: entrada ou saída
        layout.addWidget(QLabel("Tipo:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["entrada", "saída"])
        self.type_combo.currentTextChanged.connect(self.update_categories)
        layout.addWidget(self.type_combo)

        # Categoria (depende do tipo)
        layout.addWidget(QLabel("Categoria:"))
        self.category_combo = QComboBox()
        layout.addWidget(self.category_combo)

        # Valor
        layout.addWidget(QLabel("Valor:"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Ex: 100.00")
        layout.addWidget(self.amount_input)

        # Botão adicionar
        add_btn = QPushButton("Adicionar")
        add_btn.clicked.connect(self.add_transaction)
        layout.addWidget(add_btn)

        self.setLayout(layout)

        # Inicializa categorias
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

        # Validações básicas
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

        transaction = {
            "desc": desc,
            "type": tipo,
            "category": categoria,
            "amount": amount,
            # Data você pode pegar aqui, se quiser (ex: datetime.now())
        }

        self.transaction_added.emit(transaction)
        self.close()
