from __future__ import annotations

import os
from typing import Any, Optional

from .llm_client_base import LLMClient, StreamingChunk
from .langchain_gausso import GaussOLLM
from .langsmith_config import setup_langsmith, create_run_name, get_langsmith_tags


class GaussOClient(LLMClient):
    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.llm = GaussOLLM(
            access_key=access_key or os.getenv("GAUSSO_ACCESS_KEY", ""),
            secret_key=secret_key or os.getenv("GAUSSO_SECRET_KEY", ""),
            temperature=0.3,
            top_p=0.96,
            repetition_penalty=1.03,
        )
        
        # Setup LangSmith tracing
        setup_langsmith()

    def generate(self, prompt: str, stream: bool = False, **kwargs: Any):
        # Update LLM parameters if provided
        if "temperature" in kwargs:
            self.llm.temperature = kwargs["temperature"]
        if "top_p" in kwargs:
            self.llm.top_p = kwargs["top_p"]
        if "repetition_penalty" in kwargs:
            self.llm.repetition_penalty = kwargs["repetition_penalty"]
        
        # Configure LangSmith tracing
        from langchain_core.runnables import RunnableConfig
        
        config = RunnableConfig(
            run_name=create_run_name("gausso", "stream" if stream else "generate"),
            tags=get_langsmith_tags("gausso", stream),
            metadata={
                "temperature": kwargs.get("temperature", self.llm.temperature),
                "top_p": kwargs.get("top_p", self.llm.top_p),
                "repetition_penalty": kwargs.get("repetition_penalty", self.llm.repetition_penalty),
                "stream": stream,
            }
        )
            
        if stream:
            # Use LangChain's streaming
            for chunk in self.llm.stream(prompt, config=config, **kwargs):
                text = getattr(chunk, "text", "") or ""
                if text:
                    yield StreamingChunk({"text": text})
            return
            
        # Use LangChain's invoke
        result = self.llm.invoke(prompt, config=config, **kwargs)
        return result or ""


