from __future__ import annotations

import requests
from typing import Dict, Generator, Iterable, List, Optional
from .mcp import ToolMetadata


class GuideRetriever:
    """Retriever for action guides that calls external search API.

    Calls external search API with category filtering support.
    API URL can be configured via constructor parameter.
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

    @classmethod
    def get_mcp_metadata(cls) -> ToolMetadata:
        """Get MCP metadata for the GuideRetriever tool."""
        return ToolMetadata(
            name="document_retriever",
            description="Retrieve relevant documents and guides from external knowledge base using semantic search",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for finding relevant documents"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of top results to return (default: 3)",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 3
                    },
                    "category_filter": {
                        "type": "string",
                        "description": "Optional category filter to narrow search results",
                        "enum": ["troubleshooting", "maintenance", "configuration", "user_guide"]
                    }
                },
                "required": ["query"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "Formatted document snippet with title, summary, and URL"
                        }
                    },
                    "total_found": {
                        "type": "integer",
                        "description": "Total number of documents found"
                    }
                }
            }
        )

    def as_mcp_tool(self) -> callable:
        """Return a MCP-compatible tool function."""
        def mcp_retrieve(query: str, top_k: int = 3, category_filter: Optional[str] = None) -> Dict[str, any]:
            """MCP tool wrapper for document retrieval."""
            try:
                results = self.retrieve(query, top_k, category_filter)
                return {
                    "results": results,
                    "total_found": len(results),
                    "query": query,
                    "top_k": top_k,
                    "category_filter": category_filter
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "results": [],
                    "total_found": 0
                }
        
        return mcp_retrieve


