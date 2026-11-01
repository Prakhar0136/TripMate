import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

load_dotenv()

class AppConfig(BaseModel):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    def validate_keys(self):
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables.")

config = AppConfig()

def get_llm(model_name: str = "gemini-2.5-flash") -> ChatGoogleGenerativeAI:
    """
    Initializes and returns the primary LLM engine.
    Gemini 2.5 Flash provides native multimodal processing with a generous free tier.
    """
    config.validate_keys()
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=config.gemini_api_key,
        temperature=0.2,
        max_retries=2
    )