def generate_monthly_report(transactions):
    """
    Generates a basic monthly report of transactions.

    Args:
        transactions (list): List of transaction dictionaries.

    Returns:
        dict: Totals for income, expenses, and balance for the month.
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

    Args:
        transactions (list): List of transaction dictionaries.

    Returns:
        dict: Keys are categories, values are totals.
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

