from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt

class TransactionCard(QWidget):
    def __init__(self, desc: str, valor: float, tipo: str):
        super().__init__()
        self.desc = desc
        self.valor = valor
        self.tipo = tipo
        self.init_ui()

    def init_ui(self):
        # Layout principal horizontal
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Coluna descrição e tipo
        text_layout = QVBoxLayout()
        desc_label = QLabel(self.desc)
        desc_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        tipo_label = QLabel(self.tipo)
        tipo_label.setStyleSheet("color: gray; font-size: 12px;")
        text_layout.addWidget(desc_label)
        text_layout.addWidget(tipo_label)

        layout.addLayout(text_layout)

        # Valor alinhado à direita
        valor_label = QLabel(f"R$ {self.valor:.2f}")
        valor_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        valor_label.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {self.get_color()};")
        layout.addWidget(valor_label)

        self.setLayout(layout)
        self.setFixedHeight(60)

        # Estilo de fundo (leve sombra e cor dependendo do tipo)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#F0F0F0"))
        self.setPalette(palette)
        self.setStyleSheet("border-radius: 8px;")

    def get_color(self):
        # Cor verde para receita, vermelho para despesa
        if self.tipo.lower() == "receita":
            return "#2E8B57"  # verde escuro
        else:
            return "#B22222"  # vermelho escuro
