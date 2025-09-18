import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret')
    SESSION_TYPE = 'filesystem'
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', '')
