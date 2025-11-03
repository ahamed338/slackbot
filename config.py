import os

class Config:
    # Slack Configuration - will get from Render environment variables
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
    SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    
    # Bot Configuration
    BOT_NAME = os.environ.get("BOT_NAME", "HelpBot")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    
    # Response Settings
    RESPONSE_DELAY = 2  # seconds
    CONFIDENCE_THRESHOLD = 0.3
    
    # Knowledge Base File
    KNOWLEDGE_BASE_FILE = "knowledge_base.json"