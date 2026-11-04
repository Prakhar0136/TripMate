import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

load_dotenv()

class AppConfig(BaseModel):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    def validate_keys(self):
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables.")

config = AppConfig()

def get_llm(model_name: str | None = None) -> ChatGoogleGenerativeAI:
    """
    Initializes and returns the primary LLM engine.
    Uses GEMINI_MODEL env var or gemini-flash-lite-latest by default.
    """
    config.validate_keys()
    selected_model = model_name or config.gemini_model
    
    return ChatGoogleGenerativeAI(
        model=selected_model,
        google_api_key=config.gemini_api_key,
        temperature=0.2,
        max_retries=5
    )
