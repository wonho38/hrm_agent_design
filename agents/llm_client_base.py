from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class StreamingChunk(dict):
    """Simple chunk container for streaming."""
    pass


class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, stream: bool = False, **kwargs: Any) -> Any:  # pragma: no cover - interface
        ...


