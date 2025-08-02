from config import USERS, MIN_PASSWORD_LENGTH

def validate_login(username: str, password: str) -> bool:
    """
    Verifica se o usuário existe e a senha está correta.
    """
    return USERS.get(username) == password

def validate_registration(username: str, password: str, confirm_password: str) -> (bool, str):
    """
    Valida os dados do cadastro.
    Retorna (True, mensagem) se válido, (False, mensagem) se inválido.
    """
    if not username or not password or not confirm_password:
        return False, "Preencha todos os campos."

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres."

    if password != confirm_password:
        return False, "As senhas não conferem."

    if username in USERS:
        return False, "Usuário já existe."

    return True, "Cadastro válido."

def register_user(username: str, password: str) -> None:
    """
    Registra um novo usuário no sistema (em memória).
    """
    if username not in USERS:
        USERS[username] = password
    else:
        raise ValueError("Usuário já existe.")
