# transactions_screen.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QComboBox,
    QLineEdit, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from logic.transactions_manager import (
    get_transactions, remove_transaction, restore_deleted_transaction, export_transactions_csv
)
from datetime import datetime

# ------------------ FilterDialog ------------------
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

# ------------------ TransactionsScreen ------------------
class TransactionsScreen(QWidget):
    LOAD_BATCH = 50  # número de linhas carregadas por vez

    def __init__(self, parent_layout, user_id):
        super().__init__()
        self.parent_layout = parent_layout
        self.user_id = user_id
        self.deleted_transactions = []
        self.all_transactions = get_transactions()
        self.displayed_transactions = []
        self.filter_dialog = None
        self.next_load_index = 0
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # ------------------ Botões de ação ------------------
        btn_layout = QHBoxLayout()
        self.filter_btn = QPushButton("Filtrar")
        self.delete_btn = QPushButton("Deletar Selecionado")
        self.restore_btn = QPushButton("Restaurar Última Deleção")
        self.export_btn = QPushButton("Exportar CSV")
        btn_layout.addWidget(self.filter_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.restore_btn)
        btn_layout.addWidget(self.export_btn)
        self.main_layout.addLayout(btn_layout)

        # ------------------ Tabela ------------------
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Data", "Categoria", "Valor", "Tipo", "Descrição"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalScrollBar().valueChanged.connect(self.check_scroll_end)
        self.main_layout.addWidget(self.table)

        # ------------------ Conexões ------------------
        self.filter_btn.clicked.connect(self.open_filter_dialog)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.restore_btn.clicked.connect(self.restore_last)
        self.export_btn.clicked.connect(self.export_csv)

        # Carrega o primeiro batch de transações
        self.load_next_batch()

    # ------------------ Scroll Infinito ------------------
    def check_scroll_end(self, value):
        if value == self.table.verticalScrollBar().maximum():
            self.load_next_batch()

    def load_next_batch(self):
        if self.next_load_index >= len(self.all_transactions):
            return
        batch = self.all_transactions[self.next_load_index:self.next_load_index + self.LOAD_BATCH]
        start_row = self.table.rowCount()
        self.table.setRowCount(start_row + len(batch))
        for i, t in enumerate(batch):
            self.table.setItem(start_row + i, 0, QTableWidgetItem(t.get('date','')))
            self.table.setItem(start_row + i, 1, QTableWidgetItem(t.get('category','')))
            self.table.setItem(start_row + i, 2, QTableWidgetItem(f"R$ {t.get('amount',0):.2f}"))
            self.table.setItem(start_row + i, 3, QTableWidgetItem(t.get('type','')))
            self.table.setItem(start_row + i, 4, QTableWidgetItem(t.get('desc','')))
            self.displayed_transactions.append(t)
        self.next_load_index += len(batch)

    def reload_table(self):
        self.table.setRowCount(0)
        self.displayed_transactions = []
        self.next_load_index = 0
        self.load_next_batch()

    # ------------------ Filtros ------------------
    def open_filter_dialog(self):
        if not self.filter_dialog:
            self.filter_dialog = FilterDialog(self)
        self.filter_dialog.show()

    def apply_filters(self, filtros):
        start_date = datetime.strptime(filtros["data_inicio"], "%d/%m/%Y") if filtros["data_inicio"] else None
        end_date = datetime.strptime(filtros["data_fim"], "%d/%m/%Y") if filtros["data_fim"] else None
        self.all_transactions = get_transactions(start_date=start_date, end_date=end_date)
        if filtros["tipo"]:
            self.all_transactions = [t for t in self.all_transactions if t.get("type")==filtros["tipo"]]
        self.reload_table()

    # ------------------ Deletar / Restaurar ------------------
    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Atenção", "Selecione uma transação para deletar.")
            return
        transaction = self.displayed_transactions[row]
        if remove_transaction(transaction['id']):
            self.deleted_transactions.append(transaction)
            self.all_transactions.remove(transaction)
            self.reload_table()

    def restore_last(self):
        if not self.deleted_transactions:
            QMessageBox.information(self, "Info", "Não há transações para restaurar.")
            return
        transaction = self.deleted_transactions.pop()
        if restore_deleted_transaction(transaction):
            self.all_transactions.append(transaction)
            self.reload_table()

    # ------------------ Exportar CSV ------------------
    def export_csv(self):
        # Abre diálogo para escolher o local do arquivo
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar CSV", f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        if not file_path:
            return

        if export_transactions_csv(self.all_transactions, file_path):
            QMessageBox.information(self, "Sucesso", f"Transações exportadas para {file_path}")
        else:
            QMessageBox.warning(self, "Erro", "Falha ao exportar CSV.")
