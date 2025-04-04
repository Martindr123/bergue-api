# app/tests/unit/test_openai_service.py

import pytest
from api.infrastructure.services.openai_service import OpenAIService

@pytest.mark.asyncio
async def test_openai_service_parser_lettre(mocker):
    mocker.patch("openai.ChatCompletion.create", return_value=mocker.Mock(
        choices=[mocker.Mock(message={"content": '{"nom_prenom_client": "John Doe", "nom_prenom_adresse_client": "Adresse...", "nom_de_l_affaire": "Affaire...", "intro_lettre": "Intro...", "contexte_et_obj": "Contexte...", "matiere_de_mission": "Droit...", "liste_missions": "Missions...", "honoraires": "Honoraires..."}'})]
    ))

    service = OpenAIService()
    result = service.parser_lettre("Lettre Claude")

    assert result.nom_prenom_client == "John Doe"
    assert result.nom_prenom_adresse_client == "Adresse..."
