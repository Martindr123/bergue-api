# app/tests/unit/test_doc_generation_service.py

import pytest
from api.core.domain.services.doc_generation_service import DocGenerationService
from api.infrastructure.services.anthropic_service import AnthropicClient
from api.infrastructure.services.openai_service import OpenAIService

from api.core.domain.entities.letter_entity import StructuredLetter

@pytest.mark.asyncio
async def test_doc_generation_service(mocker):
    # Mock des clients
    mock_anthropic_client = mocker.Mock(spec=AnthropicClient)
    mock_openai_service = mocker.Mock(spec=OpenAIService)

    service = DocGenerationService(mock_anthropic_client, mock_openai_service)

    # Mocks
    mock_anthropic_client.generate_claude_answer.return_value = "Réponse Claude"

    # ICI on renvoie un vrai StructuredLetter:
    fake_letter = StructuredLetter(
        nom_prenom_client="**John**",
        nom_prenom_adresse_client="**Adresse**",
        nom_de_l_affaire="**Affaire**",
        intro_lettre="**Intro**",
        contexte_et_obj="**Contexte**",
        matiere_de_mission="**Matière**",
        liste_missions="**Missions**",
        honoraires="**Honoraires**",
    )
    mock_openai_service.parser_lettre.return_value = fake_letter

    # Test extraction
    txt_data = b"Hello world"
    text = service.extract_text_from_file(txt_data, ".txt")
    assert text == "Hello world"

    # Test generate_letter
    letter = service.generate_letter("Texte CR", "Missions")
    mock_anthropic_client.generate_claude_answer.assert_called_once()
    mock_openai_service.parser_lettre.assert_called_once()

    # Test build_docx_from_letter -> On ne renvoie plus un Mock, mais le vrai objet
    result_bytes = service.build_docx_from_letter(fake_letter, "1500")
    assert isinstance(result_bytes, bytes)
