from __future__ import annotations

import os
from typing import Any, Optional

from .llm_client_base import LLMClient, StreamingChunk
from .langchain_gauss import GaussLLM
 


class GaussClient(LLMClient):
    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.llm = GaussLLM(
            access_key=access_key or os.getenv("GAUSS_ACCESS_KEY", ""),
            secret_key=secret_key or os.getenv("GAUSS_SECRET_KEY", ""),
            temperature=0.3,
            top_p=0.96,
            repetition_penalty=1.03,
        )
        

    def generate(self, prompt: str, stream: bool = False, **kwargs: Any):
        # Update LLM parameters if provided
        if "temperature" in kwargs:
            self.llm.temperature = kwargs["temperature"]
        if "top_p" in kwargs:
            self.llm.top_p = kwargs["top_p"]
        if "repetition_penalty" in kwargs:
            self.llm.repetition_penalty = kwargs["repetition_penalty"]
        
        if stream:
            # Use LangChain's streaming
            for chunk in self.llm.stream(prompt, **kwargs):
                text = getattr(chunk, "text", "") or ""
                if text:
                    yield StreamingChunk({"text": text})
            return
            
        # Use LangChain's invoke
        result = self.llm.invoke(prompt, **kwargs)
        return result or ""


