from __future__ import annotations

import json
import os
from typing import Any, Dict


class PromptBuilder:
    """Builds prompts per agent and LLM provider.

    Prompts are loaded from prompt.json configuration file.
    """

    def __init__(self, default_language: str = "ko"):
        self.default_language = default_language
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from prompt.json configuration file."""
        try:
            # Find prompt.json in project root (agents/.. -> project root)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            prompt_path = os.path.join(project_root, "prompt.json")
            
            if not os.path.exists(prompt_path):
                print(f"[PromptBuilder] Warning: prompt.json not found at {prompt_path}, using fallback prompts")
                return self._get_fallback_prompts()
            
            with open(prompt_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                print("[PromptBuilder] Warning: Invalid prompt.json format, using fallback prompts")
                return self._get_fallback_prompts()
            
            return data
        except Exception as e:
            print(f"[PromptBuilder] Error loading prompt.json: {e}, using fallback prompts")
            return self._get_fallback_prompts()

    def _get_fallback_prompts(self) -> Dict[str, Any]:
        """Fallback prompts if prompt.json is not available."""
        return {
            "diagnosis": {
                "ko": {
                    "header": "진단 데이터를 분석하여 상태를 파악하고 해결책을 제공하세요.\n\n기기 유형: {device_type}\n\n진단 정보:\n{diagnosis_text}\n\n",
                    "format": "한국어로 분석 결과를 제공하세요."
                },
                "en": {
                    "header": "Analyze diagnostic data and provide solutions.\n\nDevice Type: {device_type}\n\nDiagnostic Information:\n{diagnosis_text}\n\n",
                    "format": "Provide analysis results in English."
                }
            },
            "operation_history": {
                "ko": {"base": "운영 이력을 분석하세요.", "example": "한국어로 요약하세요."},
                "en": {"base": "Analyze operation history.", "example": "Summarize in English."}
            },
            "guide": {
                "ko": {"template": "가이드를 제공하세요.\n진단: {diagnosis_summary}\n이력: {op_summary}"},
                "en": {"template": "Provide guide.\nDiagnosis: {diagnosis_summary}\nHistory: {op_summary}"}
            }
        }

    def build_diagnosis_prompt(self, device_type: str, diagnosis_text: str, provider: str, language: str | None = None) -> str:
        """Build diagnosis prompt using configuration."""
        lang = self._normalize_language(language)
        
        try:
            prompt_config = self.prompts["diagnosis"][lang]
            header = prompt_config["header"].format(device_type=device_type, diagnosis_text=diagnosis_text)
            format_block = prompt_config["format"]
            return header + format_block
        except KeyError:
            print(f"[PromptBuilder] Warning: No prompt found for diagnosis/{lang}, using fallback")
            return f"Analyze the diagnostic data for {device_type}:\n{diagnosis_text}\nProvide analysis in {lang}."

    def build_operation_history_prompt(self, op_history: Dict[str, Any], provider: str, language: str | None = None) -> str:
        """Build operation history prompt using configuration."""
        lang = self._normalize_language(language)
        
        try:
            prompt_config = self.prompts["operation_history"][lang]
            base = prompt_config["base"]
            example = prompt_config["example"]
            
            return (
                f"{base}{example}\n---\n\n"
                f"Now, based on the given operation history JSON, produce the summary according to the above format.\n\n"
                f"Operation history JSON:\n{op_history}"
            )
        except KeyError:
            print(f"[PromptBuilder] Warning: No prompt found for operation_history/{lang}, using fallback")
            return f"Analyze the operation history data and provide summary in {lang}:\n{op_history}"

    def build_guide_prompt(self, diagnosis_summary: str, op_summary: str, provider: str, language: str | None = None) -> str:
        """Build guide prompt using configuration."""
        lang = self._normalize_language(language)
        
        try:
            prompt_config = self.prompts["guide"][lang]
            template = prompt_config["template"]
            
            return template.format(
                language=lang,
                diagnosis_summary=diagnosis_summary,
                op_summary=op_summary
            )
        except KeyError:
            print(f"[PromptBuilder] Warning: No prompt found for guide/{lang}, using fallback")
            return (
                f"Provide actionable guide in {lang}.\n"
                f"Diagnosis: {diagnosis_summary}\n"
                f"Operation History: {op_summary}\n"
                f"Return numbered steps and safety cautions."
            )

    def build_actions_guide_prompt(self, diagnosis_summary: str, reference_summaries: str, language: str | None = None) -> str:
        """Build KO-only customer actions guide prompt using reference docs."""
        lang = self._normalize_language(language)
        if lang != "ko":
            # Fallback: still return in ko format to enforce ko output
            lang = "ko"
        try:
            prompt_config = self.prompts["guide"]["ko_actions"]
            template = prompt_config["template"]
            return template.format(
                diagnosis_summary=diagnosis_summary,
                reference_summaries=reference_summaries,
            )
        except KeyError:
            print("[PromptBuilder] Warning: No prompt found for guide/ko_actions, using fallback")
            return (
                "아래 진단 요약과 참고 문서 3개를 바탕으로 고객이 수행할 수 있는 조치 5개 이내를 한국어로 번호 목록으로 제시하세요.\n"
                "진단 요약:\n" + diagnosis_summary + "\n\n"
                "참고 문서 요약:\n" + reference_summaries + "\n"
                "각 항목은 1~2문장으로 구체적으로 작성하고, 필요한 경우 항목 끝에 '출처: http://...'을 1개만 표기하세요."
            )

    def _normalize_language(self, language: str | None) -> str:
        """Normalize language code to supported format."""
        lang = (language or self.default_language).lower()
        if lang in ("en", "english"):
            return "en"
        else:
            return "ko"


