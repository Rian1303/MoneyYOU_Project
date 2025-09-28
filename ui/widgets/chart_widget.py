# ui/widgets/chart_widget.py
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class ChartWidget(FigureCanvasQTAgg):
    def __init__(self, transactions, bg_color="#F9FAFB", text_color="#1E1E1E"):
        self.transactions = transactions
        self.bg_color = bg_color
        self.text_color = text_color

        self.fig = Figure(facecolor=self.bg_color)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.plot(transactions)

    def update_chart(self, transactions, bg_color=None, text_color=None):
        if bg_color:
            self.bg_color = bg_color
        if text_color:
            self.text_color = text_color
        self.transactions = transactions
        self.plot(transactions)

    def plot(self, transactions):
        self.ax.clear()
        self.fig.set_facecolor(self.bg_color)

        # calcular totais
        income = sum(tx["value"] for tx in transactions if tx["type"] == "income")
        expense = sum(tx["value"] for tx in transactions if tx["type"] == "expense")

        values = [income, expense]
        labels = ["Receita", "Despesa"]
        colors = ["#4CAF50", "#F44336"]  # verde e vermelho, bom contraste
        if sum(values) == 0:
            values = [1, 1]  # evita erro matplotlib com zero total
            labels = ["Sem dados", ""]

        wedges, texts, autotexts = self.ax.pie(
            values,
            labels=labels,
            autopct=lambda p: f"{p:.1f}%" if sum(values) > 0 else "",
            colors=colors,
            textprops={"color": self.text_color},
            startangle=90,
            wedgeprops={"edgecolor": self.bg_color}
        )

        self.ax.set_facecolor(self.bg_color)
        self.ax.set_title("Resumo Financeiro", color=self.text_color)
        self.draw()
