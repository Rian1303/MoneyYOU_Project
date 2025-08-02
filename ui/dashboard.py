from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from ui.transaction_form import TransactionForm

# Import matplotlib para gráficos
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DashboardWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"Dashboard - Organizador Financeiro - {username}")
        self.setMinimumSize(800, 600)

        self.transactions = []  # começa vazia

        self.init_ui()

    def init_ui(self):
        # Layout geral vertical para permitir rodapé embaixo
        main_vertical_layout = QVBoxLayout()

        # Layout geral horizontal: esquerda gráfico, direita lista + botões
        main_layout = QHBoxLayout()

        # === Seção do gráfico (esquerda) ===
        self.chart_group = QGroupBox("Resumo Financeiro")
        chart_layout = QVBoxLayout()
        self.chart_canvas = FigureCanvas(Figure(figsize=(5, 4)))
        chart_layout.addWidget(self.chart_canvas)
        self.chart_group.setLayout(chart_layout)

        # === Seção da lista de transações e botões (direita) ===
        self.transactions_group = QGroupBox("Transações")
        right_layout = QVBoxLayout()

        # Saldo total
        self.balance_label = QLabel("Saldo: R$ 0,00")
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.balance_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        right_layout.addWidget(self.balance_label)

        # Botão adicionar
        self.add_transaction_btn = QPushButton("Adicionar Transação")
        self.add_transaction_btn.clicked.connect(self.open_transaction_form)
        right_layout.addWidget(self.add_transaction_btn)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Descrição", "Valor", "Tipo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.table)

        self.transactions_group.setLayout(right_layout)

        # Adicionar grupos ao layout horizontal principal
        main_layout.addWidget(self.chart_group, 3)   # ocupa 3 partes do espaço
        main_layout.addWidget(self.transactions_group, 5)  # 5 partes do espaço

        # Adiciona o layout horizontal no layout vertical principal
        main_vertical_layout.addLayout(main_layout)

        # Rodapé com direitos reservados
        footer_label = QLabel("Direitos Reservados à Croma Company - Departamento de Softwares")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: gray; font-size: 10px; margin-top: 10px;")
        main_vertical_layout.addWidget(footer_label)

        # Aplica layout vertical na janela
        self.setLayout(main_vertical_layout)

        # Inicializa gráfico vazio
        self.update_dashboard()

    def update_dashboard(self):
        self.load_transactions()
        self.update_balance()
        self.update_chart()

    def load_transactions(self):
        self.table.setRowCount(len(self.transactions))
        for row, tx in enumerate(self.transactions):
            self.table.setItem(row, 0, QTableWidgetItem(tx["desc"]))
            self.table.setItem(row, 1, QTableWidgetItem(f"R$ {tx['valor']:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(tx["tipo"]))

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
        colors = ['#10B981', '#EF4444']  # verde e vermelho

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
