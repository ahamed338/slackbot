import random
import re
from typing import Dict, Optional

class EnhancedResponseHandler:
    def __init__(self, knowledge_base: Dict):
        self.knowledge_base = knowledge_base
        self.setup_responses()
        
        # Help keywords to detect help requests
        self.help_keywords = [
            "help", "how to", "how do i", "what is", "where is", 
            "can someone", "does anyone know", "question", "support",
            "trouble with", "problem with", "issue with", "anyone know",
            "need help", "looking for", "where can i", "how can i",
            "not working", "broken", "error", "can't find"
        ]
    
    def setup_responses(self):
        self.greetings = [
            "Hi {user}! 👋",
            "Hello {user}!",
            "Hey {user}! How can I help?",
            "Hi there {user}!",
            "Hey {user}! What can I help you with today?",
        ]
        
        self.follow_ups = [
            "Did that answer your question?",
            "Is there anything else you need help with?",
            "Let me know if you need more details!",
            "Did that solve your issue?",
            "Need anything else?",
        ]
        
        self.unknown_responses = [
            "I'm not sure about that one. Try contacting IT support at helpdesk@company.com or check our documentation.",
            "I don't have information on that yet. You might want to check our company documentation or ask in #it-help.",
            "That's beyond my current knowledge. For this, please reach out to the support team at helpdesk@company.com.",
            "I'm still learning about that topic. For now, please contact the relevant department for assistance.",
        ]
    
    def get_natural_response(self, question: str, user_id: str) -> str:
        """Generate more natural, conversational responses"""
        # Clean the question
        clean_question = self.clean_text(question)
        
        # Find the best match
        match = self.find_best_match(clean_question)
        
        if match:
            # Add natural greeting
            greeting = random.choice(self.greetings).format(user=f"<@{user_id}>")
            
            # Main answer
            answer = match["answer"]
            
            # Add follow-up question sometimes (30% chance)
            follow_up = ""
            if random.random() < 0.3:
                follow_up = f"\n\n{random.choice(self.follow_ups)}"
            
            return f"{greeting}\n\n{answer}{follow_up}"
        else:
            greeting = random.choice(self.greetings).format(user=f"<@{user_id}>")
            unknown_msg = random.choice(self.unknown_responses)
            return f"{greeting} {unknown_msg}"
    
    def find_best_match(self, question: str) -> Optional[Dict]:
        """Enhanced matching with context awareness"""
        question_lower = question.lower()
        
        # Direct keyword matches first
        for key, data in self.knowledge_base.items():
            for keyword in data["keywords"]:
                if keyword.lower() in question_lower:
                    return {
                        "answer": data["answer"],
                        "score": 1.0,
                        "topic": key
                    }
        
        # Question-based matching
        best_match = None
        best_score = 0
        
        for key, data in self.knowledge_base.items():
            score = self.calculate_match_score(question_lower, data)
            if score > best_score and score > 0.3:
                best_score = score
                best_match = {
                    "answer": data["answer"],
                    "score": score,
                    "topic": key
                }
        
        return best_match
    
    def calculate_match_score(self, question: str, data: Dict) -> float:
        """Calculate how well the question matches the knowledge base entry"""
        score = 0
        
        # Check against keywords
        for keyword in data["keywords"]:
            if keyword.lower() in question:
                score += 0.3
        
        # Check against main question
        if data["question"].lower() in question:
            score += 0.5
        
        return min(score, 1.0)
    
    def is_help_request(self, text: str) -> bool:
        """Check if message appears to be a help request"""
        if not text:
            return False
            
        clean_text = self.clean_text(text)
        
        # Check for help keywords
        if any(keyword in clean_text for keyword in self.help_keywords):
            return True
        
        # Check for question marks (but not in URLs)
        if '?' in text and '://' not in text:
            # Make sure it's not a rhetorical question
            non_rhetorical = ["how", "what", "where", "when", "why", "can", "does", "is"]
            if any(word in clean_text for word in non_rhetorical):
                return True
            
        return False
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text for processing"""
        # Remove mentions and URLs
        text = re.sub(r'<@[^>]+>', '', text)  # Remove user mentions
        text = re.sub(r'<#[^>]+>', '', text)  # Remove channel mentions
        text = re.sub(r'http\S+', '', text)   # Remove URLs
        text = re.sub(r'[^\w\s?]', '', text)  # Remove special chars except spaces and ?
        return text.lower().strip()