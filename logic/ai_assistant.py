import os
from openai import OpenAI
from dotenv import load_dotenv
from database.data_manager import load_transactions


class AIAssistant:
    """
    Assistente financeiro integrado ao MoneyYOU.
    Usa OpenAI GPT para responder perguntas do usuário sobre suas finanças.
    """

    def __init__(self, model="gpt-4o-mini"):
        self.model = model

        # 1️⃣ Carrega automaticamente o arquivo .env
        # Procura em logic/openai_key.env e config/openai_key.env
        possible_envs = [
            os.path.join(os.path.dirname(__file__), "openai_key.env"),               # logic/
            os.path.join(os.path.dirname(__file__), "..", "config", "openai_key.env") # config/
        ]
        loaded = False
        for env_path in possible_envs:
            if os.path.exists(env_path):
                load_dotenv(env_path)
                print(f"[DEBUG] OPENAI .env carregado de: {env_path}")
                loaded = True
                break

        if not loaded:
            print("⚠️ Nenhum arquivo openai_key.env encontrado. O assistente pode não funcionar.")

        # 2️⃣ Pega a chave do ambiente
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("❌ OPENAI_API_KEY não encontrado. Verifique o openai_key.env")

        # 3️⃣ Inicializa o cliente OpenAI
        self.client = OpenAI(api_key=api_key)

    # ------------------- Função principal -------------------
    def ask(self, user_message: str, user_id: str) -> str:
        """
        Pergunta à IA usando a mensagem do usuário e suas transações financeiras.
        """
        try:
            transactions = load_transactions(user_id=user_id)

            if transactions:
                user_prompt = (
                    f"Você é um assistente financeiro do MoneyYOU.\n"
                    f"📊 Transações do usuário:\n{transactions}\n\n"
                    f"💬 Pergunta do usuário: {user_message}"
                )
            else:
                user_prompt = f"💬 Pergunta do usuário: {user_message}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente financeiro do MoneyYOU. Responda sempre de forma clara e prática."},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=600,
                temperature=0.6
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"⚠️ Erro ao acessar a IA: {e}"

    # ------------------- Alias para Dashboard -------------------
    def reply(self, user_message: str, user_id: str) -> str:
        """
        Alias de ask(), usado pelo Dashboard para enviar perguntas.
        """
        return self.ask(user_message, user_id)
