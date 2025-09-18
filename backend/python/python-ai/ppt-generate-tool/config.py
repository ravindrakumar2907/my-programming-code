import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key')
    SESSION_TYPE = 'filesystem'

    # Optional LLM keys (leave blank to use DummyLLM)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '')

    # App settings
    SEARCH_MAX_RESULTS = int(os.getenv('SEARCH_MAX_RESULTS', '5'))
    SEARCH_TIMEOUT_SEC = int(os.getenv('SEARCH_TIMEOUT_SEC', '10'))
