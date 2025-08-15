from __future__ import annotations

import os
from typing import Any, Optional

from .llm_client_base import LLMClient, StreamingChunk


class OpenAIClient(LLMClient):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def generate(self, prompt: str, stream: bool = False, **kwargs: Any):
        # Use LangChain wrapper to enable LangSmith auto-tracing
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=kwargs.get("temperature", 0.3),
            max_tokens=kwargs.get("max_tokens", 800),
            top_p=kwargs.get("top_p", 0.9),
        )
        if stream:
            for chunk in llm.stream(prompt):
                text = getattr(chunk, "content", None) or ""
                if text:
                    yield StreamingChunk({"text": text})
            return
        result = llm.invoke(prompt)
        return getattr(result, "content", None) or ""


