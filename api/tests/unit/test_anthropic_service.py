# app/tests/unit/test_anthropic_service.py

import pytest
from api.infrastructure.services.anthropic_service import AnthropicClient

@pytest.mark.asyncio
async def test_anthropic_service(mocker):
    # On mock la méthode completions.create
    mock_client = mocker.Mock()
    mock_client.completions.create.return_value = mocker.Mock(completion="Réponse Claude")

    anthro_client = AnthropicClient(api_key="fake_key")
    anthro_client.client = mock_client  # injection du mock

    result = anthro_client.generate_claude_answer("Compte rendu", "Missions")
    assert result == "Réponse Claude"
