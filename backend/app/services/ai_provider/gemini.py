"""Google Gemini implementation of the AIProvider interface.

Uses the official google-genai SDK (`from google import genai`).
Handles OpenAI-style message conversion, system instructions extraction,
consecutive role merging, batching for embeddings, and strict fail-closed
error handling.
"""
from collections.abc import AsyncIterator

from google import genai
from google.genai import types

from app.core.config import Settings
from app.services.ai_provider.base import AIProvider, AIProviderError


class GeminiProvider(AIProvider):
    def __init__(self, settings: Settings):
        self._api_key = settings.gemini_api_key or "dummy-api-key"
        self._chat_model = getattr(settings, "gemini_chat_model", "gemini-2.5-flash")
        self._embed_model = getattr(settings, "gemini_embed_model", "text-embedding-004")
        self._client = genai.Client(api_key=self._api_key)

    # ---------- EMBEDDINGS ----------
    async def embed(self, text: str) -> list[float]:
        vectors = await self.embed_batch([text])
        if not vectors:
            raise AIProviderError("Gemini embed returned no vector.")
        return vectors[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            # Batch embedding chunking (max 50 per API request)
            chunk_size = 50
            all_vectors: list[list[float]] = []
            for i in range(0, len(texts), chunk_size):
                batch = texts[i : i + chunk_size]
                result = await self._client.aio.models.embed_content(
                    model=self._embed_model,
                    contents=batch,
                )
                if not result or not hasattr(result, "embeddings") or result.embeddings is None:
                    raise AIProviderError("Gemini embed_content returned no embeddings.")
                for item in result.embeddings:
                    all_vectors.append(list(item.values))
            return all_vectors
        except Exception as exc:
            if isinstance(exc, AIProviderError):
                raise
            # Fail closed: always raise AIProviderError on failure
            raise AIProviderError(f"Gemini embeddings failed: {exc}") from exc

    # ---------- CHAT ----------
    async def chat(self, messages: list[dict], context: str | None = None) -> str:
        contents, config = self._prepare_gemini_inputs(messages, context)
        try:
            response = await self._client.aio.models.generate_content(
                model=self._chat_model,
                contents=contents,
                config=config,
            )
            if response.text is not None:
                return response.text
            # Fallback if text property is empty but candidates exist
            if response.candidates and response.candidates[0].content:
                parts = response.candidates[0].content.parts
                return "".join(p.text for p in parts if p.text)
            return ""
        except Exception as exc:
            raise AIProviderError(f"Gemini chat failed: {exc}") from exc

    async def chat_stream(
        self, messages: list[dict], context: str | None = None
    ) -> AsyncIterator[str]:
        contents, config = self._prepare_gemini_inputs(messages, context)
        try:
            stream = await self._client.aio.models.generate_content_stream(
                model=self._chat_model,
                contents=contents,
                config=config,
            )
            async for chunk in stream:
                if chunk.text:
                    yield chunk.text
        except Exception as exc:
            raise AIProviderError(f"Gemini stream failed: {exc}") from exc

    def _prepare_gemini_inputs(
        self, messages: list[dict], context: str | None = None
    ) -> tuple[list[types.Content], types.GenerateContentConfig]:
        all_messages = []
        if context:
            all_messages.append({"role": "system", "content": context})
        all_messages.extend(messages)

        system_texts = []
        contents: list[types.Content] = []

        for m in all_messages:
            role = m.get("role", "user")
            content_str = str(m.get("content", ""))
            if role == "system":
                if content_str:
                    system_texts.append(content_str)
                continue

            gemini_role = "model" if role in ("assistant", "model") else "user"
            part = types.Part.from_text(text=content_str)

            # Avoid consecutive messages with identical roles
            if contents and contents[-1].role == gemini_role:
                contents[-1].parts.append(part)
            else:
                contents.append(types.Content(role=gemini_role, parts=[part]))

        if not contents:
            fallback_text = "\n\n".join(system_texts) if system_texts else "Hello"
            contents.append(
                types.Content(role="user", parts=[types.Part.from_text(text=fallback_text)])
            )
            system_texts.clear()

        config = types.GenerateContentConfig(
            system_instruction="\n\n".join(system_texts) if system_texts else None,
            temperature=0.2,
        )
        return contents, config
