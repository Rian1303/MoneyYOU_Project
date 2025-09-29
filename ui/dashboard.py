# ui/dashboard.py  (PyQt6)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QLineEdit, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
    QTextEdit
)
from PyQt6.QtCore import Qt, QDate, QTimer
from ui.widgets.chart_widget import ChartWidget

from ui.transaction_form import TransactionForm
from ui.settings_screen import SettingsScreen
from ui.transactions_screen import TransactionsScreen
from database.data_manager import load_transactions, filter_transactions
from logic.theme_manager import set_theme, load_theme_qss
from logic.usr_config import UserConfigManager
from logic.finance_logic import FinanceLogic

try:
    from logic.ai_assistant import AIAssistant
except Exception:
    AIAssistant = None


class DashboardWindow(QWidget):
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.transactions = []
        self.user_config = {}

        self.finance = FinanceLogic()

        # ---------------- Configurações ----------------
        self.settings_widget = SettingsScreen(self.username)
        self.settings_widget.theme_changed.connect(self.apply_theme)
        self.settings_widget.config_changed.connect(self.on_config_changed)

        self.transactions_screen = TransactionsScreen(self.username)

        # Assistente Financeiro
        self.assistant = None
        self.assistant_error = None
        if AIAssistant:
            try:
                self.assistant = AIAssistant()
            except Exception as e:
                self.assistant_error = str(e)

        # Carregar configs do usuário
        try:
            cfg = UserConfigManager.get_user_config(self.username)
        except Exception:
            cfg = {}
        self.apply_user_config(cfg)

        try:
            self.config_listener = UserConfigManager.listen_user_config(
                self.username, self.apply_user_config
            )
        except Exception:
            self.config_listener = None

        # Montar interface
        self.init_ui()
        self.update_dashboard()

    # ---------------- UI ----------------
    def init_ui(self):
        self.setWindowTitle("MoneyYOU - Dashboard")
        self.setMinimumSize(1150, 750)

        self.main_layout = QVBoxLayout(self)

        # ---------- Topbar ----------
        self.topbar_layout = QHBoxLayout()
        self.dashboard_btn = QPushButton("🏠 Início")
        self.transactions_btn = QPushButton("📑 Transações")
        self.settings_btn = QPushButton("⚙️ Configurações")
        self.logout_btn = QPushButton("⏻ Sair")

        for btn in [self.dashboard_btn, self.transactions_btn, self.settings_btn, self.logout_btn]:
            btn.setFixedHeight(36)
            btn.setStyleSheet("font-weight: bold;")

        self.topbar_layout.addWidget(self.dashboard_btn)
        self.topbar_layout.addWidget(self.transactions_btn)
        self.topbar_layout.addWidget(self.settings_btn)
        self.topbar_layout.addStretch()

        # Avatar simples
        self.user_icon = QLabel()
        self.user_icon.setFixedSize(42, 42)
        self.user_icon.setStyleSheet("border-radius:21px; background-color:#7C3AED;")
        self.topbar_layout.addWidget(self.user_icon)
        self.topbar_layout.addWidget(self.logout_btn)

        self.main_layout.addLayout(self.topbar_layout)

        # ---------- Conteúdo ----------
        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        # Grupo gráfico
        self.chart_group = QGroupBox("📊 Resumo Financeiro")
        chart_layout = QVBoxLayout()
        self.chart_canvas = ChartWidget([])
        chart_layout.addWidget(self.chart_canvas)
        self.chart_group.setLayout(chart_layout)

        # Grupo transações e assistente
        self.transactions_group = QGroupBox("💰 Transações e Assistente")
        right_layout = QVBoxLayout()

        # Saldo
        self.balance_label = QLabel("Saldo: R$ 0,00")
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.balance_label.setStyleSheet("font-size:16pt; font-weight:bold; margin: 10px 0;")
        right_layout.addWidget(self.balance_label)

        # Botões de ação
        controls = QHBoxLayout()
        self.add_transaction_btn = QPushButton("➕ Adicionar")
        self.filter_btn = QPushButton("🔍 Filtrar")
        self.refresh_btn = QPushButton("🔄 Atualizar")
        controls.addWidget(self.add_transaction_btn)
        controls.addWidget(self.filter_btn)
        controls.addWidget(self.refresh_btn)
        right_layout.addLayout(controls)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Data", "Descrição", "Categoria", "Valor", "Tipo"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        right_layout.addWidget(self.table)

        # Assistente Financeiro
        self.assistant_group = QGroupBox("🤖 Assistente Financeiro (Beta)")
        ag = QVBoxLayout()
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("background:#1E1E1E; color:#F9FAFB; padding:5px; border-radius:8px;")
        ag.addWidget(self.chat_history)

        chat_input_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Digite sua dúvida financeira...")
        self.chat_send_btn = QPushButton("Enviar")
        chat_input_row.addWidget(self.chat_input)
        chat_input_row.addWidget(self.chat_send_btn)
        ag.addLayout(chat_input_row)
        self.assistant_group.setLayout(ag)

        if self.assistant is None:
            self.chat_history.setPlainText(
                "⚠️ Assistente indisponível.\n"
                + (f"Motivo: {self.assistant_error}" if self.assistant_error else "Verifique a configuração da API.")
            )
            self.chat_input.setDisabled(True)
            self.chat_send_btn.setDisabled(True)

        right_layout.addWidget(self.assistant_group)
        self.transactions_group.setLayout(right_layout)

        # Layout inicial
        self.content_layout.addWidget(self.chart_group, 3)
        self.content_layout.addWidget(self.transactions_group, 6)

        # ---------- Conexões ----------
        self.dashboard_btn.clicked.connect(self.show_dashboard_content)
        self.settings_btn.clicked.connect(self.show_settings_content)
        self.transactions_btn.clicked.connect(self.show_transactions_content)
        self.add_transaction_btn.clicked.connect(self.open_transaction_form)
        self.filter_btn.clicked.connect(self.open_filter_dialog)
        self.refresh_btn.clicked.connect(self.update_dashboard)
        self.logout_btn.clicked.connect(self.close)
        self.chat_send_btn.clicked.connect(self.on_send_message)

    # ---------------- Dashboard Logic ----------------
    def update_dashboard(self, transactions=None):
        self.transactions = transactions or load_transactions(user_id=self.username) or []
        if not isinstance(self.transactions, list):
            self.transactions = []

        self.load_transactions_table(self.transactions)
        self.update_balance(self.transactions)
        self.update_chart(self.transactions)

    def load_transactions_table(self, transactions):
        display_currency = self.user_config.get("currency", "BRL")
        self.table.setRowCount(len(transactions))
        for row, tx in enumerate(transactions):
            date_str = tx.get("date", "")
            desc = tx.get("desc", "")
            category = tx.get("category", "")
            amount = float(tx.get("amount", 0) or 0)
            tx_currency = tx.get("currency", "BRL")
            typ = tx.get("type", "")

            try:
                converted_amount = self.finance.convert_currency(amount, tx_currency, display_currency)
            except Exception:
                converted_amount = amount

            display_text = self.finance.format_currency(converted_amount, display_currency)

            self.table.setItem(row, 0, QTableWidgetItem(date_str))
            self.table.setItem(row, 1, QTableWidgetItem(desc))
            self.table.setItem(row, 2, QTableWidgetItem(category))
            self.table.setItem(row, 3, QTableWidgetItem(display_text))
            self.table.setItem(row, 4, QTableWidgetItem(typ))

    def update_balance(self, transactions):
        saldo = 0.0
        display_currency = self.user_config.get("currency", "BRL")
        for tx in transactions:
            amt = float(tx.get("amount", 0) or 0)
            tx_currency = tx.get("currency", "BRL")
            try:
                converted = self.finance.convert_currency(amt, tx_currency, display_currency)
            except Exception:
                converted = amt
            if tx.get("type") in ("entrada", "receita"):
                saldo += converted
            else:
                saldo -= converted
        self.balance_label.setText(f"Saldo: {self.finance.format_currency(saldo, display_currency)}")

    def update_chart(self, transactions):
        normalized = []
        for tx in transactions:
            amt = float(tx.get("amount", 0) or 0)
            tx_currency = tx.get("currency", "BRL")
            try:
                converted = self.finance.convert_currency(amt, tx_currency, self.user_config.get("currency", "BRL"))
            except Exception:
                converted = amt
            typ = tx.get("type", "").lower()
            typ_std = "income" if typ in ("entrada", "receita", "income") else "expense"
            normalized.append({"value": converted, "type": typ_std, "category": tx.get("category", "Outros")})

        theme = self.user_config.get("theme", "light")
        if theme == "dark":
            bg_color = "#1E1E1E"
            text_color = "#F9FAFB"
        else:
            bg_color = "#F9FAFB"
            text_color = "#1E1E1E"

        self.chart_canvas.update_chart(normalized, bg_color=bg_color, text_color=text_color)

    # ---------------- Actions ----------------
    def open_transaction_form(self):
        self.transaction_form = TransactionForm(user_id=self.username)
        self.transaction_form.transaction_added.connect(self.update_dashboard)
        self.transaction_form.show()

    # ---------------- Filter ----------------
    def open_filter_dialog(self):
        dlg = FilterDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            f = dlg.get_filters()
            try:
                filtered = filter_transactions(
                    user_id=self.username,
                    tx_type=f["type"],
                    start_date=f["start_date"],
                    end_date=f["end_date"],
                    category=f["category"] or None,
                    min_amount=f["min_amount"],
                    max_amount=f["max_amount"],
                )
            except Exception:
                filtered = self._local_filter(self.transactions, f)
            self.update_dashboard(filtered)

    def _local_filter(self, transactions, f):
        filtered = []
        for tx in transactions:
            if f["type"] and tx.get("type") != f["type"]:
                continue
            if f["category"] and tx.get("category") != f["category"]:
                continue
            tx_date = QDate.fromString(tx.get("date", ""), "yyyy-MM-dd")
            if f["start_date"] and tx_date < f["start_date"]:
                continue
            if f["end_date"] and tx_date > f["end_date"]:
                continue
            amt = float(tx.get("amount", 0) or 0)
            if f["min_amount"] and amt < f["min_amount"]:
                continue
            if f["max_amount"] and amt > f["max_amount"]:
                continue
            filtered.append(tx)
        return filtered

    # ---------------- Navegação ----------------
    def show_dashboard_content(self):
        self.clear_content_layout()
        self.content_layout.addWidget(self.chart_group, 3)
        self.content_layout.addWidget(self.transactions_group, 6)

    def show_settings_content(self):
        self.clear_content_layout()
        self.content_layout.addWidget(self.settings_widget)

    def show_transactions_content(self):
        self.clear_content_layout()
        self.content_layout.addWidget(self.transactions_screen)

    def clear_content_layout(self):
        while self.content_layout.count():
            widget = self.content_layout.takeAt(0).widget()
            if widget:
                widget.setParent(None)

    # ---------------- Assistente ----------------
    def on_send_message(self):
        msg = self.chat_input.text().strip()
        if not msg:
            return
        self.chat_history.append(f"👤 Você: {msg}")
        self.chat_input.clear()
        if self.assistant:
            response = self.assistant.ask(msg, user_id=self.username)
            self.chat_history.append(f"🤖 Assistente: {response}")

    # ---------------- Theme / Config ----------------
    def apply_theme(self, theme):
        set_theme(theme)
        self.setStyleSheet(load_theme_qss())
        self.update_chart(self.transactions)

    def apply_user_config(self, config: dict):
        QTimer.singleShot(0, lambda cfg=config: self._apply_user_config_ui(cfg))

    def _apply_user_config_ui(self, config: dict):
        if not config:
            return
        self.user_config = config
        theme = config.get("theme")
        if theme:
            self.apply_theme(theme)
        avatar_color = config.get("avatar_color")
        if avatar_color:
            self.user_icon.setStyleSheet(f"border-radius:21px; background-color:{avatar_color};")
        self.update_dashboard()

    def on_config_changed(self, key, value):
        self.user_config[key] = value
        UserConfigManager.set_user_config(self.username, self.user_config)  # salva config
        if key == "currency":
            self.update_dashboard()
        elif key == "theme":
            self.apply_theme(value)

    def closeEvent(self, event):
        try:
            UserConfigManager.set_user_config(self.username, self.user_config)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
        super().closeEvent(event)


