from pathlib import Path
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder, SystemMessagePromptTemplate
)
from langchain import hub

from src.services.mcp.create_client import get_client
from config import settings, agent_config
from src.agents.models import get_chat_model
from src.services.tool.minIO import minio_tools
from src.services.tool.IQA import iqa_tools

class DataProcessorChain:
    @classmethod
    def get_generator_chain(cls):
        llm = get_chat_model(model_name=agent_config.llm_model_name)
        tools = minio_tools + iqa_tools
        llm = llm.bind_tools(tools)
        fp_prompt = Path(settings.BASE, 'src', 'agents', 'data_processor', 'prompts', f'processor_agent.md')
        f = open(fp_prompt, 'r', encoding='utf-8')
        system_template = SystemMessagePromptTemplate.from_template(f.read())
        # system_template = hub.pull(agent_config.LANGSMITH_PROMPT_TEMPLATE_NAME)

        messages = MessagesPlaceholder(variable_name='messages')

        prompt = ChatPromptTemplate.from_messages([system_template, messages])

        chain = prompt | llm 

        return chain
    @classmethod
    async def get_generator_chain_mcp(cls):

        mcp_tools = await get_client()
        llm = get_chat_model(model_name=agent_config.llm_model_name)
        llm = llm.bind_tools(mcp_tools)

        fp_prompt = Path(settings.BASE, 'src', 'agents', 'data_processor', 'prompts', f'processor_agent.md')
        f = open(fp_prompt, 'r', encoding='utf-8')
        system_template = SystemMessagePromptTemplate.from_template(f.read())
        # system_template = hub.pull(agent_config.LANGSMITH_PROMPT_TEMPLATE_NAME)

        messages = MessagesPlaceholder(variable_name='messages')

        prompt = ChatPromptTemplate.from_messages([system_template, messages])

        chain = prompt | llm 

        return chain