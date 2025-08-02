from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from ui.transaction_form import TransactionForm

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DashboardWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"Dashboard - Organizador Financeiro - {username}")
        self.setMinimumSize(800, 600)  # tamanho mínimo adequado para o layout

        self.transactions = []  # lista de transações inicial vazia

        self.init_ui()

    def init_ui(self):
        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setContentsMargins(12, 12, 12, 12)
        main_vertical_layout.setSpacing(8)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)

        # Grupo do gráfico (lado esquerdo)
        self.chart_group = QGroupBox("Resumo Financeiro")
        chart_layout = QVBoxLayout()
        self.chart_canvas = FigureCanvas(Figure(figsize=(5, 4)))
        chart_layout.addWidget(self.chart_canvas)
        self.chart_group.setLayout(chart_layout)

        # Grupo das transações e botões (lado direito)
        self.transactions_group = QGroupBox("Transações")
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        self.balance_label = QLabel("Saldo: R$ 0,00")
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        right_layout.addWidget(self.balance_label)

        self.add_transaction_btn = QPushButton("Adicionar Transação")
        self.add_transaction_btn.clicked.connect(self.open_transaction_form)
        right_layout.addWidget(self.add_transaction_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Data", "Descrição", "Valor", "Tipo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)  # esconder numeração das linhas
        self.table.setAlternatingRowColors(True)
        right_layout.addWidget(self.table)

        self.transactions_group.setLayout(right_layout)

        main_layout.addWidget(self.chart_group, 3)   # 3/8 da largura total
        main_layout.addWidget(self.transactions_group, 5)  # 5/8 da largura total

        main_vertical_layout.addLayout(main_layout)

        # Rodapé com direitos reservados
        footer_label = QLabel("Direitos Reservados à Croma Company - Departamento de Softwares")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setObjectName("footerLabel")
        footer_label.setStyleSheet("color: gray; font-size: 10px; margin-top: 10px;")
        main_vertical_layout.addWidget(footer_label)

        self.setLayout(main_vertical_layout)

        # Atualiza o dashboard ao iniciar
        self.update_dashboard()

    def update_dashboard(self):
        self.load_transactions()
        self.update_balance()
        self.update_chart()

    def load_transactions(self):
        self.table.setRowCount(len(self.transactions))
        for row, tx in enumerate(self.transactions):
            data_text = tx.get("data", "")
            self.table.setItem(row, 0, QTableWidgetItem(data_text))
            self.table.setItem(row, 1, QTableWidgetItem(tx["desc"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"R$ {tx['valor']:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(tx["tipo"]))

    def update_balance(self):
        saldo = 0
        for tx in self.transactions:
            if tx["tipo"].lower() == "receita":
                saldo += tx["valor"]
            else:
                saldo -= tx["valor"]
        self.balance_label.setText(f"Saldo: R$ {saldo:.2f}")

    def update_chart(self):
        self.chart_canvas.figure.clear()
        ax = self.chart_canvas.figure.add_subplot(111)

        receita = sum(tx["valor"] for tx in self.transactions if tx["tipo"].lower() == "receita")
        despesa = sum(tx["valor"] for tx in self.transactions if tx["tipo"].lower() == "despesa")

        categories = ['Receitas', 'Despesas']
        values = [receita, despesa]
        colors = ['#10B981', '#EF4444']

        ax.bar(categories, values, color=colors)
        ax.set_title("Resumo de Receitas vs Despesas")
        ax.set_ylabel("Valor (R$)")
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        self.chart_canvas.draw()

    def open_transaction_form(self):
        self.form = TransactionForm()
        self.form.transaction_added.connect(self.handle_new_transaction)
        self.form.show()

    def handle_new_transaction(self, transaction):
        self.transactions.append(transaction)
        self.update_dashboard()
        QMessageBox.information(self, "Sucesso", "Transação adicionada com sucesso!")
 