from __future__ import annotations

from typing import Any, Callable, Dict, Protocol


class MCPTool(Protocol):
    def __call__(self, *args: Any, **kwargs: Any):  # pragma: no cover - protocol
        ...


class MCPRegistry:
    """Minimal MCP-like registry for agents and tools.

    This is a placeholder to demonstrate how the root agent could integrate an
    MCP server. In real usage, map these registries to actual MCP transport and
    tool/agent invocation protocols.
    """

    def __init__(self) -> None:
        self.agents: Dict[str, Any] = {}
        self.tools: Dict[str, MCPTool] = {}

    def register_agent(self, name: str, agent: Any) -> None:
        self.agents[name] = agent

    def register_tool(self, name: str, tool: MCPTool) -> None:
        self.tools[name] = tool

    def list(self) -> Dict[str, Any]:
        return {"agents": list(self.agents.keys()), "tools": list(self.tools.keys())}


