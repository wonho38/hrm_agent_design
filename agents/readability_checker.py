from __future__ import annotations

import re
from typing import Dict, List, Set, Any


class ReadabilityChecker:
    """텍스트의 가독성을 검사하는 클래스."""
    
    def __init__(self, 
                 max_word_count: int = 500,
                 max_bullet_count: int = 5,
                 max_technical_term_ratio: float = 0.01,
                 fk_score_min: int = 60,
                 fk_score_max: int = 80):
        """
        ReadabilityChecker 초기화.
        
        Args:
            max_word_count: 최대 단어 수 (기본값: 500)
            max_bullet_count: 최대 개조식 항목 수 (기본값: 5)
            max_technical_term_ratio: 최대 전문용어 비율 (기본값: 0.01 = 1%)
            fk_score_min: Flesch-Kincaid 점수 최소값 (기본값: 60)
            fk_score_max: Flesch-Kincaid 점수 최대값 (기본값: 80)
        """
        self.max_word_count = max_word_count
        self.max_bullet_count = max_bullet_count
        self.max_technical_term_ratio = max_technical_term_ratio
        self.fk_score_min = fk_score_min
        self.fk_score_max = fk_score_max
        
        # 전문 용어 사전 (확장 가능)
        self.technical_terms: Set[str] = {
            '냉매', '컴프레서', '증발기', '응축기', '제상',
            '인버터', '히트펌프', '듀얼인버터', '리니어컴프레서', '스마트인버터',
            '이온발생기', '플라즈마', 'HEPA',
            '펄세이터', '터보샷', '마그네트론', '웨이브돔', '세라믹히터', '할로겐히터', '쿼츠히터'
        }
    
    def add_technical_terms(self, terms: List[str]) -> None:
        """전문 용어 사전에 새로운 용어들을 추가합니다."""
        self.technical_terms.update(terms)
    
    def remove_technical_terms(self, terms: List[str]) -> None:
        """전문 용어 사전에서 용어들을 제거합니다."""
        self.technical_terms.difference_update(terms)
    
    def get_technical_terms(self) -> Set[str]:
        """현재 전문 용어 사전을 반환합니다."""
        return self.technical_terms.copy()
    
    def _calculate_korean_fk_score(self, text: str) -> int:
        """
        한국어 Flesch-Kincaid 점수를 계산합니다.
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            int: FK 점수 (0-100)
        """
        try:
            # URL 제거
            clean_text = re.sub(r'https?://[^\s]+', '', text)
            
            # 개조식 고려한 문장 분리
            temp_text = re.sub(r'(\d+\.)\s+', r'\1|||', clean_text)
            sentences = re.split(r'[.!?]+', temp_text)
            sentences = [s.replace('|||', ' ').strip() for s in sentences if s.strip()]
            
            if not sentences:
                return 70  # 기본값 (중간값)
                
            words = clean_text.split()
            total_words = len([w for w in words if w.strip()])
            if total_words == 0:
                return 0
            
            # 평균 문장 길이
            avg_sentence_length = total_words / len(sentences)
            
            # 음절 수 계산
            korean_chars = re.findall(r'[가-힣]', clean_text)
            english_words = len([w for w in words if re.search(r'[a-zA-Z]', w)])
            
            korean_syllables = len(korean_chars)
            english_syllables = english_words * 1.5
            total_syllables = korean_syllables + english_syllables
            
            avg_syllables_per_word = total_syllables / total_words if total_words > 0 else 0
            
            # 한국어용 FK 공식 (목표 점수 10점 하향 조정)
            fk_score = 120 - (2.5 * avg_sentence_length) - (12 * avg_syllables_per_word)
            
            # 0-100 범위로 제한
            fk_score = max(0, min(100, fk_score))
            
            return round(fk_score)
            
        except Exception as e:
            print(f"FK 점수 계산 중 오류: {str(e)}")
            return 0
    
    def _check_bullet_format(self, text: str) -> tuple[bool, int]:
        """
        개조식 형태를 검사합니다.
        
        Args:
            text: 검사할 텍스트
            
        Returns:
            tuple: (개조식 형태 여부, 개조식 항목 수)
        """
        bullet_pattern = r'\d+\.\s'
        bullet_matches = re.findall(bullet_pattern, text)
        bullet_count = len(bullet_matches)
        bullet_format = 1 <= bullet_count <= self.max_bullet_count
        return bullet_format, bullet_count
    
    def _check_word_count(self, text: str) -> tuple[bool, int]:
        """
        단어 수를 검사합니다.
        
        Args:
            text: 검사할 텍스트
            
        Returns:
            tuple: (단어 수 기준 통과 여부, 단어 수)
        """
        words = text.split()
        word_count = len(words)
        word_count_ok = word_count <= self.max_word_count
        return word_count_ok, word_count
    
    def _check_technical_terms(self, text: str, word_count: int) -> tuple[bool, List[str], float]:
        """
        전문 용어 사용률을 검사합니다.
        
        Args:
            text: 검사할 텍스트
            word_count: 총 단어 수
            
        Returns:
            tuple: (쉬운 용어 사용 여부, 발견된 전문 용어 목록, 전문 용어 비율)
        """
        found_technical_terms = []
        for term in self.technical_terms:
            if term in text:
                found_technical_terms.append(term)
        
        # 전문 용어 사용률 계산 (전체 단어 대비)
        technical_term_ratio = len(found_technical_terms) / max(word_count, 1)
        simple_terms = technical_term_ratio <= self.max_technical_term_ratio
        
        return simple_terms, found_technical_terms, technical_term_ratio
    
    def check_readability(self, text: str) -> Dict[str, Any]:
        """
        텍스트의 가독성을 종합적으로 검사합니다.
        
        Args:
            text: 검사할 텍스트
            
        Returns:
            dict: 가독성 검사 결과
                - bullet_format (bool): 개조식 여부
                - bullet_count (int): 개조식 항목 수
                - word_count (int): 단어 수
                - word_count_ok (bool): 단어수 기준 이내 여부
                - simple_terms (bool): 쉬운 용어 사용 여부
                - technical_terms_found (list): 발견된 전문 용어 목록
                - technical_term_ratio (float): 전문 용어 비율 (%)
                - fk_score (int): Flesch-Kincaid 점수
                - fk_score_ok (bool): FK 점수 기준 범위 여부
                - overall_readable (bool): 전체 가독성 통과 여부
        """
        try:
            # 1. 개조식 검사
            bullet_format, bullet_count = self._check_bullet_format(text)
            
            # 2. 단어수 검사
            word_count_ok, word_count = self._check_word_count(text)
            
            # 3. 전문 용어 검사
            simple_terms, found_technical_terms, technical_term_ratio = self._check_technical_terms(text, word_count)
            
            # 4. Flesch-Kincaid 점수 계산
            fk_score = self._calculate_korean_fk_score(text)
            fk_score_ok = self.fk_score_min <= fk_score <= self.fk_score_max
            
            # 전체 가독성 판단
            overall_readable = bullet_format and word_count_ok and simple_terms and fk_score_ok
            
            return {
                'bullet_format': bullet_format,
                'bullet_count': bullet_count,
                'word_count': word_count,
                'word_count_ok': word_count_ok,
                'simple_terms': simple_terms,
                'technical_terms_found': found_technical_terms,
                'technical_term_ratio': round(technical_term_ratio * 100, 2),
                'fk_score': fk_score,
                'fk_score_ok': fk_score_ok,
                'overall_readable': overall_readable
            }
            
        except Exception as e:
            print(f"가독성 검사 중 오류 발생: {str(e)}")
            return {
                'bullet_format': False,
                'bullet_count': 0,
                'word_count': 0,
                'word_count_ok': False,
                'simple_terms': False,
                'technical_terms_found': [],
                'technical_term_ratio': 0,
                'fk_score': 0,
                'fk_score_ok': False,
                'overall_readable': False,
                'error': str(e)
            }


# 하위 호환성을 위한 함수들 (기존 코드와의 호환성 유지)
def check_readability(text: str) -> Dict[str, Any]:
    """
    기존 함수 형태의 가독성 검사 (하위 호환성 유지).
    
    Args:
        text: 검사할 텍스트
        
    Returns:
        dict: 가독성 검사 결과
    """
    checker = ReadabilityChecker()
    return checker.check_readability(text)
