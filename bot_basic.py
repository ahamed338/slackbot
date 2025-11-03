import os
import time
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config import Config
from utils.helpers import load_knowledge_base, setup_logging
from utils.response_handler import ResponseHandler

# Load knowledge base and initialize response handler
knowledge_base = load_knowledge_base(Config.KNOWLEDGE_BASE_FILE)

# DEBUG: Add these lines
import json
print(f"DEBUG: Knowledge base file: {Config.KNOWLEDGE_BASE_FILE}")
print(f"DEBUG: Knowledge base entries loaded: {len(knowledge_base)}")
print(f"DEBUG: Knowledge base keys: {list(knowledge_base.keys())}")

response_handler = ResponseHandler(knowledge_base, Config.CONFIDENCE_THRESHOLD)
# Setup logging
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET
)

# Load knowledge base and initialize response handler
knowledge_base = load_knowledge_base(Config.KNOWLEDGE_BASE_FILE)
response_handler = ResponseHandler(knowledge_base, Config.CONFIDENCE_THRESHOLD)

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
            response_text = f"Hi <@{user}>! {match['answer']}"
            logger.info(f"Responding with answer for topic: {match['topic']} (score: {match['score']:.2f})")
        else:
            response_text = f"Hi <@{user}>! I'm not sure about that. Please contact IT support or check the company documentation."
            logger.info(f"No good match found for question: {text}")
        
        say(response_text)
        
    except Exception as e:
        logger.error(f"Error handling mention: {e}")
        say("Sorry, I encountered an error processing your request.")

@app.event("message")
def handle_messages(event, say):
    """Monitor messages for help requests"""
    try:
        # Skip bot messages, messages without text, or edits
        if (event.get("subtype") in ["bot_message", "message_changed"] or 
            not event.get("text")):
            return
        
        text = event["text"]
        user = event["user"]
        channel = event["channel"]
        
        # Check if this is a help request
        if response_handler.is_help_request(text):
            logger.info(f"Detected help request from user {user} in channel {channel}")
            
            match = response_handler.find_best_match(text)
            
            if match:
                # Small delay to make it feel natural
                time.sleep(Config.RESPONSE_DELAY)
                
                response = (
                    f"Hi <@{user}>! I noticed you might need help. {match['answer']}\n\n"
                    f"_If this doesn't answer your question, feel free to mention me with @{Config.BOT_NAME}_"
                )
                
                # Try to reply in thread, otherwise send to channel
                thread_ts = event.get("thread_ts") or event.get("ts")
                app.client.chat_postMessage(
                    channel=channel,
                    text=response,
                    thread_ts=thread_ts
                )
                
                logger.info(f"Auto-responded to help request with topic: {match['topic']}")
                
    except Exception as e:
        logger.error(f"Error handling message: {e}")

@app.command("/ask")
def handle_ask_command(ack, respond, command):
    """Handle /ask slash command"""
    ack()
    
    question = command["text"]
    user_id = command["user_id"]
    
    logger.info(f"Slash command /ask from user {user_id}: {question}")
    
    if not question:
        respond("Please ask a question after the /ask command. Example: `/ask how to reset password`")
        return
    
    match = response_handler.find_best_match(question)
    
    if match:
        response = f"{match['answer']}\n\n_This answered your question about {match['topic']} with {match['score']:.0%} confidence._"
    else:
        response = (
            "I couldn't find a specific answer for that question. "
            "Please try:\n"
            "• Contacting IT support at helpdesk@company.com\n"
            "• Checking the company documentation\n"
            "• Asking your question in a channel with @here"
        )
    
    respond(response)

@app.event("app_home_opened")
def handle_app_home(client, event, logger):
    """Update app home when opened"""
    try:
        user_id = event["user"]
        
        client.views_publish(
            user_id=user_id,
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🤖 Help Bot Assistant"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Hello! I'm {Config.BOT_NAME}, here to help answer your questions."
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*How to use me:*\n• Mention me `@{Config.BOT_NAME}` in any channel\n• Use `/ask [question]` for quick answers\n• I'll automatically detect help requests"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*I can help with:*\n• Password reset\n• IT support\n• Vacation policy\n• Expense reports\n• Meeting rooms\n• HR contacts\n• Software requests"
                        }
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")

if __name__ == "__main__":
    logger.info("Starting Basic Help Bot...")
    handler = SocketModeHandler(app, Config.SLACK_APP_TOKEN)
    handler.start()