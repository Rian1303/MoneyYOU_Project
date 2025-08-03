"""
Pacote logic

Contém a lógica do aplicativo:
- Autenticação (login)
- Gerenciamento de transações
- Geração de relatórios
"""

from .auth import validate_login, validate_registration, register_user
from .transactions import (
    add_transaction,
    edit_transaction,
    delete_transaction,
    filter_transactions,
)

            