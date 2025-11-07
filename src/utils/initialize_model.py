from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

def initialize_model(
        model_name: str, 
        model_provider: str, 
        base_url: str, 
        temperature: float, 
        api_key: str, 
        max_tokens: int = None
    ) -> BaseChatModel:
    # Initialize the model

    if "anthropic".lower() in model_name.lower():
        model = init_chat_model(
            model=model_name,
            max_tokens=max_tokens
        )
    else:
        if max_tokens is None:
            model = init_chat_model(
                model=model_name,
                model_provider=model_provider,
                api_key=api_key,
                base_url=base_url,
                temperature=temperature
            )
        else:
            model = init_chat_model(
                model=model_name,
                model_provider=model_provider,
                api_key=api_key,
                base_url=base_url,
                temperature=temperature,
                max_tokens=max_tokens
            )

    return model