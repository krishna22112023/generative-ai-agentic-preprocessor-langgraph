from langchain_openai import ChatOpenAI

from config import settings


def get_chatgpt_model(model_name: str, **kwargs) -> ChatOpenAI:
    model = ChatOpenAI(
        model=model_name,
        temperature=kwargs.get('temperature', 0.3),
        api_key=kwargs.get('api_key', settings.OPENAI_API_KEY),
    )

    return model