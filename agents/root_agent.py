from __future__ import annotations

from typing import Any, Dict, Generator, Iterable, Optional, Protocol, Callable
import json
import os
from contextlib import nullcontext

from .diagnosis_summarizer import DiagnosisSummarizer
from .op_history_summarizer import OperationHistorySummarizer
from .guide_provider import GuideProvider
from .retriever import GuideRetriever
from .mcp import MCPRegistry


class Tool(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover - protocol
        ...


class RootAgent:
    """Root agent orchestrating sub-agents and tools via a minimal MCP-like registry.

    - Streaming: yields strings incrementally
    - Extensible: register new agents/tools at runtime
    - LangSmith: use tracing context if LANGCHAIN_TRACING_V2 is enabled
    """

    def __init__(self, provider_override: Optional[str] = None, provider_kwargs_override: Optional[Dict[str, Any]] = None) -> None:
        self.agents: Dict[str, Any] = {}
        self.tools: Dict[str, Tool] = {}
        self.mcp = MCPRegistry()

        # Load configuration
        self.config: Dict[str, Any] = self._load_config()
        self.default_language: str = self.config.get("language", "ko")
        llm_cfg: Dict[str, Any] = self.config.get("llm", {}) if isinstance(self.config.get("llm", {}), dict) else {}
        provider: str = str(provider_override or llm_cfg.get("provider", "openai"))
        provider_kwargs: Dict[str, Any] = (
            provider_kwargs_override
            if isinstance(provider_kwargs_override, dict)
            else {k: v for k, v in llm_cfg.items() if k in {"model", "api_key", "model_id", "region", "access_key", "secret_key"}}
        )

        # Configure LangSmith tracing from config if present
        self._configure_langsmith()

        # Print configured defaults for visibility
        print(f"[RootAgent] Configured language: {self.default_language}")
        print(f"[RootAgent] Configured LLM provider: {provider}")

        # Agents wired to configured provider/model
        self.register_agent(
            "diagnosis_summarizer",
            DiagnosisSummarizer(provider=provider, **provider_kwargs),
        )
        self.register_agent(
            "op_history_summarizer",
            OperationHistorySummarizer(provider=provider, **provider_kwargs),
        )
        self.register_agent(
            "guide_provider",
            GuideProvider(provider=provider, **provider_kwargs),
        )

        # Default tools
        self.register_tool("guider_retriever", GuideRetriever().stream)

    # MCP-like registry
    def register_agent(self, name: str, agent: Any) -> None:
        self.agents[name] = agent
        self.mcp.register_agent(name, agent)

    def register_tool(self, name: str, tool: Tool) -> None:
        self.tools[name] = tool
        self.mcp.register_tool(name, tool)

    def list_capabilities(self) -> Dict[str, Any]:
        return self.mcp.list()

    # Streaming runners
    def _trace_ctx(self, name: str):
        try:
            from langchain_core.tracers import context as langsmith_context  # type: ignore
            return langsmith_context(name)
        except Exception:
            return nullcontext()

    def run_diagnosis(self, analytics: Dict[str, Any], language: Optional[str] = None) -> Generator[str, None, None]:
        from .guardrails import DiagnosisGuardrail
        from .logger import log_event
        
        agent: DiagnosisSummarizer = self.agents["diagnosis_summarizer"]
        lang = language or self.default_language
        print(f"[RootAgent] run_diagnosis language={lang}")
        log_event({"stage": "run_diagnosis", "language": lang})
        
        # Initialize diagnosis guardrail
        guardrail = DiagnosisGuardrail(include_readability_report=True)
        
        # Collect all chunks from the LLM
        raw_output = ""
        with self._trace_ctx("diagnosis_summarizer"):
            for chunk in agent.summarize(analytics, language=lang, stream=True):
                raw_output += chunk
                yield chunk
        
        # Apply post-guardrail processing with readability analysis
        try:
            processed_output = guardrail.post_guard(raw_output)
            
            # If post_guard added content (readability report), yield the additional content
            if len(processed_output) > len(raw_output):
                additional_content = processed_output[len(raw_output):]
                yield additional_content
                log_event({"stage": "diagnosis_post_guard", "status": "readability_added"})
                
        except Exception as e:
            print(f"[RootAgent] Diagnosis post-guardrail processing failed: {e}")
            log_event({"stage": "diagnosis_post_guard", "status": "failed", "error": str(e)})

    def run_op_history(self, operation_history: Dict[str, Any], language: Optional[str] = None) -> Generator[str, None, None]:
        from .guardrails import OperationHistoryGuardrail, GuardrailException
        from .logger import log_event
        
        lang = language or self.default_language
        print(f"[RootAgent] run_op_history language={lang}")
        log_event({"stage": "run_op_history", "language": lang})
        
        # Apply pre-guardrail validation
        guardrail = OperationHistoryGuardrail()
        try:
            validated_data = guardrail.pre_guard(operation_history)
            log_event({"stage": "op_history_guardrail", "status": "passed"})
        except GuardrailException as e:
            error_msg = str(e)
            print(f"[RootAgent] Operation history guardrail failed: {error_msg}")
            log_event({"stage": "op_history_guardrail", "status": "failed", "error": error_msg})
            
            # Return error message instead of calling LLM
            if lang == "en":
                yield "Insufficient data available. Unable to provide operation history analysis due to lack of adequate operation history data."
            else:
                yield error_msg
            return
        
        # If validation passes, proceed with LLM processing
        agent: OperationHistorySummarizer = self.agents["op_history_summarizer"]
        
        # Collect all chunks from the LLM
        raw_output = ""
        with self._trace_ctx("op_history_summarizer"):
            for chunk in agent.summarize(validated_data, language=lang, stream=True):
                raw_output += chunk
                yield chunk
        
        # Apply post-guardrail processing with readability analysis
        try:
            processed_output = guardrail.post_guard(raw_output)
            
            # If post_guard added content (readability report), yield the additional content
            if len(processed_output) > len(raw_output):
                additional_content = processed_output[len(raw_output):]
                yield additional_content
                log_event({"stage": "op_history_post_guard", "status": "readability_added"})
                
        except Exception as e:
            print(f"[RootAgent] Post-guardrail processing failed: {e}")
            log_event({"stage": "op_history_post_guard", "status": "failed", "error": str(e)})

    def run_guide(self, diagnosis_summary: str, op_summary: str, language: Optional[str] = None) -> Generator[str, None, None]:
        agent: GuideProvider = self.agents["guide_provider"]
        lang = language or self.default_language
        from .logger import log_event
        print(f"[RootAgent] run_guide language={lang}")
        log_event({"stage": "run_guide", "language": lang})
        with self._trace_ctx("guide_provider"):
            for chunk in agent.provide(diagnosis_summary, op_summary, language=lang, stream=True):
                yield chunk

    def call_tool(self, tool_name: str, *args: Any, **kwargs: Any) -> Generator[str, None, None]:
        tool = self.tools.get(tool_name)
        if not tool:
            yield f"Unknown tool: {tool_name}\n"
            return
        for item in tool(*args, **kwargs):
            yield item

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from configure.json at project root.

        Falls back to sensible defaults if the file is missing or invalid.
        """
        try:
            # agents/.. -> project root
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            config_path = os.path.join(project_root, "configure.json")
            if not os.path.exists(config_path):
                return {"language": "ko", "llm": {"provider": "openai"}}
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return {"language": "ko", "llm": {"provider": "openai"}}
            return data
        except Exception:
            return {"language": "ko", "llm": {"provider": "openai"}}

    def _configure_langsmith(self) -> None:
        """Set LangSmith-related environment variables from config if provided."""
        try:
            ls_cfg = self.config.get("langsmith", {}) if isinstance(self.config, dict) else {}
            if not isinstance(ls_cfg, dict):
                return
            enabled = ls_cfg.get("enabled")
            if enabled is True:
                os.environ["LANGCHAIN_TRACING_V2"] = "true"
            # Only set the following if provided to avoid overwriting user env
            api_key = ls_cfg.get("api_key")
            if api_key:
                os.environ["LANGCHAIN_API_KEY"] = str(api_key)
            project = ls_cfg.get("project")
            if project:
                os.environ["LANGCHAIN_PROJECT"] = str(project)
            endpoint = ls_cfg.get("endpoint")
            if endpoint:
                os.environ["LANGCHAIN_ENDPOINT"] = str(endpoint)
        except Exception:
            # Fail-open: do not block agent init on tracing config
            pass


