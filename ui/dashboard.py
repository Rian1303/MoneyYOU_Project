from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from ui.transaction_form import TransactionForm
from logic.transactions import filter_transactions, load_transactions
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ------------------ FilterDialog inline ------------------
class FilterDialog(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Filtrar Transações")
        layout = QVBoxLayout()
        # Tipo
        tipo_layout = QHBoxLayout()
        tipo_label = QLabel("Tipo:")
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("")
        self.tipo_combo.addItems(["entrada", "saída", "receita", "despesa"])
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

    def accept(self):
        self.parent().apply_filters(self.get_filters())
        self.hide()

    def reject(self):
        self.hide()

    def get_filters(self):
        return {
            "tipo": self.tipo_combo.currentText().strip() or None,
            "data_inicio": self.data_inicio_edit.text().strip() or None,
            "data_fim": self.data_fim_edit.text().strip() or None,
        }

# ------------------ DashboardWindow ------------------
class DashboardWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.transactions = load_transactions(user_id=username)
        self.transaction_form = None
        self.filter_dialog = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Dashboard - {self.username}")
        self.setMinimumSize(900, 650)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # ------------------ Barra superior ------------------
        self.topbar_layout = QHBoxLayout()
        self.dashboard_btn = QPushButton("Dashboard")
        self.transactions_btn = QPushButton("Transações")
        self.settings_btn = QPushButton("Configurações")

        self.topbar_layout.addWidget(self.dashboard_btn)
        self.topbar_layout.addWidget(self.transactions_btn)
        self.topbar_layout.addWidget(self.settings_btn)
        self.topbar_layout.addStretch()

        # Ícone do usuário
        self.user_icon = QLabel()
        self.user_icon.setFixedSize(30, 30)
        self.user_icon.setStyleSheet("border-radius: 15px; background-color: #7C3AED;")
        self.topbar_layout.addWidget(self.user_icon)

        self.main_layout.addLayout(self.topbar_layout)

        # ------------------ Conexões da Barra Superior ------------------
        self.dashboard_btn.clicked.connect(self.show_dashboard_content)
        self.transactions_btn.clicked.connect(self.open_transactions)  # <-- aqui
        self.settings_btn.clicked.connect(self.show_settings_content)


        # ------------------ Área principal ------------------
        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        # Gráfico
        self.chart_group = QGroupBox("Resumo Financeiro")
        chart_layout = QVBoxLayout()
        self.chart_canvas = FigureCanvas(Figure(figsize=(6,5)))
        chart_layout.addWidget(self.chart_canvas)
        self.chart_group.setLayout(chart_layout)

        # Transações
        self.transactions_group = QGroupBox("Transações")
        right_layout = QVBoxLayout()
        self.balance_label = QLabel("Saldo: R$ 0,00")
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.balance_label)
        self.add_transaction_btn = QPushButton("Adicionar Transação")
        right_layout.addWidget(self.add_transaction_btn)
        self.filter_btn = QPushButton("Filtrar")
        right_layout.addWidget(self.filter_btn)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Data", "Descrição", "Valor", "Tipo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        right_layout.addWidget(self.table)
        self.transactions_group.setLayout(right_layout)

        self.content_layout.addWidget(self.chart_group, 3)
        self.content_layout.addWidget(self.transactions_group, 5)

        # ------------------ Rodapé ------------------
        self.footer_label = QLabel("Direitos Reservados à Croma Company - Dep. de Software")
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setStyleSheet("color: gray; font-size: 10pt; margin-top: 10px;")
        self.main_layout.addWidget(self.footer_label)

        # ------------------ Conexões ------------------
        self.dashboard_btn.clicked.connect(self.show_dashboard_content)
        self.settings_btn.clicked.connect(self.show_settings_content)
        self.transactions_btn.clicked.connect(self.open_transactions)
        self.add_transaction_btn.clicked.connect(self.open_transaction_form)
        self.filter_btn.clicked.connect(self.open_filter_dialog)

        self.update_dashboard()

    # ------------------ Atualização ------------------
    def update_dashboard(self):
        self.transactions = load_transactions(user_id=self.username)
        self.load_transactions(self.transactions)
        self.update_balance()
        self.update_chart()

    def load_transactions(self, transactions=None):
        transactions = transactions or self.transactions
        self.table.setRowCount(len(transactions))
        for row, tx in enumerate(transactions):
            self.table.setItem(row, 0, QTableWidgetItem(tx.get("date", "")))
            self.table.setItem(row, 1, QTableWidgetItem(tx.get("desc", "")))
            self.table.setItem(row, 2, QTableWidgetItem(f"R$ {tx.get('amount',0):.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(tx.get("type","")))

    def update_balance(self):
        saldo = sum(tx.get("amount",0) if tx.get("type") in ["entrada","receita"] else -tx.get("amount",0)
                    for tx in self.transactions)
        self.balance_label.setText(f"Saldo: R$ {saldo:.2f}")

    def update_chart(self):
        self.chart_canvas.figure.clear()
        ax = self.chart_canvas.figure.add_subplot(111)
        receita = sum(tx.get("amount",0) for tx in self.transactions if tx.get("type") in ["entrada","receita"])
        despesa = sum(tx.get("amount",0) for tx in self.transactions if tx.get("type") in ["saída","despesa"])
        ax.bar(["Receitas","Despesas"], [receita, despesa], color=['#10B981','#EF4444'])
        ax.set_title("Resumo de Receitas vs Despesas")
        self.chart_canvas.draw()

    # ------------------ Ações ------------------
    def open_transaction_form(self):
        if not self.transaction_form:
            self.transaction_form = TransactionForm(user_id=self.username)
            self.transaction_form.transaction_added.connect(self.handle_new_transaction)
            self.transaction_form.destroyed.connect(lambda: setattr(self, 'transaction_form', None))
            self.transaction_form.show()
        else:
            self.transaction_form.raise_()
            self.transaction_form.activateWindow()

    def handle_new_transaction(self, transaction):
        self.update_dashboard()

    def open_filter_dialog(self):
        if not self.filter_dialog:
            self.filter_dialog = FilterDialog(self)
        self.filter_dialog.show()

    def apply_filters(self, filtros):
        filtradas = filter_transactions(self.transactions,
                                       tipo=filtros["tipo"],
                                       data_inicio=filtros["data_inicio"],
                                       data_fim=filtros["data_fim"])
        self.load_transactions(filtradas)
        self.update_balance()

    # ------------------ Configurações e Transações ------------------
    def show_settings_content(self):
        from ui.settings_screen import SettingsScreen
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.settings_widget = SettingsScreen()
        self.content_layout.addWidget(self.settings_widget)

    def show_dashboard_content(self):
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.content_layout.addWidget(self.chart_group, 3)
        self.content_layout.addWidget(self.transactions_group, 5)
# ------------------ Abrir Tela de Transações ------------------
    def open_transactions(self):
        # Remove widgets atuais do content_layout
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Cria a tela de transações dentro do mesmo layout
        from ui.transactions_screen import TransactionsScreen
        self.transactions_window = TransactionsScreen(parent_layout=self.content_layout, user_id=self.username)
        self.content_layout.addWidget(self.transactions_window)
