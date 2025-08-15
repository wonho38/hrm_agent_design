from __future__ import annotations

from typing import Any

from .llm_client_base import LLMClient, StreamingChunk
from .llm_client_openai import OpenAIClient
from .llm_client_bedrock import BedrockClient
from .llm_client_gauss import GaussClient
from .llm_client_gausso import GaussOClient


def build_llm(provider: str, **kwargs: Any) -> LLMClient:
    key = (provider or "").lower()
    if key in ("openai", "oai"):
        return OpenAIClient(model=kwargs.get("model"), api_key=kwargs.get("api_key"))
    if key in ("bedrock", "aws"):
        return BedrockClient(model_id=kwargs.get("model_id"), region=kwargs.get("region"))
    if key in ("gauss",):
        return GaussClient(access_key=kwargs.get("access_key"), secret_key=kwargs.get("secret_key"))
    if key in ("gausso", "gauss_o", "gauss-vision"):
        return GaussOClient(access_key=kwargs.get("access_key"), secret_key=kwargs.get("secret_key"))
    raise ValueError(f"Unsupported LLM provider: {provider}")

