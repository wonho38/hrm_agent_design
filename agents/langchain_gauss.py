"""Custom LangChain LLM for Gauss API."""

from __future__ import annotations

import os
from typing import Any, Dict, Iterator, List, Mapping, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk

from gauss_api import GaussAPI
 

from pydantic import PrivateAttr


class GaussLLM(LLM):
    """Custom LangChain LLM wrapper for Gauss API."""
    
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    temperature: float = 0.3
    top_p: float = 0.96
    repetition_penalty: float = 1.03
    
    _client: GaussAPI = PrivateAttr()
    
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._client = GaussAPI(
            access_key=self.access_key or os.getenv("GAUSS_ACCESS_KEY", ""),
            secret_key=self.secret_key or os.getenv("GAUSS_SECRET_KEY", ""),
        )
        
        

    @property
    def _llm_type(self) -> str:
        """Return identifier of LLM."""
        return "gauss"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "repetition_penalty": self.repetition_penalty,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call out to Gauss API."""
        
        response = self._client.chat_completion(
            prompt,
            stream=False,
            temperature=kwargs.get("temperature", self.temperature),
            top_p=kwargs.get("top_p", self.top_p),
            repetition_penalty=kwargs.get("repetition_penalty", self.repetition_penalty),
        )
        
        if not response:
            return ""
            
        try:
            result = response["choices"][0]["message"]["content"]
            return result
        except (KeyError, IndexError) as e:
            return ""

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Stream the LLM on the given prompt."""
        
        response = self._client.chat_completion(
            prompt,
            stream=True,
            temperature=kwargs.get("temperature", self.temperature),
            top_p=kwargs.get("top_p", self.top_p),
            repetition_penalty=kwargs.get("repetition_penalty", self.repetition_penalty),
        )
        
        # Fallback: if streaming response is empty, try non-streaming once
        if not response:
            response = self._client.chat_completion(
                prompt,
                stream=False,
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                repetition_penalty=kwargs.get("repetition_penalty", self.repetition_penalty),
            )
            if not response:
                # As a last resort, emit a single empty chunk to avoid upstream errors
                yield GenerationChunk(text="")
                return
            
        try:
            text = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            # If parsing fails, try non-streaming fallback
            response = self._client.chat_completion(
                prompt,
                stream=False,
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                repetition_penalty=kwargs.get("repetition_penalty", self.repetition_penalty),
            )
            try:
                text = response["choices"][0]["message"]["content"] if response else ""
            except Exception:
                text = ""
            if text == "":
                # Emit a single empty chunk so that callers do not crash
                yield GenerationChunk(text="")
                return
            
        # Simulate streaming by splitting into lines
        full_response = ""
        for line in text.split("\n"):
            if line:
                chunk_text = line + "\n"
                chunk = GenerationChunk(text=chunk_text)
                full_response += chunk_text
                
                yield chunk
        
        # Completed streaming
