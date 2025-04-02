from langchain_anthropic import ChatAnthropic

from config import settings

def get_anthropic_model(model_name: str, **kwargs) -> ChatAnthropic:
    model = ChatAnthropic(
        model=model_name,
        temperature=kwargs.get('temperature', 0.3),
        max_retries=2,
        api_key=kwargs.get('api_key', settings.ANTHROPIC_API_KEY)
    )

    return model