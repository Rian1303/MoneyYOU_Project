from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QDateEdit
)
from PyQt6.QtCore import pyqtSignal, QDate

class TransactionForm(QWidget):
    transaction_added = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adicionar Transação")
        self.setMinimumSize(350, 300)

        # Categorias por tipo
        self.categories = {
            "Entrada": ["Salário", "Bolsa", "Outras Entradas"],
            "Saída": ["Alimentação", "Transporte", "Moradia", "Lazer", "Outras Saídas"]
        }

        self.setup_ui()
        self.update_category_options()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        form_layout = QVBoxLayout()

        # Descrição
        desc_layout = QHBoxLayout()
        desc_label = QLabel("Descrição:")
        desc_label.setMinimumWidth(80)
        self.desc_input = QLineEdit()
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        form_layout.addLayout(desc_layout)

        # Valor
        value_layout = QHBoxLayout()
        value_label = QLabel("Valor (R$):")
        value_label.setMinimumWidth(80)
        self.value_input = QLineEdit()
        value_layout.addWidget(value_label)
        value_layout.addWidget(self.value_input)
        form_layout.addLayout(value_layout)

        # Tipo
        type_layout = QHBoxLayout()
        type_label = QLabel("Tipo:")
        type_label.setMinimumWidth(80)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Entrada", "Saída"])
        self.type_combo.currentIndexChanged.connect(self.update_category_options)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        form_layout.addLayout(type_layout)

        # Categoria
        category_layout = QHBoxLayout()
        category_label = QLabel("Categoria:")
        category_label.setMinimumWidth(80)
        self.category_combo = QComboBox()
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        form_layout.addLayout(category_layout)

        # Data
        date_layout = QHBoxLayout()
        date_label = QLabel("Data:")
        date_label.setMinimumWidth(80)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        form_layout.addLayout(date_layout)

        main_layout.addLayout(form_layout)

        # Botões
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        add_btn = QPushButton("Adicionar")
        add_btn.clicked.connect(self.submit_transaction)
        button_layout.addWidget(add_btn)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def update_category_options(self):
        selected_type = self.type_combo.currentText()
        self.category_combo.clear()
        self.category_combo.addItems(self.categories.get(selected_type, []))

    def submit_transaction(self):
        desc = self.desc_input.text().strip()
        valor_text = self.value_input.text().strip()
        tipo = self.type_combo.currentText()
        categoria = self.category_combo.currentText()
        data = self.date_input.date().toString("dd/MM/yyyy")

        if not desc:
            QMessageBox.warning(self, "Erro", "Descrição não pode ficar vazia.")
            return

        try:
            valor = float(valor_text.replace(',', '.'))
            if valor <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Erro", "Informe um valor numérico positivo.")
            return

        transaction = {
            "type": tipo,
            "category": categoria,
            "amount": valor,
            "description": desc,
            "date": data
        }

        self.transaction_added.emit(transaction)
        self.close()
