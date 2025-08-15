from __future__ import annotations

import os
from typing import Any, Optional

from .llm_client_base import LLMClient, StreamingChunk


class BedrockClient(LLMClient):
    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        # Defer to LangChain's Bedrock wrapper for LangSmith tracing
        self.model_id = model_id or os.getenv(
            "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"
        )
        self.region = region or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "ap-northeast-2"

    def generate(self, prompt: str, stream: bool = False, **kwargs: Any):
        from langchain_aws import ChatBedrock

        llm = ChatBedrock(
            model_id=self.model_id,
            region_name=self.region,
            # temperature/top_p supported for some providers; harmless if ignored
            model_kwargs={
                "temperature": kwargs.get("temperature", 0.3),
                "top_p": kwargs.get("top_p", 0.9),
                "max_tokens": kwargs.get("max_tokens", 800),
            },
        )
        if stream:
            for chunk in llm.stream(prompt):
                text = getattr(chunk, "content", None) or ""
                if text:
                    yield StreamingChunk({"text": text})
            return
        result = llm.invoke(prompt)
        return getattr(result, "content", None) or ""


