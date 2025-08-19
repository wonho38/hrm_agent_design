from __future__ import annotations

from typing import Any, Dict, Optional

from .llm_providers import build_llm
from .prompt_builder import PromptBuilder
from .guardrails import Guardrail
from .logger import log_event


class GuideProvider:
    def __init__(
        self,
        provider: str = "openai",
        prompt_builder: Optional[PromptBuilder] = None,
        guardrail: Optional[Guardrail] = None,
        **provider_kwargs: Any,
    ) -> None:
        self.provider = provider
        self.provider_kwargs = provider_kwargs
        self.prompt_builder = prompt_builder or PromptBuilder(default_language="ko")
        self.guardrail = guardrail or Guardrail()

    def provide(self, diagnosis_summary: str, op_summary: str, language: str = "ko", stream: bool = True):
        payload = {"diagnosis_summary": diagnosis_summary, "op_summary": op_summary, "language": language}
        payload = self.guardrail.pre_guard(payload)
        
        # Build prompt using PromptBuilder
        prompt = self.prompt_builder.build_guide_prompt(diagnosis_summary, op_summary, self.provider, language)
        print(f"[GuideProvider] provider={self.provider}, language={language}")
        log_event({
            "stage": "guide_build_prompt",
            "provider": self.provider,
            "language": language,
            "prompt_preview": prompt[:300],
        })
        llm = build_llm(self.provider, **self.provider_kwargs)

        # For Gauss provider, force non-streaming and emit once
        if stream and self.provider.lower() != "gauss":
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
            "stage": "guide_llm_output",
            "provider": self.provider,
            "language": language,
            "output_preview": (output or "")[:300],
        })
        yield self.guardrail.post_guard(output or "")


