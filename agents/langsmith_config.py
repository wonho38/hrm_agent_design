"""LangSmith configuration for tracing LLM calls."""

import os
from typing import Optional


def setup_langsmith() -> bool:
    """
    Setup LangSmith tracing if API key is available.
    
    Returns:
        bool: True if LangSmith is configured, False otherwise
    """
    langsmith_api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
    
    if langsmith_api_key:
        # Set required environment variables for LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        
        # Optional: Set project name
        project_name = os.getenv("LANGCHAIN_PROJECT", "hrm-agent-llm-calls")
        os.environ["LANGCHAIN_PROJECT"] = project_name
        
        # Optional: Set endpoint if using custom LangSmith instance
        langsmith_endpoint = os.getenv("LANGCHAIN_ENDPOINT")
        if langsmith_endpoint:
            os.environ["LANGCHAIN_ENDPOINT"] = langsmith_endpoint
            
        print(f"✅ LangSmith tracing enabled for project: {project_name}")
        return True
    else:
        print("⚠️ LangSmith API key not found. Tracing disabled.")
        print("   Set LANGCHAIN_API_KEY or LANGSMITH_API_KEY environment variable to enable tracing.")
        return False


def get_langsmith_project_name() -> str:
    """Get the current LangSmith project name."""
    return os.getenv("LANGCHAIN_PROJECT", "hrm-agent-llm-calls")


def is_langsmith_enabled() -> bool:
    """Check if LangSmith tracing is enabled."""
    return os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"


def create_run_name(llm_type: str, operation: str = "generate") -> str:
    """
    Create a descriptive run name for LangSmith tracing.
    
    Args:
        llm_type: Type of LLM (openai, bedrock, gauss, gausso)
        operation: Operation being performed (generate, stream)
        
    Returns:
        str: Formatted run name
    """
    return f"hrm-{llm_type}-{operation}"


def get_langsmith_tags(llm_type: str, stream: bool = False) -> list[str]:
    """
    Get tags for LangSmith runs.
    
    Args:
        llm_type: Type of LLM
        stream: Whether this is a streaming operation
        
    Returns:
        list: Tags for the run
    """
    tags = ["hrm-agent", llm_type]
    if stream:
        tags.append("streaming")
    return tags
