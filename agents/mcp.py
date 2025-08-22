from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Protocol
import json
from dataclasses import dataclass


class MCPTool(Protocol):
    def __call__(self, *args: Any, **kwargs: Any):  # pragma: no cover - protocol
        ...


@dataclass
class ToolMetadata:
    """Metadata for MCP tools following MCP specification."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None


@dataclass
class AgentMetadata:
    """Metadata for MCP agents."""
    name: str
    description: str
    capabilities: List[str]


class MCPRegistry:
    """Enhanced MCP-like registry for agents and tools.

    This registry follows MCP (Model Context Protocol) patterns and provides
    proper metadata management, error handling, and tool discovery capabilities.
    """

    def __init__(self) -> None:
        self.agents: Dict[str, Any] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        self.agent_metadata: Dict[str, AgentMetadata] = {}

    def register_agent(self, name: str, agent: Any, metadata: Optional[AgentMetadata] = None) -> None:
        """Register an agent with optional metadata."""
        self.agents[name] = agent
        if metadata:
            self.agent_metadata[name] = metadata

    def register_tool(self, name: str, tool: MCPTool, metadata: Optional[ToolMetadata] = None) -> None:
        """Register a tool with optional metadata."""
        self.tools[name] = tool
        if metadata:
            self.tool_metadata[name] = metadata

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a registered tool by name."""
        return self.tools.get(name)

    def get_agent(self, name: str) -> Optional[Any]:
        """Get a registered agent by name."""
        return self.agents.get(name)

    def get_tool_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Get metadata for a specific tool."""
        return self.tool_metadata.get(name)

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all tools with their metadata in MCP format."""
        tools = {}
        for name, tool in self.tools.items():
            metadata = self.tool_metadata.get(name)
            tools[name] = {
                "name": name,
                "description": metadata.description if metadata else "No description available",
                "inputSchema": metadata.input_schema if metadata else {},
                "outputSchema": metadata.output_schema if metadata else None
            }
        return tools

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all agents with their metadata."""
        agents = {}
        for name, agent in self.agents.items():
            metadata = self.agent_metadata.get(name)
            agents[name] = {
                "name": name,
                "description": metadata.description if metadata else "No description available",
                "capabilities": metadata.capabilities if metadata else []
            }
        return agents

    def list(self) -> Dict[str, Any]:
        """List all registered components."""
        return {
            "agents": self.list_agents(),
            "tools": self.list_tools()
        }

    def invoke_tool(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Safely invoke a tool with error handling."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        try:
            return tool(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Error invoking tool '{name}': {str(e)}")

    def to_mcp_manifest(self) -> str:
        """Export registry as MCP-compatible JSON manifest."""
        manifest = {
            "version": "1.0.0",
            "name": "HRM Agent MCP Server",
            "description": "MCP server for HRM agent tools and capabilities",
            "tools": self.list_tools(),
            "agents": self.list_agents()
        }
        return json.dumps(manifest, indent=2, ensure_ascii=False)


