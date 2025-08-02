# ui/widgets/transaction_card.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

class TransactionCard(QWidget):
    def __init__(self, transaction):
        super().__init__()
        self.transaction = transaction
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        # Descrição e Data
        top_layout = QHBoxLayout()
        desc_label = QLabel(self.transaction.get("desc", "Sem descrição"))
        desc_label.setStyleSheet("font-weight: bold")
        date_label = QLabel(self.transaction.get("data", "--/--/----"))
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        date_label.setStyleSheet("color: gray; font-size: 10px;")
        top_layout.addWidget(desc_label)
        top_layout.addStretch()
        top_layout.addWidget(date_label)

        # Valor
        valor = self.transaction.get("valor", 0.0)
        valor_label = QLabel(f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        tipo = self.transaction.get("tipo", "").lower()
        if tipo == "receita":
            valor_label.setStyleSheet("color: green; font-size: 14px;")
        else:
            valor_label.setStyleSheet("color: red; font-size: 14px;")

        layout.addLayout(top_layout)
        layout.addWidget(valor_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #f0f0f0; border-radius: 10px;")
