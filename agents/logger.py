from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any, Dict


def _log_path() -> str:
    # agents/.. -> project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    return os.path.join(project_root, "hrm_agent_log.json")


def log_event(event: Dict[str, Any]) -> None:
    try:
        payload = {
            "id": str(uuid.uuid4()),
            "ts": time.time(),
            **event,
        }
        path = _log_path()
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # Do not crash on logging failures
        pass


