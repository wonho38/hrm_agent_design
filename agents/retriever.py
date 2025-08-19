from __future__ import annotations

import requests
from typing import Dict, Generator, Iterable, List, Optional


class GuideRetriever:
    """Retriever for action guides that calls external search API.

    Calls http://localhost:5001/search API with category filtering support.
    """

    def __init__(self, api_base_url: str = "http://localhost:5001"):
        self.api_base_url = api_base_url

    def retrieve(self, query: str, top_k: int = 3, category_filter: Optional[str] = None) -> List[str]:
        """Retrieve guides from external API."""
        try:
            payload = {
                "query": query,
                "top_k": top_k,
                "parallel": True
            }
            if category_filter:
                payload["category_filter"] = category_filter

            response = requests.post(f"{self.api_base_url}/search", json=payload, timeout=30)
            
            if response.ok:
                data = response.json()
                results = data.get("results", [])
                
                formatted_results = []
                for idx, item in enumerate(results[:top_k], start=1):
                    title = item.get("title", "")
                    content = item.get("content", "")
                    url = item.get("url", "")
                    
                    # Format similar to the expected format
                    snippet = content[:400] if content else ""
                    formatted_result = f"[{idx}] 제목: {title}\n요약: {snippet}"
                    if url:
                        formatted_result += f"\nURL: {url}"
                    
                    formatted_results.append(formatted_result)
                
                return formatted_results
            else:
                print(f"[GuideRetriever] API 요청 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[GuideRetriever] API 호출 중 오류: {e}")
            return []

    def stream(self, query: str, top_k: int = 3, category_filter: Optional[str] = None) -> Generator[str, None, None]:
        """Stream guides from external API."""
        results = self.retrieve(query, top_k=top_k, category_filter=category_filter)
        for result in results:
            yield result + "\n\n"


