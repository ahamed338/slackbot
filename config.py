import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Slack Configuration
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
    SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Bot Configuration
    BOT_NAME = os.getenv("BOT_NAME", "HelpBot")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Response Settings
    RESPONSE_DELAY = 2  # seconds
    CONFIDENCE_THRESHOLD = 0.3
    
    # Knowledge Base File
    KNOWLEDGE_BASE_FILE = "knowledge_base.json"