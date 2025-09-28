# logic/finance.py

class FinanceLogic:
    """
    Classe responsável por lógica financeira:
    - Conversão de moedas
    - Formatação de valores com símbolo
    - Taxas de câmbio base (ilustrativas)
    """

    # Taxas de câmbio base (ilustrativas, 1 BRL -> X)
    exchange_rates = {
        "BRL": 1.0,      # Base
        "USD": 0.19,     # 1 BRL = 0,19 USD
        "EUR": 0.17,     # 1 BRL = 0,17 EUR
    }

    # Símbolos para cada moeda
    currency_symbols = {
        "BRL": "R$",
        "USD": "$",
        "EUR": "€"
    }

    def __init__(self):
        pass

    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Converte um valor de uma moeda para outra usando as taxas de câmbio.
        """
        if from_currency not in self.exchange_rates:
            raise ValueError(f"Moeda de origem inválida: {from_currency}")
        if to_currency not in self.exchange_rates:
            raise ValueError(f"Moeda de destino inválida: {to_currency}")

        # Converte para BRL (base)
        amount_in_brl = amount / self.exchange_rates[from_currency]

        # Converte para moeda de destino
        converted = amount_in_brl * self.exchange_rates[to_currency]
        return converted

    def format_currency(self, amount: float, currency: str) -> str:
        """
        Retorna o valor formatado com símbolo da moeda e 2 casas decimais.
        """
        symbol = self.currency_symbols.get(currency, "")
        # Formata com vírgula como separador de milhar e ponto decimal
        formatted_amount = f"{amount:,.2f}"
        return f"{symbol} {formatted_amount}"

    def update_exchange_rate(self, currency: str, rate: float):
        """
        Atualiza a taxa de câmbio de uma moeda (para testes ou ajustes).
        """
        self.exchange_rates[currency] = rate

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Retorna a taxa de câmbio direta de from_currency para to_currency.
        """
        if from_currency not in self.exchange_rates or to_currency not in self.exchange_rates:
            raise ValueError("Moeda inválida")
        return self.exchange_rates[to_currency] / self.exchange_rates[from_currency]
