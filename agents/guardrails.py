from __future__ import annotations

from typing import Any, Dict


class Guardrail:
    """Dummy guardrail class with function declarations only."""

    def pre_guard(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-process and validate input before prompt creation."""
        return payload

    def post_guard(self, raw_output: str) -> str:
        """Validate and possibly redact model output."""
        return raw_output


