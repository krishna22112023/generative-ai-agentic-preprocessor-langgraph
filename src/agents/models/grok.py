from langchain_groq import ChatGroq

from config import settings


def get_grok_model(model_name: str, **kwargs) -> ChatGroq:
    model = ChatGroq(
        model=model_name,
        temperature=kwargs.get('temperature', 0.3),
        max_retries=2,
        api_key=kwargs.get('api_key', settings.GROQ_API_KEY)
    )

    return model