from __future__ import annotations

import json
from typing import Any, Dict, Generator, Optional

from .llm_providers import build_llm
from .prompt_builder import PromptBuilder
from .guardrails import Guardrail
from .logger import log_event


class DiagnosisSummarizer:
    def __init__(
        self,
        provider: str = "gauss",
        prompt_builder: Optional[PromptBuilder] = None,
        guardrail: Optional[Guardrail] = None,
        **provider_kwargs: Any,
    ) -> None:
        self.provider = provider
        self.provider_kwargs = provider_kwargs
        self.prompt_builder = prompt_builder or PromptBuilder(default_language="ko")
        self.guardrail = guardrail or Guardrail()

    def summarize(self, analytics: Dict[str, Any], language: str = "ko", stream: bool = True):
        payload = {"analytics": analytics, "language": language}
        payload = self.guardrail.pre_guard(payload)
        prompt = self.prompt_builder.build_diagnosis_prompt(analytics, self.provider, language)
        print(f"[DiagnosisSummarizer] provider={self.provider}, language={language}")
        log_event({
            "stage": "diagnosis_build_prompt",
            "provider": self.provider,
            "language": language,
            "prompt_preview": prompt[:300],
        })
        llm = build_llm(self.provider, **self.provider_kwargs)

        if stream:
            preview = []
            for chunk in llm.generate(prompt, stream=True):
                text = chunk.get("text", "")
                if text:
                    if len("".join(preview)) < 500:
                        preview.append(text)
                    yield text
            return

        output = llm.generate(prompt, stream=False)
        log_event({
            "stage": "diagnosis_llm_output",
            "provider": self.provider,
            "language": language,
            "output_preview": (output or "")[:300],
        })
        yield self.guardrail.post_guard(output or "")


