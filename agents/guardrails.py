from __future__ import annotations

from typing import Any, Dict, Optional
from .readability_checker import ReadabilityChecker


class GuardrailException(Exception):
    """Exception raised when guardrail validation fails."""
    pass


class Guardrail:
    """Base guardrail class with validation methods."""

    def pre_guard(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-process and validate input before prompt creation."""
        return payload

    def post_guard(self, raw_output: str) -> str:
        """Validate and possibly redact model output."""
        return raw_output


class OperationHistoryGuardrail(Guardrail):
    """Guardrail specifically for operation history data validation."""

    def __init__(self, include_readability_report: bool = True):
        """
        Initialize OperationHistoryGuardrail.
        
        Args:
            include_readability_report: Whether to include readability analysis in post_guard
        """
        self.include_readability_report = include_readability_report
        self.readability_checker = ReadabilityChecker()

    def pre_guard(self, operation_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate operation history data before LLM processing.
        
        Args:
            operation_history: Dictionary containing operation history data
            
        Returns:
            Dict[str, Any]: Validated operation history data
            
        Raises:
            GuardrailException: If operation history data is insufficient
        """
        # Check if operation_history exists and has operationHistory key
        if not operation_history:
            raise GuardrailException("운영 이력 데이터가 없습니다. 분석을 위한 충분한 데이터가 제공되지 않았습니다.")
        
        # Check for operationHistory key specifically
        operation_data = operation_history.get("operationHistory")
        
        if operation_data is None:
            raise GuardrailException("운영 이력 데이터(operationHistory)가 없습니다. 분석을 위한 충분한 데이터가 제공되지 않았습니다.")
        
        # Check if operationHistory is empty (empty list, dict, or string)
        if not operation_data:
            raise GuardrailException("운영 이력 데이터가 비어있습니다. 분석을 위한 충분한 데이터가 제공되지 않았습니다.")
        
        # Additional checks for different data types
        if isinstance(operation_data, (list, dict)):
            if len(operation_data) == 0:
                raise GuardrailException("운영 이력 데이터가 비어있습니다. 분석을 위한 충분한 데이터가 제공되지 않았습니다.")
        elif isinstance(operation_data, str):
            if not operation_data.strip():
                raise GuardrailException("운영 이력 데이터가 비어있습니다. 분석을 위한 충분한 데이터가 제공되지 않았습니다.")
        
        return operation_history

    def post_guard(self, raw_output: str) -> str:
        """
        Post-process operation history summary output with readability analysis.
        
        Args:
            raw_output: Raw LLM output text
            
        Returns:
            str: Processed output with optional readability report
        """
        if not self.include_readability_report:
            return raw_output
        
        try:
            # Perform readability check
            readability_result = self.readability_checker.check_readability(raw_output)
            
            # Generate readability report
            readability_report = self._generate_readability_report(readability_result)
            
            # Append readability report to the original output
            enhanced_output = f"{raw_output}\n\n{readability_report}"
            
            return enhanced_output
            
        except Exception as e:
            print(f"[OperationHistoryGuardrail] 가독성 검사 중 오류 발생: {e}")
            # Return original output if readability check fails
            return raw_output

    def _generate_readability_report(self, readability_result: Dict[str, Any]) -> str:
        """
        Generate a formatted readability report.
        
        Args:
            readability_result: Result from ReadabilityChecker
            
        Returns:
            str: Formatted readability report
        """
        # Extract key metrics
        overall_readable = readability_result.get('overall_readable', False)
        bullet_format = readability_result.get('bullet_format', False)
        bullet_count = readability_result.get('bullet_count', 0)
        word_count = readability_result.get('word_count', 0)
        word_count_ok = readability_result.get('word_count_ok', False)
        simple_terms = readability_result.get('simple_terms', False)
        technical_terms_found = readability_result.get('technical_terms_found', [])
        technical_term_ratio = readability_result.get('technical_term_ratio', 0)
        fk_score = readability_result.get('fk_score', 0)
        fk_score_ok = readability_result.get('fk_score_ok', False)
        
        # Generate status indicators
        def get_status_icon(condition: bool) -> str:
            return "✅" if condition else "❌"
        
        def get_status_text(condition: bool) -> str:
            return "양호" if condition else "개선 필요"
        
        # Build the report
        report_lines = [
            "📊 **가독성 분석 결과**",
            "=" * 40,
            f"🎯 **종합 평가**: {get_status_icon(overall_readable)} {get_status_text(overall_readable)}",
            "",
            "📋 **세부 분석**:",
            f"• 개조식 형태: {get_status_icon(bullet_format)} {bullet_count}개 항목 ({get_status_text(bullet_format)})",
            f"• 단어 수: {get_status_icon(word_count_ok)} {word_count}개 단어 ({get_status_text(word_count_ok)})",
            f"• 용어 난이도: {get_status_icon(simple_terms)} 전문용어 {technical_term_ratio}% ({get_status_text(simple_terms)})",
            f"• 가독성 점수: {get_status_icon(fk_score_ok)} FK {fk_score}점 ({get_status_text(fk_score_ok)})",
        ]
        
        # Add technical terms if found
        if technical_terms_found:
            report_lines.extend([
                "",
                f"🔍 **발견된 전문용어**: {', '.join(technical_terms_found)}"
            ])
        
        # Add recommendations if needed
        recommendations = []
        if not bullet_format:
            if bullet_count == 0:
                recommendations.append("• 내용을 1-5개의 개조식 항목으로 구성해 주세요")
            elif bullet_count > 5:
                recommendations.append(f"• 개조식 항목을 5개 이하로 줄여주세요 (현재 {bullet_count}개)")
        
        if not word_count_ok:
            recommendations.append(f"• 단어 수를 500개 이하로 줄여주세요 (현재 {word_count}개)")
        
        if not simple_terms and technical_terms_found:
            recommendations.append("• 전문용어를 일반인이 이해하기 쉬운 용어로 바꿔주세요")
        
        if not fk_score_ok:
            if fk_score < 60:
                recommendations.append("• 문장을 더 간단하고 명확하게 작성해 주세요")
            elif fk_score > 80:
                recommendations.append("• 문장을 조금 더 자세하게 설명해 주세요")
        
        if recommendations:
            report_lines.extend([
                "",
                "💡 **개선 권장사항**:",
                *recommendations
            ])
        
        return "\n".join(report_lines)

    def set_readability_enabled(self, enabled: bool) -> None:
        """Enable or disable readability reporting."""
        self.include_readability_report = enabled

    def configure_readability_checker(self, **kwargs) -> None:
        """
        Configure the readability checker with custom parameters.
        
        Args:
            **kwargs: Parameters for ReadabilityChecker constructor
        """
        self.readability_checker = ReadabilityChecker(**kwargs)


class DiagnosisGuardrail(Guardrail):
    """Guardrail specifically for diagnosis data validation and readability checking."""

    def __init__(self, include_readability_report: bool = True):
        """
        Initialize DiagnosisGuardrail.
        
        Args:
            include_readability_report: Whether to include readability analysis in post_guard
        """
        self.include_readability_report = include_readability_report
        self.readability_checker = ReadabilityChecker()

    def pre_guard(self, diagnosis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pre-process diagnosis data (currently no validation needed).
        
        Args:
            diagnosis_data: Dictionary containing diagnosis data
            
        Returns:
            Dict[str, Any]: Validated diagnosis data
        """
        return diagnosis_data

    def post_guard(self, raw_output: str) -> str:
        """
        Post-process diagnosis summary output with readability analysis.
        
        Args:
            raw_output: Raw LLM output text
            
        Returns:
            str: Processed output with optional readability report
        """
        if not self.include_readability_report:
            return raw_output
        
        try:
            # Perform readability check
            readability_result = self.readability_checker.check_readability(raw_output)
            
            # Generate readability report
            readability_report = self._generate_readability_report(readability_result)
            
            # Append readability report to the original output
            enhanced_output = f"{raw_output}\n\n{readability_report}"
            
            return enhanced_output
            
        except Exception as e:
            print(f"[DiagnosisGuardrail] 가독성 검사 중 오류 발생: {e}")
            # Return original output if readability check fails
            return raw_output

    def _generate_readability_report(self, readability_result: Dict[str, Any]) -> str:
        """
        Generate a formatted readability report.
        
        Args:
            readability_result: Result from ReadabilityChecker
            
        Returns:
            str: Formatted readability report
        """
        # Extract key metrics
        overall_readable = readability_result.get('overall_readable', False)
        bullet_format = readability_result.get('bullet_format', False)
        bullet_count = readability_result.get('bullet_count', 0)
        word_count = readability_result.get('word_count', 0)
        word_count_ok = readability_result.get('word_count_ok', False)
        simple_terms = readability_result.get('simple_terms', False)
        technical_terms_found = readability_result.get('technical_terms_found', [])
        technical_term_ratio = readability_result.get('technical_term_ratio', 0)
        fk_score = readability_result.get('fk_score', 0)
        fk_score_ok = readability_result.get('fk_score_ok', False)
        
        # Generate status indicators
        def get_status_icon(condition: bool) -> str:
            return "✅" if condition else "❌"
        
        def get_status_text(condition: bool) -> str:
            return "양호" if condition else "개선 필요"
        
        # Build the report
        report_lines = [
            "📊 **가독성 분석 결과**",
            "=" * 40,
            f"🎯 **종합 평가**: {get_status_icon(overall_readable)} {get_status_text(overall_readable)}",
            "",
            "📋 **세부 분석**:",
            f"• 개조식 형태: {get_status_icon(bullet_format)} {bullet_count}개 항목 ({get_status_text(bullet_format)})",
            f"• 단어 수: {get_status_icon(word_count_ok)} {word_count}개 단어 ({get_status_text(word_count_ok)})",
            f"• 용어 난이도: {get_status_icon(simple_terms)} 전문용어 {technical_term_ratio}% ({get_status_text(simple_terms)})",
            f"• 가독성 점수: {get_status_icon(fk_score_ok)} FK {fk_score}점 ({get_status_text(fk_score_ok)})",
        ]
        
        # Add technical terms if found
        if technical_terms_found:
            report_lines.extend([
                "",
                f"🔍 **발견된 전문용어**: {', '.join(technical_terms_found)}"
            ])
        
        # Add recommendations if needed
        recommendations = []
        if not bullet_format:
            if bullet_count == 0:
                recommendations.append("• 내용을 1-5개의 개조식 항목으로 구성해 주세요")
            elif bullet_count > 5:
                recommendations.append(f"• 개조식 항목을 5개 이하로 줄여주세요 (현재 {bullet_count}개)")
        
        if not word_count_ok:
            recommendations.append(f"• 단어 수를 500개 이하로 줄여주세요 (현재 {word_count}개)")
        
        if not simple_terms and technical_terms_found:
            recommendations.append("• 전문용어를 일반인이 이해하기 쉬운 용어로 바꿔주세요")
        
        if not fk_score_ok:
            if fk_score < 60:
                recommendations.append("• 문장을 더 간단하고 명확하게 작성해 주세요")
            elif fk_score > 80:
                recommendations.append("• 문장을 조금 더 자세하게 설명해 주세요")
        
        if recommendations:
            report_lines.extend([
                "",
                "💡 **개선 권장사항**:",
                *recommendations
            ])
        
        return "\n".join(report_lines)

    def set_readability_enabled(self, enabled: bool) -> None:
        """Enable or disable readability reporting."""
        self.include_readability_report = enabled

    def configure_readability_checker(self, **kwargs) -> None:
        """
        Configure the readability checker with custom parameters.
        
        Args:
            **kwargs: Parameters for ReadabilityChecker constructor
        """
        self.readability_checker = ReadabilityChecker(**kwargs)


