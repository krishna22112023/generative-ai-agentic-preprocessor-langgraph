from src.agents.models.openai import get_chatgpt_model
from src.agents.models.anthropic import get_anthropic_model
from src.agents.models.grok import get_grok_model


def get_chat_model(model_name: str, **kwargs):
    if 'gpt' in model_name:
        return get_chatgpt_model(model_name, **kwargs)
    elif 'claude' in model_name:
        return get_anthropic_model(model_name, **kwargs)
    elif 'grok' in model_name:
        return get_grok_model(model_name, **kwargs)
    else:
        raise ValueError(f"Model {model_name} not supported.")