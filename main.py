from __future__ import annotations

import json
from typing import Any, Dict

from agents.root_agent import RootAgent


def stream_print(gen):
    for chunk in gen:
        print(chunk, end="")


def demo():
    root = RootAgent()
    print("Capabilities:", root.list_capabilities())

    # Load first item with id == airconditioner_001
    with open("data/sample_original.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    target = next((it for it in data if it.get("id") == "airconditioner_001"), data[0])

    analytics: Dict[str, Any] = target.get("analytics", {})
    op_history: Dict[str, Any] = target.get("operation_history", {})

    # Use configured language from RootAgent by omitting explicit language
    print(f"\n--- Diagnosis ({root.default_language}): airconditioner_001 ---")
    stream_print(root.run_diagnosis(analytics))

    print(f"\n\n--- Operation History ({root.default_language}): airconditioner_001 ---")
    stream_print(root.run_op_history(op_history))


if __name__ == "__main__":
    demo()


