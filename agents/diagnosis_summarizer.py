from __future__ import annotations

import json
from typing import Any, Dict, Generator, List, Optional

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

    def _build_diagnosis_text(self, analytics: Dict[str, Any]) -> str:
        """Build diagnosis text from analytics data."""
        diagnosis_lists: List[Dict[str, Any]] = analytics.get("diagnosisLists", [])
        
        diagnosis_summary: List[str] = []
        for diagnosis_group in diagnosis_lists:
            device_sub_type = diagnosis_group.get("deviceSubType", "Unknown")
            diagnosis_result = diagnosis_group.get("diagnosisResult", "Unknown")
            diagnosis_summary.append(f"Device Sub Type: {device_sub_type}")
            diagnosis_summary.append(f"Overall Diagnosis Result: {diagnosis_result}")
            for d in diagnosis_group.get("diagnosisList", []):
                title = d.get("title", "Unknown")
                label = d.get("diagnosisLabel", "Unknown")
                code = d.get("diagnosisCode", "Unknown")
                result = d.get("diagnosisResult", "Unknown")
                description = d.get("diagnosisDescription", "No description available")
                diagnosis_summary.append(f"- {title} ({label}, Code: {code}): {result}")
                diagnosis_summary.append(f"  Description: {description}")

        return "\n".join(diagnosis_summary)

    def summarize(self, analytics: Dict[str, Any], language: str = "ko", stream: bool = True):
        payload = {"analytics": analytics, "language": language}
        payload = self.guardrail.pre_guard(payload)
        
        # Build diagnosis text from analytics
        device_type = analytics.get("deviceType", "Unknown")
        diagnosis_text = self._build_diagnosis_text(analytics)
        
        # Build prompt using PromptBuilder
        prompt = self.prompt_builder.build_diagnosis_prompt(device_type, diagnosis_text, self.provider, language)
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


