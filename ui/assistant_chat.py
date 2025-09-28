# ui/assistant_chart.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from logic.ai_assistant import AIAssistant
from database.data_manager import load_transactions


class AssistantChart(QWidget):
    def __init__(self, user_id: str, parent=None):
        super().__init__(parent)

        self.user_id = user_id
        self.assistant = AIAssistant()

        layout = QVBoxLayout(self)

        # Título
        titulo = QLabel("📊 Análise Financeira com IA")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin: 5px;")
        layout.addWidget(titulo)

        # Gráfico matplotlib
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.canvas)

        # Área de texto para análise
        self.analysis_label = QLabel("⏳ Gerando análise...")
        self.analysis_label.setWordWrap(True)
        layout.addWidget(self.analysis_label)

        # Atualiza dados
        self.update_analysis()

    def update_analysis(self):
        """Atualiza gráfico e pede análise para a IA"""
        transactions = load_transactions(user_id=self.user_id)

        if not transactions:
            self.analysis_label.setText("⚠️ Nenhuma transação encontrada.")
            return

        # --- Parte 1: gráfico (exemplo: receitas vs despesas)
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        receitas = sum(t["valor"] for t in transactions if t["tipo"] == "receita")
        despesas = sum(t["valor"] for t in transactions if t["tipo"] == "despesa")

        ax.bar(["Receitas", "Despesas"], [receitas, despesas], color=["green", "red"])
        ax.set_title("Resumo Financeiro")
        self.canvas.draw()

        # --- Parte 2: análise com IA
        pergunta = (
            f"Com base nessas transações: {transactions}, "
            "faça uma análise breve sobre o equilíbrio financeiro do usuário."
        )

        resposta = self.assistant.ask(pergunta, user_id=self.user_id)
        self.analysis_label.setText(f"🤖 {resposta}")
