from datetime import datetime
from database.data_manager import (
    add_transaction as db_add_transaction,
    load_transactions,
    edit_transaction as db_edit_transaction,
    delete_transaction as db_delete_transaction
)

from logic.firebase import send_transaction_to_firebase  # 🔹 NOVO

def add_transaction(data: dict) -> dict:
    """
    Adiciona uma nova transação na base local e no Firebase.
    """
    try:
        if 'date' not in data or not data['date']:
            data['date'] = datetime.now().strftime('%d/%m/%Y')
        else:
            try:
                datetime.strptime(data['date'], '%d/%m/%Y')
            except ValueError:
                return {"status": "error", "message": "Data inválida. Use o formato dd/mm/yyyy."}

        # Salva localmente (SQLite)
        db_add_transaction(data)

        # Tenta enviar ao Firebase
        try:
            send_transaction_to_firebase(data)
        except Exception as e:
            print(f"[Aviso] Firebase falhou, mas transação local foi salva: {e}")

        return {"status": "success", "message": "Transação adicionada com sucesso."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def edit_transaction(id: int, new_data: dict) -> bool:
    """
    Edita transação pelo id.
    Retorna True se editou, False se não encontrou.
    """
    return db_edit_transaction(id, new_data)

def delete_transaction(id: int) -> bool:
    """
    Deleta transação pelo id.
    Retorna True se deletou, False se não encontrou.
    """
    return db_delete_transaction(id)

def filter_transactions(transactions: list, tipo=None, categoria=None, data_inicio=None, data_fim=None) -> list:
    """
    Filtra transações por tipo, categoria e intervalo de datas (strings dd/mm/yyyy).
    """
    filtered = transactions
    date_format = "%d/%m/%Y"

    if tipo:
        filtered = [t for t in filtered if t.get('type', '').lower() == tipo.lower()]

    if categoria:
        filtered = [t for t in filtered if t.get('category', '').lower() == categoria.lower()]

    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, date_format)
            filtered = [t for t in filtered if datetime.strptime(t.get('date', '01/01/1900'), date_format) >= dt_inicio]
        except Exception:
            pass

    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, date_format)
            filtered = [t for t in filtered if datetime.strptime(t.get('date', '01/01/1900'), date_format) <= dt_fim]
        except Exception:
            pass

    return filtered

def calcular_saldo(transactions: list) -> float:
    """
    Calcula saldo total com base no tipo das transações ('entrada' soma, 'saida' subtrai).
    """
    saldo = 0.0
    for t in transactions:
        try:
            valor = float(t.get('amount', 0))
        except (ValueError, TypeError):
            valor = 0.0

        tipo = t.get('type', '').lower()
        if tipo == 'entrada':
            saldo += valor
        elif tipo == 'saida':
            saldo -= valor

    return saldo
