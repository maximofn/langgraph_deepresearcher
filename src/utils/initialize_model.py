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
    """
    Initialize a chat model based on the provider.
    
    Args:
        model_name: Name of the model to use
        model_provider: Provider of the model (openai, anthropic, google_genai, etc.)
        base_url: Base URL for the API
        temperature: Temperature for model sampling
        api_key: API key for authentication
        max_tokens: Maximum tokens for response (optional)
    
    Returns:
        BaseChatModel: Initialized chat model
    """
    
    # Anthropic models (Claude)
    if "anthropic" in model_name.lower():
        model = init_chat_model(
            model=model_name,
            model_provider="anthropic",
            max_tokens=max_tokens,
            temperature=temperature,
            api_key=api_key
        )
    
    # Google Gemini models (using Google Generative AI, not Vertex AI)
    elif "gemini" in model_name.lower():
        model = init_chat_model(
            model=model_name,
            model_provider="google_genai",
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key
        )
    
    # Other providers (OpenAI, GitHub, Cerebras, etc.)
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