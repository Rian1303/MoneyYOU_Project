from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Criar figura matplotlib
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def plot_pie_chart(self, data):
        """
        data: dict com categorias e valores. Exemplo:
            {"Receita": 7000, "Despesa": 3000}
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        labels = list(data.keys())
        sizes = list(data.values())

        colors = ['#7C3AED', '#B22222']  # Roxo e vermelho, por exemplo

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Mantém círculo

        self.canvas.draw()
