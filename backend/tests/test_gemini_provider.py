from unittest.mock import AsyncMock, MagicMock
import pytest

from app.core.config import Settings
from app.services.ai_provider.base import AIProviderError
from app.services.ai_provider.gemini import GeminiProvider


@pytest.fixture
def dummy_settings():
    return Settings(
        ai_provider="gemini",
        gemini_api_key="test-key",
        gemini_chat_model="gemini-2.5-flash",
        gemini_embed_model="text-embedding-004",
    )


@pytest.mark.asyncio
async def test_gemini_embed_success(dummy_settings):
    provider = GeminiProvider(dummy_settings)
    
    # Mock genai client embed_content
    mock_item = MagicMock()
    mock_item.values = [0.1] * 768
    mock_result = MagicMock()
    mock_result.embeddings = [mock_item]
    
    provider._client.aio.models.embed_content = AsyncMock(return_value=mock_result)
    
    vec = await provider.embed("hello")
    assert len(vec) == 768
    assert vec[0] == 0.1
    provider._client.aio.models.embed_content.assert_called_once()


@pytest.mark.asyncio
async def test_gemini_embed_fail_closed(dummy_settings):
    provider = GeminiProvider(dummy_settings)
    provider._client.aio.models.embed_content = AsyncMock(side_effect=RuntimeError("API Error"))
    
    with pytest.raises(AIProviderError, match="Gemini embeddings failed"):
        await provider.embed("hello")


@pytest.mark.asyncio
async def test_gemini_chat_success_and_role_merging(dummy_settings):
    provider = GeminiProvider(dummy_settings)
    
    mock_resp = MagicMock()
    mock_resp.text = "Hello from Gemini"
    provider._client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    
    messages = [
        {"role": "user", "content": "Hi"},
        {"role": "user", "content": "How are you?"},  # Consecutive user message should merge
    ]
    reply = await provider.chat(messages, context="You are an assistant.")
    assert reply == "Hello from Gemini"
    
    # Verify call arguments
    call_kwargs = provider._client.aio.models.generate_content.call_args.kwargs
    assert call_kwargs["config"].system_instruction == "You are an assistant."
    assert len(call_kwargs["contents"]) == 1  # The two user messages should merge into 1 turn
    assert len(call_kwargs["contents"][0].parts) == 2


@pytest.mark.asyncio
async def test_gemini_chat_fail_closed(dummy_settings):
    provider = GeminiProvider(dummy_settings)
    provider._client.aio.models.generate_content = AsyncMock(side_effect=ValueError("Quota exceeded"))
    
    with pytest.raises(AIProviderError, match="Gemini chat failed"):
        await provider.chat([{"role": "user", "content": "Hi"}])
