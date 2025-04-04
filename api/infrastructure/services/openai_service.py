# app/infrastructure/services/openai_service.py

import os
import json
from dotenv import load_dotenv
from pydantic import ValidationError
from typing import Any, Dict

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from api.config import config
openai_model = config.get("openai_model")

# Ici, on ne montre pas l'implémentation "OpenAI" exact car vous aviez du pseudo-code.
# On fait quelque chose d'analogue avec l'API standard d'OpenAI.

import openai
openai.api_key = OPENAI_API_KEY

from api.core.domain.entities.letter_entity import StructuredLetter

class OpenAIService:
    def parser_lettre(self, claude_response: str) -> StructuredLetter:
        """
        Envoie la réponse de Claude à l'API OpenAI en demandant de parser en JSON.
        Retourne un objet StructuredLetter.
        """
        # Prompt final
        system_prompt = """
Tu es chargé de parser la lettre de mission dans un JSON strict, au format :
{
  "nom_prenom_client": "...",
  "nom_prenom_adresse_client": "...",
  "nom_de_l_affaire": "...",
  "intro_lettre": "...",
  "contexte_et_obj": "...",
  "matiere_de_mission": "...",
  "liste_missions": "...",
  "honoraires": "..."
}
Tous les éléments importants (noms, chiffres) doivent être entourés de **...**. 
Ne renvoie QUE ce JSON, sans texte supplémentaire.
"""

        user_prompt = f"""
Voici la lettre de mission à parser :
{claude_response}
"""

        response = openai.ChatCompletion.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        raw_content = response.choices[0].message["content"].strip()

        # On essaie de parser le JSON
        try:
            parsed_dict = json.loads(raw_content)
            structured_letter = StructuredLetter(**parsed_dict)
            return structured_letter
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Erreur lors du parsing JSON : {str(e)}")

# Instanciation globale (exemple)
openai_service = OpenAIService()
