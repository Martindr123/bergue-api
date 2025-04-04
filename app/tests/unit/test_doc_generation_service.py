# app/tests/unit/test_doc_generation_service.py

import pytest
from app.core.domain.services.doc_generation_service import DocGenerationService
from app.infrastructure.services.anthropic_service import AnthropicClient
from app.infrastructure.services.openai_service import OpenAIService

@pytest.mark.asyncio
async def test_doc_generation_service(mocker):
    # Mock des clients
    mock_anthropic_client = mocker.Mock(spec=AnthropicClient)
    mock_openai_service = mocker.Mock(spec=OpenAIService)

    service = DocGenerationService(mock_anthropic_client, mock_openai_service)

    # Mocks
    mock_anthropic_client.generate_claude_answer.return_value = "Réponse Claude"
    mock_openai_service.parser_lettre.return_value = "Structure Lettres"

    # Test extraction
    txt_data = b"Hello world"
    text = service.extract_text_from_file(txt_data, ".txt")
    assert text == "Hello world"

    # Test generate_letter
    letter = service.generate_letter("Texte CR", "Missions")
    mock_anthropic_client.generate_claude_answer.assert_called_once()
    mock_openai_service.parser_lettre.assert_called_once()

    # Test build_docx_from_letter -> on ne va pas forcément vérifier le binaire,
    # on peut juste vérifier que ça retourne des bytes:
    mock_openai_service.parser_lettre.return_value = mocker.Mock()
    result_bytes = service.build_docx_from_letter(mock_openai_service.parser_lettre.return_value, "1500")
    assert isinstance(result_bytes, bytes)
