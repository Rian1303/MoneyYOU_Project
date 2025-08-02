"""
Pacote logic

Contém a lógica do aplicativo:
- Autenticação (login)
- Gerenciamento de transações
- Geração de relatórios
"""

from .auth import check_credentials
from .transactions import (
    add_transaction,
    edit_transaction,
    delete_transaction,
    filter_transactions,
)

            