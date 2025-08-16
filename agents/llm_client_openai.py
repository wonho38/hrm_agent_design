from __future__ import annotations

import os
from typing import Any, Optional

from .llm_client_base import LLMClient, StreamingChunk
from .langsmith_config import setup_langsmith, create_run_name, get_langsmith_tags


class OpenAIClient(LLMClient):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Setup LangSmith tracing
        setup_langsmith()

    def generate(self, prompt: str, stream: bool = False, **kwargs: Any):
        # Use LangChain wrapper to enable LangSmith auto-tracing
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        from langchain_core.runnables import RunnableConfig

        llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=kwargs.get("temperature", 0.3),
            max_tokens=kwargs.get("max_tokens", 800),
            top_p=kwargs.get("top_p", 0.9),
        )
        
        # Convert prompt to message format for ChatOpenAI
        messages = [HumanMessage(content=prompt)]
        
        # Configure LangSmith tracing
        config = RunnableConfig(
            run_name=create_run_name("openai", "stream" if stream else "generate"),
            tags=get_langsmith_tags("openai", stream),
            metadata={
                "model": self.model,
                "temperature": kwargs.get("temperature", 0.3),
                "max_tokens": kwargs.get("max_tokens", 800),
                "top_p": kwargs.get("top_p", 0.9),
                "stream": stream,
            }
        )
        
        if stream:
            for chunk in llm.stream(messages, config=config):
                text = getattr(chunk, "content", None) or ""
                if text:
                    yield StreamingChunk({"text": text})
            return
            
        result = llm.invoke(messages, config=config)
        return getattr(result, "content", None) or ""


