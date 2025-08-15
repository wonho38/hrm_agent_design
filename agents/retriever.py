from __future__ import annotations

from typing import Dict, Generator, Iterable, List, Optional


class GuideRetriever:
    """A simple in-memory retriever for action guides by code or keyword.

    In a real system this would connect to a vector DB or search index.
    """

    def __init__(self):
        self._guides: Dict[str, str] = {
            "E101": "Check the inlet filter and ensure water supply valve is fully open.",
            "Cooling_Inefficiency": "Clean condenser coils and ensure 10cm clearance for ventilation.",
        }

    def add_guide(self, key: str, content: str) -> None:
        self._guides[key] = content

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        hits: List[str] = []
        for k, v in self._guides.items():
            if query.lower() in k.lower() or query.lower() in v.lower():
                hits.append(f"[{k}] {v}")
        return hits[:top_k]

    def stream(self, query: str, top_k: int = 3) -> Generator[str, None, None]:
        for hit in self.retrieve(query, top_k=top_k):
            yield hit + "\n"