# ---------------- Filter Dialog ----------------
class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtrar Transações")
        self.setMinimumWidth(350)
        layout = QVBoxLayout()

        self.type_cb = QComboBox()
        self.type_cb.addItems(["", "entrada", "saída"])
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.type_cb)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        layout.addWidget(QLabel("Data Inicial:"))
        layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        layout.addWidget(QLabel("Data Final:"))
        layout.addWidget(self.end_date)

        self.category_input = QLineEdit()
        layout.addWidget(QLabel("Categoria:"))
        layout.addWidget(self.category_input)

        self.min_amount_input = QLineEdit()
        self.max_amount_input = QLineEdit()
        layout.addWidget(QLabel("Valor Mínimo:"))
        layout.addWidget(self.min_amount_input)
        layout.addWidget(QLabel("Valor Máximo:"))
        layout.addWidget(self.max_amount_input)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def get_filters(self):
        return {
            "type": self.type_cb.currentText() or None,
            "start_date": self.start_date.date() if self.start_date.date().isValid() else None,
            "end_date": self.end_date.date() if self.end_date.date().isValid() else None,
            "category": self.category_input.text().strip(),
            "min_amount": float(self.min_amount_input.text() or 0),
            "max_amount": float(self.max_amount_input.text() or 0),
        }
