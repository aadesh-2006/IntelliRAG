import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException, status
from app.config import settings

class BaseLLMService(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        pass

class MockLLMService(BaseLLMService):
    def __init__(self, model_name: str = "mock-model"):
        self._model_name = model_name

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        if "=== RETRIEVED DOCUMENT CONTEXT ===" not in user_prompt:
            return "The provided documents do not contain sufficient information to answer this question."

        context_match = re.search(
            r"=== RETRIEVED DOCUMENT CONTEXT ===\n(.*?)\n=== END DOCUMENT CONTEXT ===",
            user_prompt,
            re.DOTALL
        )
        context_text = context_match.group(1).strip() if context_match else ""

        if not context_text or context_text == "No relevant context found.":
            return "The provided documents do not contain sufficient information to answer this question."

        source_blocks = re.findall(r"\[SOURCE (\d+) \| DOC: (.*?)\]\n(.*?)(?=\n\[SOURCE|\Z)", context_text, re.DOTALL)
        
        query_match = re.search(r"User Query:\s*(.*)", user_prompt)
        query = query_match.group(1).strip() if query_match else ""

        if not source_blocks:
            return f"Based on the provided documents: {context_text[:200]}..."

        answer_parts = []
        for src_id, doc_name, content in source_blocks:
            clean_content = content.strip().replace("\n", " ")
            if len(clean_content) > 120:
                clean_content = clean_content[:120] + "..."
            answer_parts.append(f"{clean_content} [Source {src_id}]")

        summary = " ".join(answer_parts)
        return f"Based on the provided documentation, {summary}"

class GeminiLLMService(BaseLLMService):
    def __init__(
        self,
        api_key: str = settings.LLM_API_KEY,
        model_name: str = settings.LLM_MODEL
    ):
        self.api_key = api_key
        self._model_name = model_name

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key is not configured"
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model_name}:generateContent?key={self.api_key}"
        
        payload: Dict[str, Any] = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            "generationConfig": {
                "temperature": temperature if temperature is not None else settings.LLM_TEMPERATURE,
                "maxOutputTokens": max_tokens if max_tokens is not None else settings.LLM_MAX_OUTPUT_TOKENS,
            }
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, json=payload)
                if res.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Gemini API returned error {res.status_code}: {res.text}"
                    )
                data = res.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return "The model did not return any candidates."
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    return "The model returned an empty response."
                return parts[0].get("text", "")
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to communicate with LLM provider: {str(exc)}"
            )

def get_llm_service() -> BaseLLMService:
    provider = settings.LLM_PROVIDER.lower().strip()
    if provider == "gemini" and settings.LLM_API_KEY:
        return GeminiLLMService()
    return MockLLMService(model_name=settings.LLM_MODEL)

llm_service: BaseLLMService = get_llm_service()
