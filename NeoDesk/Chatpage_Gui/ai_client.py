from openai import OpenAI
import os
from dotenv import load_dotenv
from log_setup import get_logger
logger = get_logger(__name__)

# .env aus Projektwurzel laden (eine Ebene über Chatpage_Gui)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)


class AIClient:
    """
    Schlichtes Wrapper-Objekt für OpenAI Chat Completions.
    Nutzt OPENAI_API_KEY aus .env.
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY fehlt (.env in der Projektwurzel).")
        self.client = OpenAI(api_key=api_key)

    def ask(self, prompt: str) -> str:
        """
        Sendet die Nutzereingabe an das Modell und gibt den Antworttext zurück.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.exception('Unhandled exception')
            return f"Fehler: {e}"