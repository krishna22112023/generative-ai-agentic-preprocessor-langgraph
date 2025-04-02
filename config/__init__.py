from config.log_config import logging
from config.settings import Settings
from config.agent_config import AgentConfig

settings = Settings()
agent_config = AgentConfig()

logger = logging.getLogger(settings.APP_NAME)