import os
import time
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI

from config import Config
from utils.helpers import load_knowledge_base, setup_logging
from utils.response_handler import ResponseHandler

# Setup logging
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None

# Load knowledge base
knowledge_base = load_knowledge_base(Config.KNOWLEDGE_BASE_FILE)

class AIResponseHandler(ResponseHandler):
    def __init__(self, knowledge_base: Dict, openai_client, confidence_threshold: float = 0.3):
        super().__init__(knowledge_base, confidence_threshold)
        self.openai_client = openai_client
    
    def get_ai_response(self, question: str, context: str = "") -> Optional[str]:
        """Get AI-generated response for questions not in knowledge base"""
        if not self.openai_client:
            return None
            
        try:
            prompt = f"""You are a helpful workplace assistant. Answer this question based on the context provided. If you're not sure, say so.

Context: {context}
Question: {question}

Provide a brief, helpful answer:"""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful workplace assistant. Keep answers brief, professional, and helpful. If you're uncertain, direct users to contact support."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def find_best_match(self, question: str) -> Optional[Dict]:
        """Find best match with AI fallback"""
        # First try knowledge base
        kb_match = super().find_best_match(question)
        
        if kb_match:
            return kb_match
        
        # If no good KB match and AI is available, try AI
        if self.openai_client:
            ai_response = self.get_ai_response(question)
            if ai_response:
                return {
                    "answer": f"{ai_response}\n\n_This is an AI-generated response. For official policies, please verify with the relevant department._",
                    "score": 0.5,  # Medium confidence for AI responses
                    "topic": "ai_generated"
                }
        
        return None

# Initialize AI response handler
response_handler = AIResponseHandler(knowledge_base, openai_client, Config.CONFIDENCE_THRESHOLD)

# Reuse the same event handlers from bot_basic.py
# (You can copy the event handlers from bot_basic.py here)

@app.event("app_mention")
def handle_mentions(event, say):
    """Handle when the bot is mentioned"""
    try:
        text = event["text"]
        user = event["user"]
        channel = event["channel"]
        
        logger.info(f"Bot mentioned by user {user} in channel {channel}")
        
        # Find the best answer
        match = response_handler.find_best_match(text)
        
        if match:
            if match["topic"] == "ai_generated":
                response_text = f"Hi <@{user}>! {match['answer']}"
            else:
                response_text = f"Hi <@{user}>! {match['answer']}"
            logger.info(f"Responding with answer for topic: {match['topic']} (score: {match['score']:.2f})")
        else:
            response_text = f"Hi <@{user}>! I'm not sure about that. Please contact IT support or check the company documentation."
            logger.info(f"No good match found for question: {text}")
        
        say(response_text)
        
    except Exception as e:
        logger.error(f"Error handling mention: {e}")
        say("Sorry, I encountered an error processing your request.")

# ... (Include all the other event handlers from bot_basic.py)

if __name__ == "__main__":
    if openai_client:
        logger.info("Starting AI-Powered Help Bot...")
    else:
        logger.info("Starting Help Bot (AI not configured)...")
    
    handler = SocketModeHandler(app, Config.SLACK_APP_TOKEN)
    handler.start()