"""Custom LangChain LLM for GaussO API."""

from __future__ import annotations

import os
from typing import Any, Dict, Iterator, List, Mapping, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk

from gausso_api import GaussOAPI
from .langsmith_config import setup_langsmith


class GaussOLLM(LLM):
    """Custom LangChain LLM wrapper for GaussO API."""
    
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    temperature: float = 0.3
    top_p: float = 0.96
    repetition_penalty: float = 1.03
    
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.client = GaussOAPI(
            access_key=self.access_key or os.getenv("GAUSSO_ACCESS_KEY", ""),
            secret_key=self.secret_key or os.getenv("GAUSSO_SECRET_KEY", ""),
        )
        
        # Setup LangSmith tracing
        setup_langsmith()

    @property
    def _llm_type(self) -> str:
        """Return identifier of LLM."""
        return "gausso"

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
        """Call out to GaussO API."""
        # Log the call to LangSmith if run_manager is available
        if run_manager:
            run_manager.on_llm_start(
                serialized={"name": "GaussOLLM"},
                prompts=[prompt],
                run_id=run_manager.run_id,
                tags=["gausso", "custom-llm"],
                metadata={
                    "temperature": kwargs.get("temperature", self.temperature),
                    "top_p": kwargs.get("top_p", self.top_p),
                    "repetition_penalty": kwargs.get("repetition_penalty", self.repetition_penalty),
                }
            )
        
        response = self.client.chat_completion(
            prompt,
            stream=False,
            temperature=kwargs.get("temperature", self.temperature),
            top_p=kwargs.get("top_p", self.top_p),
            repetition_penalty=kwargs.get("repetition_penalty", self.repetition_penalty),
        )
        
        if not response:
            if run_manager:
                run_manager.on_llm_error(Exception("Empty response from GaussO API"))
            return ""
            
        try:
            result = response["choices"][0]["message"]["content"]
            if run_manager:
                run_manager.on_llm_end(
                    response={"generations": [[{"text": result}]]},
                    run_id=run_manager.run_id
                )
            return result
        except (KeyError, IndexError) as e:
            if run_manager:
                run_manager.on_llm_error(e)
            return ""

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Stream the LLM on the given prompt."""
        # Log the streaming call to LangSmith if run_manager is available
        if run_manager:
            run_manager.on_llm_start(
                serialized={"name": "GaussOLLM"},
                prompts=[prompt],
                run_id=run_manager.run_id,
                tags=["gausso", "custom-llm", "streaming"],
                metadata={
                    "temperature": kwargs.get("temperature", self.temperature),
                    "top_p": kwargs.get("top_p", self.top_p),
                    "repetition_penalty": kwargs.get("repetition_penalty", self.repetition_penalty),
                    "streaming": True,
                }
            )
        
        response = self.client.chat_completion(
            prompt,
            stream=True,
            temperature=kwargs.get("temperature", self.temperature),
            top_p=kwargs.get("top_p", self.top_p),
            repetition_penalty=kwargs.get("repetition_penalty", self.repetition_penalty),
        )
        
        if not response:
            if run_manager:
                run_manager.on_llm_error(Exception("Empty response from GaussO API"))
            return
            
        try:
            text = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            if run_manager:
                run_manager.on_llm_error(e)
            return
            
        # Simulate streaming by splitting into lines
        full_response = ""
        for line in text.split("\n"):
            if line:
                chunk_text = line + "\n"
                chunk = GenerationChunk(text=chunk_text)
                full_response += chunk_text
                
                if run_manager:
                    run_manager.on_llm_new_token(chunk.text, chunk=chunk)
                yield chunk
        
        # Log completion to LangSmith
        if run_manager:
            run_manager.on_llm_end(
                response={"generations": [[{"text": full_response}]]},
                run_id=run_manager.run_id
            )
