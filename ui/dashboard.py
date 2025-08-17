import sys
import os   
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox, QDialog,
    QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from ui.transaction_form import TransactionForm
from datetime import datetime

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Importe sua função de filtro (ajuste o caminho conforme seu projeto)
from logic.transactions import filter_transactions
from logic.transactions import load_transactions, add_transaction

from logic.firebase import sync_transactions_to_firebase


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtrar Transações")
        self.setModal(True)
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        # Tipo
        tipo_layout = QHBoxLayout()
        tipo_label = QLabel("Tipo:")
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("")  # vazio = sem filtro
        self.tipo_combo.addItems(["entrada", "saída", "receita", "despesa"])  # possíveis tipos usados
        tipo_layout.addWidget(tipo_label)
        tipo_layout.addWidget(self.tipo_combo)
        layout.addLayout(tipo_layout)

        # Data início
        data_inicio_layout = QHBoxLayout()
        data_inicio_label = QLabel("Data Início (dd/mm/aaaa):")
        self.data_inicio_edit = QLineEdit()
        data_inicio_layout.addWidget(data_inicio_label)
        data_inicio_layout.addWidget(self.data_inicio_edit)
        layout.addLayout(data_inicio_layout)

        # Data fim
        data_fim_layout = QHBoxLayout()
        data_fim_label = QLabel("Data Fim (dd/mm/aaaa):")
        self.data_fim_edit = QLineEdit()
        data_fim_layout.addWidget(data_fim_label)
        data_fim_layout.addWidget(self.data_fim_edit)
        layout.addLayout(data_fim_layout)

        # Botões
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Aplicar")
        self.cancel_btn = QPushButton("Cancelar")
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_filters(self):
        return {
            "tipo": self.tipo_combo.currentText().strip() or None,
            "data_inicio": self.data_inicio_edit.text().strip() or None,
            "data_fim": self.data_fim_edit.text().strip() or None,
        }


class DashboardWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"Dashboard - Organizador Financeiro - {username}")
        self.setMinimumSize(900, 650)  # Evitar cortes

        self.username = username
        self.transactions = load_transactions(user_id=self.username)  # Ajuste se precisar converter username em id
        

        self.init_ui()

    def init_ui(self):
        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setContentsMargins(12, 12, 12, 12)
        main_vertical_layout.setSpacing(8)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)

        # Gráfico (lado esquerdo)
        self.chart_group = QGroupBox("Resumo Financeiro")
        chart_layout = QVBoxLayout()
        self.chart_canvas = FigureCanvas(Figure(figsize=(6, 5)))
        chart_layout.addWidget(self.chart_canvas)
        self.chart_group.setLayout(chart_layout)

        # Transações e botões (lado direito)
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

        self.filter_btn = QPushButton("Filtrar")
        self.filter_btn.clicked.connect(self.open_filter_dialog)
        right_layout.addWidget(self.filter_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Data", "Descrição", "Valor", "Tipo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        right_layout.addWidget(self.table)

        self.transactions_group.setLayout(right_layout)

        main_layout.addWidget(self.chart_group, 3)
        main_layout.addWidget(self.transactions_group, 5)

        main_vertical_layout.addLayout(main_layout)

        footer_label = QLabel("Direitos Reservados à Croma Company - Departamento de Softwares")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setObjectName("footerLabel")
        footer_label.setStyleSheet("color: gray; font-size: 10px; margin-top: 10px;")
        main_vertical_layout.addWidget(footer_label)

        self.setLayout(main_vertical_layout)

        self.update_dashboard()

        self.sync_btn = QPushButton("🔄 Sincronizar com Firebase")
        self.sync_btn.clicked.connect(self.sync_with_firebase)
        right_layout.addWidget(self.sync_btn)

    def update_dashboard(self):
        from logic.transactions import load_transactions
        self.transactions = load_transactions(user_id=self.username)
        self.load_transactions(self.transactions)
        self.update_balance(self.transactions)
        self.update_chart(self.transactions)

    def load_transactions(self, transactions=None):
        transactions = transactions or self.transactions
        self.table.setRowCount(len(transactions))
        for row, tx in enumerate(transactions):
            data_text = tx.get("date", "")
            self.table.setItem(row, 0, QTableWidgetItem(data_text))
            self.table.setItem(row, 1, QTableWidgetItem(tx.get("desc", "")))
            self.table.setItem(row, 2, QTableWidgetItem(f"R$ {tx.get('amount', 0):.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(tx.get("type", "")))

    def update_balance(self, transactions=None):
        transactions = transactions or self.transactions
        saldo = 0
        for tx in transactions:
            tipo = tx.get("type", "").lower()
            valor = tx.get("amount", 0)
            if tipo in ("entrada", "receita"):
                saldo += valor
            elif tipo in ("saída", "despesa"):
                saldo -= valor
        self.balance_label.setText(f"Saldo: R$ {saldo:.2f}")

    def update_chart(self, transactions=None):
        transactions = transactions or self.transactions
        self.chart_canvas.figure.clear()
        ax = self.chart_canvas.figure.add_subplot(111)

        receita = sum(tx.get("amount", 0) for tx in transactions if tx.get("type", "").lower() in ("entrada", "receita"))
        despesa = sum(tx.get("amount", 0) for tx in transactions if tx.get("type", "").lower() in ("saída", "despesa"))

        categories = ['Receitas', 'Despesas']
        values = [receita, despesa]
        colors = ['#10B981', '#EF4444']

        ax.bar(categories, values, color=colors)
        ax.set_title("Resumo de Receitas vs Despesas")
        ax.set_ylabel("Valor (R$)")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.margins(y=0.1)
        self.chart_canvas.draw()

    def open_transaction_form(self):
        self.form = TransactionForm()
        self.form.transaction_added.connect(self.handle_new_transaction)
        self.form.show()

    def open_filter_dialog(self):
        dialog = FilterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filtros = dialog.get_filters()
            filtradas = filter_transactions(
                self.transactions,
                tipo=filtros["tipo"],
                data_inicio=filtros["data_inicio"],
                data_fim=filtros["data_fim"]
            )
            self.load_transactions(filtradas)
            self.update_balance(filtradas)
            self.update_chart(filtradas)

    def handle_new_transaction(self, transaction):
        from logic.transactions import add_transaction

        # Inclua o username/id na transação
        transaction['user_id'] = self.username

        response = add_transaction(transaction)
        if response.get("status") == "success":
            self.update_dashboard()
            QMessageBox.information(self, "Sucesso", "Transação adicionada com sucesso!")
        else:
            QMessageBox.warning(self, "Erro", response.get("message", "Erro ao salvar transação."))

    def sync_with_firebase(self):
        try:
            result = sync_transactions_to_firebase(user_id=self.username)
            if result["status"] == "success":
                QMessageBox.information(self, "Sucesso", "Transações sincronizadas com o Firebase.")
            else:
                QMessageBox.warning(self, "Erro", f"Erro ao sincronizar: {result['message']}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {str(e)}")
