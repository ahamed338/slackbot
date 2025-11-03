import os
import time
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from config import Config
from utils.helpers import load_knowledge_base, setup_logging
from utils.enhanced_handler import EnhancedResponseHandler
from utils.conversation_memory import ConversationMemory

# Setup logging
setup_logging(Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET
)

# Load knowledge base and initialize enhanced handlers
knowledge_base = load_knowledge_base(Config.KNOWLEDGE_BASE_FILE)
response_handler = EnhancedResponseHandler(knowledge_base)
conversation_memory = ConversationMemory()

@app.event("app_mention")
def handle_mentions(event, say):
    """Handle when the bot is mentioned - ENHANCED VERSION"""
    try:
        text = event["text"]
        user = event["user"]
        channel = event["channel"]
        
        logger.info(f"Bot mentioned by user {user} in channel {channel}")
        logger.info(f"Question: {text}")
        
        # Get natural, conversational response
        response = response_handler.get_natural_response(text, user)
        
        # Store conversation in memory
        conversation_memory.add_conversation(user, text, response)
        
        logger.info(f"Responding to user {user}")
        say(response)
        
    except Exception as e:
        logger.error(f"Error handling mention: {e}")
        say("Sorry, I encountered an error processing your request. Please try again or contact IT support.")

@app.event("message")
def handle_messages(event, say):
    """Monitor messages for help requests - ENHANCED VERSION"""
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
            
            # Get natural response
            response = response_handler.get_natural_response(text, user)
            
            # Store conversation
            conversation_memory.add_conversation(user, text, response)
            
            # Small delay to make it feel natural
            time.sleep(Config.RESPONSE_DELAY)
            
            # Enhanced response with better formatting
            enhanced_response = (
                f"{response}\n\n"
                f"_💡 Pro tip: You can also mention me with `@{Config.BOT_NAME}` for faster help!_"
            )
            
            # Try to reply in thread, otherwise send to channel
            thread_ts = event.get("thread_ts") or event.get("ts")
            app.client.chat_postMessage(
                channel=channel,
                text=enhanced_response,
                thread_ts=thread_ts
            )
            
            logger.info(f"Auto-responded to help request from user {user}")
                
    except Exception as e:
        logger.error(f"Error handling message: {e}")

@app.command("/ask")
def handle_ask_command(ack, respond, command):
    """Handle /ask slash command - ENHANCED VERSION"""
    ack()
    
    question = command["text"]
    user_id = command["user_id"]
    
    logger.info(f"Slash command /ask from user {user_id}: {question}")
    
    if not question:
        respond("Please ask a question after the /ask command. Example: `/ask how to reset password`")
        return
    
    # Get natural response
    response = response_handler.get_natural_response(question, user_id)
    
    # Store conversation
    conversation_memory.add_conversation(user_id, question, response)
    
    respond(response)

@app.command("/history")
def handle_history_command(ack, respond, command):
    """Show conversation history for the user"""
    ack()
    
    user_id = command["user_id"]
    
    logger.info(f"History command from user {user_id}")
    
    history = conversation_memory.get_user_history(user_id)
    
    if not history:
        respond("You haven't had any conversations with me yet. Ask me something using `/ask` or by mentioning me!")
        return
    
    # Format history response
    history_text = "*Your recent conversations with me:*\n\n"
    
    for i, conv in enumerate(reversed(history[-5:]), 1):  # Show last 5 conversations
        question = conv["question"][:100] + "..." if len(conv["question"]) > 100 else conv["question"]
        history_text += f"{i}. *You asked:* {question}\n"
    
    history_text += "\n_Need more help? Just ask!_"
    
    respond(history_text)

@app.command("/help")
def handle_help_command(ack, respond, command):
    """Show help information about the bot"""
    ack()
    
    help_text = f"""
*🤖 {Config.BOT_NAME} - Help Guide*

*How to use me:*
• *Mention me:* `@{Config.BOT_NAME}` followed by your question
• *Slash command:* `/ask [your question]` for quick answers
• *Auto-detection:* I'll often detect help requests automatically

*Examples:*
• `@{Config.BOT_NAME} how do I reset my password?`
• `/ask wifi network information`
• `Does anyone know the vacation policy?`

*Additional commands:*
• `/history` - See your recent conversations
• `/help` - Show this help message

*I can help with:* IT support, HR policies, software requests, meeting rooms, and much more!
"""
    
    respond(help_text)

@app.event("app_home_opened")
def handle_app_home(client, event, logger):
    """Update app home when opened - SAFE VERSION"""
    try:
        user_id = event["user"]
        
        # Simple home view that's less likely to cause errors
        home_view = {
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🤖 {Config.BOT_NAME}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hello! I'm your helpful assistant here to answer questions and provide support."
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Quick Start:*\n• Mention me in any channel\n• Use `/ask` for direct questions\n• I automatically detect help requests"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Need help?* Try these:\n• `/ask how to reset password`\n• `/ask wifi information`\n• `/ask IT support contact`"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "💡 Pro tip: I work best with specific questions!"
                        }
                    ]
                }
            ]
        }
        
        try:
            client.views_publish(
                user_id=user_id,
                view=home_view
            )
        except Exception as e:
            # If app home isn't fully enabled, just log it - it's not critical for bot functionality
            logger.info(f"App home view couldn't be published (non-critical): {e}")
            
    except Exception as e:
        logger.info(f"App home setup note: {e}")

# Error handler for better error management
@app.error
def global_error_handler(error, body, logger):
    logger.error(f"Error: {error}")
    logger.debug(f"Request body: {body}")

if __name__ == "__main__":
    logger.info("Starting Enhanced Help Bot...")
    logger.info(f"Loaded {len(knowledge_base)} knowledge base entries")
    
    try:
        handler = SocketModeHandler(app, Config.SLACK_APP_TOKEN)
        handler.start()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise