from pydantic_settings import BaseSettings
from typing import Optional

class AgentConfig(BaseSettings):
    llm_model_name: str = 'gpt-4o'
    LANGSMITH_PROMPT_TEMPLATE_NAME: Optional[str] = None
    ENABLE_MCP_TOOLS: bool = False
