# app/infrastructure/services/anthropic_service.py

import os
import json
import anthropic
from dotenv import load_dotenv

# Chargement du .env
load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Lecture de la config
from api.config import config

claude_model = config.get("claude_model")

class AnthropicClient:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_claude_answer(self, compte_rendu: str, missions_intro: str) -> str:
        prompt_user = f"""
A l'aide du compte-rendu de réunion avec le client :
{compte_rendu}
--------------------------

Rédige la lettre de mission pour les missions suivantes :
{missions_intro}
"""
        prompt_system = f"""
Tu es l'assistant d'un avocat expérimenté...
Voici un exemple d'une de ses lettres de missions (fichier model.txt)...
Renvoie aussi les zones de tabulations en mettant les balises (\\t).

(Le style complet se trouve dans le template model.txt)
"""

        # On concatène (chez Anthropic, c’est un peu différent. On construit le message)
        # NOTE: le code ici est simplifié, vous pouvez adapter selon anthropic-python
        response = self.client.completions.create(
            model=claude_model,
            max_tokens_to_sample=5000,
            temperature=0.7,
            prompt=anthropic.HUMAN_PROMPT + prompt_user + anthropic.AI_PROMPT + prompt_system,
        )
        return response.completion

# Instanciation globale (exemple)
anthropic_client = AnthropicClient(api_key=CLAUDE_API_KEY)
