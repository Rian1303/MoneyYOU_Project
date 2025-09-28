import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO


def generate_monthly_report(transactions):
    """
    Generates a basic monthly report of transactions.
    """
    total_income = 0.0
    total_expenses = 0.0

    for transaction in transactions:
        value = transaction.get('value', 0)
        try:
            value = float(value)
        except (ValueError, TypeError):
            value = 0.0

        if transaction.get('type') == 'income':
            total_income += value
        elif transaction.get('type') == 'expense':
            total_expenses += value

    balance = total_income - total_expenses

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance
    }


def calculate_totals_by_category(transactions):
    """
    Calculates totals grouped by category.
    """
    category_totals = {}

    for transaction in transactions:
        category = transaction.get('category', 'Others')
        value = transaction.get('value', 0)
        try:
            value = float(value)
        except (ValueError, TypeError):
            value = 0.0

        category_totals[category] = category_totals.get(category, 0.0) + value

    return category_totals


def generate_pie_chart(transactions):
    """
    Generates a pie chart of expenses grouped by category.
    Returns a BytesIO buffer with the PNG image (to be used in Qt).
    """
    # Filtrar apenas despesas
    expenses = [t for t in transactions if t.get("type") == "expense"]

    if not expenses:
        return None

    df = pd.DataFrame(expenses)

    # Agrupar por categoria
    df_grouped = df.groupby("category")["value"].sum().reset_index()

    # Paleta de cores institucionais (MoneyYOU)
    colors = ["#7C3AED", "#A855F7", "#1E1E1E", "#6366F1", "#F97316"]

    # Criar gráfico
    fig, ax = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax.pie(
        df_grouped["value"],
        labels=df_grouped["category"],
        autopct="%.1f%%",
        colors=colors[:len(df_grouped)],
        startangle=140,
        textprops={"fontsize": 9, "color": "white"},
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )

    ax.set_title("Distribuição de Despesas", fontsize=12, weight="bold", color="#1E1E1E")

    # Exportar para buffer
    buf = BytesIO()
    plt.savefig(buf, format="png", transparent=True, bbox_inches="tight")
    plt.close(fig)

    buf.seek(0)
    return buf
