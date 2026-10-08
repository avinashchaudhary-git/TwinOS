import httpx

from app.core.config import settings
from app.core.logging import logger
from app.llm.mock_llm import MockLLM
from app.llm.prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT_TEMPLATE


class LLMProvider:
    def __init__(self, provider_type: str | None = None):
        self.provider_type = provider_type or settings.LLM_PROVIDER
        self.mock_llm = MockLLM()

    def generate_answer(self, question: str, context: str) -> str:
        """Generates an answer using the configured provider (mock, openai, or gemini)."""
        if self.provider_type == "mock" or not (settings.OPENAI_API_KEY or settings.GEMINI_API_KEY):
            return self.mock_llm.generate(
                prompt=RAG_SYSTEM_PROMPT, context=context, question=question
            )

        # Real OpenAI mode
        if self.provider_type == "openai" and settings.OPENAI_API_KEY:
            try:
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": RAG_SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": RAG_USER_PROMPT_TEMPLATE.format(
                                context=context, question=question
                            ),
                        },
                    ],
                    "temperature": 0.1,
                }
                with httpx.Client(timeout=30) as client:
                    res = client.post(
                        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
                    )
                    res.raise_for_url()
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"OpenAI call failed ({e}). Falling back to deterministic mock LLM.")
                return self.mock_llm.generate(
                    prompt=RAG_SYSTEM_PROMPT, context=context, question=question
                )

        # Real Gemini mode
        if self.provider_type == "gemini" and settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
                prompt_text = f"{RAG_SYSTEM_PROMPT}\n\n{RAG_USER_PROMPT_TEMPLATE.format(context=context, question=question)}"
                payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
                with httpx.Client(timeout=30) as client:
                    res = client.post(url, json=payload)
                    res.raise_for_status()
                    data = res.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                logger.error(f"Gemini call failed ({e}). Falling back to deterministic mock LLM.")
                return self.mock_llm.generate(
                    prompt=RAG_SYSTEM_PROMPT, context=context, question=question
                )

        return self.mock_llm.generate(prompt=RAG_SYSTEM_PROMPT, context=context, question=question)


def get_llm_provider() -> LLMProvider:
    return LLMProvider()
