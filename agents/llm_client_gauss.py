from __future__ import annotations

import os
from typing import Any, Optional

from .llm_client_base import LLMClient, StreamingChunk


class GaussClient(LLMClient):
    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        from gauss_api import GaussAPI  # local wrapper

        self.client = GaussAPI(
            access_key or os.getenv("GAUSS_ACCESS_KEY", ""),
            secret_key or os.getenv("GAUSS_SECRET_KEY", ""),
        )

    def generate(self, prompt: str, stream: bool = False, **kwargs: Any):
        resp = self.client.chat_completion(
            prompt,
            stream=stream,
            temperature=kwargs.get("temperature", 0.3),
            top_p=kwargs.get("top_p", 0.96),
            repetition_penalty=kwargs.get("repetition_penalty", 1.03),
        )
        if stream:
            # Local API returns full JSON; simulate chunking
            if not resp:
                return
            try:
                text = resp["choices"][0]["message"]["content"]
            except Exception:
                text = ""
            for line in text.split("\n"):
                if line:
                    yield StreamingChunk({"text": line + "\n"})
            return
        if not resp:
            return ""
        try:
            return resp["choices"][0]["message"]["content"]
        except Exception:
            return ""


