from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette

class TransactionCard(QWidget):
    transaction_updated = pyqtSignal(dict)
    transaction_deleted = pyqtSignal(dict)

    def __init__(self, transaction, dark_mode=False):
        super().__init__()
        self.transaction = transaction
        self.dark_mode = dark_mode
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(15)

        # Indicador de tipo de transação
        self.type_label = QLabel(self.transaction.get("type", ""))
        self.type_label.setFixedWidth(60)
        self.type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.type_label)

        # Descrição e categoria
        info_layout = QVBoxLayout()
        self.desc_label = QLabel(self.transaction.get("desc", ""))
        self.category_label = QLabel(self.transaction.get("category", ""))
        info_layout.addWidget(self.desc_label)
        info_layout.addWidget(self.category_label)
        main_layout.addLayout(info_layout)

        # Valor
        self.amount_label = QLabel(f"R$ {self.transaction.get('amount', 0):.2f}")
        self.amount_label.setFixedWidth(80)
        self.amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.amount_label)

        # Recorrência
        recurrence_layout = QVBoxLayout()
        recurrence_label = QLabel("Recorrência:")
        self.recurrence_combo = QComboBox()
        self.recurrence_combo.addItems(["Nenhuma", "Diário", "Semanal", "Mensal", "Anual"])
        # Seleciona a recorrência atual
        current_recurrence = self.transaction.get("recurrence", "Nenhuma")
        index = self.recurrence_combo.findText(current_recurrence)
        if index >= 0:
            self.recurrence_combo.setCurrentIndex(index)
        recurrence_layout.addWidget(recurrence_label)
        recurrence_layout.addWidget(self.recurrence_combo)
        main_layout.addLayout(recurrence_layout)

        # Botões de ação
        btn_layout = QVBoxLayout()
        self.update_btn = QPushButton("Atualizar")
        self.update_btn.clicked.connect(self.update_transaction)
        self.delete_btn = QPushButton("Excluir")
        self.delete_btn.clicked.connect(self.delete_transaction)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #1E1E1E;
                    color: #F9FAFB;
                    border: 1px solid #333;
                    border-radius: 5px;
                }
                QComboBox {
                    background-color: #2C2C2C;
                    color: #F9FAFB;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #F9FAFB;
                    color: #1E1E1E;
                    border: 1px solid #CCC;
                    border-radius: 5px;
                }
                QComboBox {
                    background-color: #FFFFFF;
                    color: #1E1E1E;
                }
            """)

    def update_transaction(self):
        # Atualiza a transação com a recorrência selecionada
        self.transaction["recurrence"] = self.recurrence_combo.currentText()
        self.transaction_updated.emit(self.transaction)

    def delete_transaction(self):
        self.transaction_deleted.emit(self.transaction)
