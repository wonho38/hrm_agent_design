from __future__ import annotations

from typing import Any, Dict, List


class PromptBuilder:
    """Builds prompts per agent and LLM provider.

    Prompts are simple strings; agents can extend or override if needed.
    """

    def __init__(self, default_language: str = "ko"):
        self.default_language = default_language

    def build_diagnosis_prompt(self, analytics: Dict[str, Any], provider: str, language: str | None = None) -> str:
        """Match the reference prompt from analytics_amazon.py, but output ONLY the specified language."""
        lang = (language or self.default_language).lower()
        device_type = analytics.get("deviceType", "Unknown")
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

        diagnosis_text = "\n".join(diagnosis_summary)

        header = (
            "You are an expert appliance technician analyzing diagnostic data to help customers understand their appliance status and provide actionable solutions.\n\n"
            f"Device Type: {device_type}\n\n"
            f"Diagnostic Information:\n{diagnosis_text}\n\n"
            "IMPORTANT GUIDELINES:\n"
            "- Focus on providing helpful, customer-oriented diagnostic results\n"
            "- DO NOT mention data insufficiency, lack of data, or insufficient history\n"
            "- If diagnostic results show \"Explain\" or \"Lack\", interpret them as potential maintenance needs or normal operation guidance\n"
            "- Provide practical, actionable advice that customers can understand and follow\n"
            "- Focus on preventive care and maintenance recommendations when appropriate\n"
            "- Be concise and direct - provide only the most relevant information\n"
            "- Each section should have 1-3 bullet points maximum, with single points preferred when sufficient\n\n"
            "Based on this diagnostic information, classify the device status and provide detailed analysis.\n\n"
        )

        if lang in ("en", "english"):
            format_block = (
                "Provide your analysis in ENGLISH in the following EXACT format:\n\n"
                "Conclusion: [MUST be exactly one of: \"normal\" OR \"needs repair\" OR \"self-repairable\"]\n"
                "1. Problem Detection:\n"
                "  - [1-2 bullet points, each maximum 2 lines]\n"
                "2. Cause:\n"
                "  - [1-2 bullet points, each maximum 2 lines]\n"
                "3. Remote Resolution Possibility:\n"
                "  - [1-2 bullet points, each maximum 2 lines]\n"
                "4. Solution:\n"
                "  - [1-2 bullet points, each maximum 2 lines]\n"
                "5. Potential Damage:\n"
                "  - [1-2 bullet points, each maximum 2 lines]\n\n"
                "Reference diagnostic codes explicitly when helpful."
            )
        else:
            format_block = (
                "한국어로 아래 형식을 정확히 따라 작성하세요:\n\n"
                "결론: [반드시 다음 중 하나: \"정상\" 또는 \"수리 필요\" 또는 \"자가 조치 가능\"]\n"
                "1. 문제 감지:\n"
                "  - [1-2개 항목]\n"
                "2. 원인:\n"
                "  - [1-2개 항목]\n"
                "3. 원격 해결 가능 여부:\n"
                "  - [1-2개 항목]\n"
                "4. 해결 방안:\n"
                "  - [1-2개 항목]\n"
                "5. 미해결시 잠재적 피해:\n"
                "  - [1-2개 항목]\n\n"
                "진단 코드는 필요 시 명시적으로 참조하세요."
            )

        return header + format_block

    def build_operation_history_prompt(self, op_history: Dict[str, Any], provider: str, language: str | None = None) -> str:
        """Match the PROMPT from operation_history_amazon.py, but output ONLY the specified language."""
        lang = (language or self.default_language).lower()
        base = (
            "You are given operation history data for a home appliance such as an air conditioner, refrigerator, or washing machine.  \n"
            "Analyze the data and produce a concise summary in numbered bullet points (1–5).  \n"
            "Follow these rules:\n\n"
            "1. The **Conclusion** must always be point 1.  \n"
            "   - Possible values: \"Normal operation\", \"Detected abnormal operation\", \"Insufficient data\".  \n"
            "   - In Korean: \"정상 동작\", \"동작 이상 감지\", \"데이터 부족\".\n\n"
            "2. After point 1, summarize the most important operational insights in 2–4 additional points.  \n"
            "   - Include temperature trends, cycle performance, error events, or missing data.  \n"
            "   - Mention specific measurements when relevant.  \n"
            "   - Avoid unnecessary technical details.\n\n"
        )

        if lang in ("en", "english"):
            example = (
                "Output language: English only.\n\n"
                "Format exactly like this example:\n\n"
                "English  \n"
                "1. **Conclusion:** Normal operation.  \n"
                "2. [Key observation #1]  \n"
                "3. [Key observation #2]  \n"
                "4. [Key observation #3]  \n"
                "5. [Key observation #4]  \n"
            )
        else:
            example = (
                "출력 언어: 한국어만 사용하세요.\n\n"
                "다음 예시 형식을 정확히 따르세요:\n\n"
                "한국어  \n"
                "1. **결론:** 정상 동작.  \n"
                "2. [핵심 관찰 #1]  \n"
                "3. [핵심 관찰 #2]  \n"
                "4. [핵심 관찰 #3]  \n"
                "5. [핵심 관찰 #4]  \n"
            )

        return (
            f"{base}{example}\n---\n\n"
            f"Now, based on the given operation history JSON, produce the summary according to the above format.\n\n"
            f"Operation history JSON:\n{op_history}"
        )

    def build_guide_prompt(self, diagnosis_summary: str, op_summary: str, provider: str, language: str | None = None) -> str:
        lang = (language or self.default_language).lower()
        return (
            "You are a guide provider generating actionable steps based on diagnosis and usage summaries.\n"
            f"Language: {lang}. If 'both', output English then Korean.\n\n"
            f"Diagnosis summary:\n{diagnosis_summary}\n\nOperation history summary:\n{op_summary}\n\n"
            "Return concise, numbered steps and safety cautions when relevant."
        )


