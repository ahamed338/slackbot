import logging
from typing import Dict, Optional
from utils.helpers import calculate_similarity, clean_text

class ResponseHandler:
    def __init__(self, knowledge_base: Dict, confidence_threshold: float = 0.3):
        self.knowledge_base = knowledge_base
        self.confidence_threshold = confidence_threshold
        
        # Help keywords to detect help requests
        self.help_keywords = [
            "help", "how to", "how do i", "what is", "where is", 
            "can someone", "does anyone know", "question", "support",
            "trouble with", "problem with", "issue with", "anyone know",
            "need help", "looking for", "where can i", "how can i"
        ]
    
    def is_help_request(self, text: str) -> bool:
        """Check if message appears to be a help request"""
        if not text:
            return False
            
        clean_msg = clean_text(text)
        
        # Check for help keywords
        if any(keyword in clean_msg for keyword in self.help_keywords):
            return True
        
        # Check for question marks (but not in URLs)
        if '?' in text and '://' not in text:
            return True
            
        return False
    
    def find_best_match(self, question: str) -> Optional[Dict]:
        """Find the best matching answer from knowledge base"""
        clean_question = clean_text(question)
        best_match = None
        best_score = 0.0
        
        for key, data in self.knowledge_base.items():
            # Check against the main question
            question_score = calculate_similarity(clean_question, data["question"])
            
            # Check against keywords
            keyword_score = 0
            for keyword in data.get("keywords", []):
                keyword_score = max(keyword_score, calculate_similarity(clean_question, keyword))
            
            # Take the best score
            score = max(question_score, keyword_score)
            
            if score > best_score and score >= self.confidence_threshold:
                best_score = score
                best_match = {
                    "answer": data["answer"],
                    "score": score,
                    "topic": key
                }
        
        return best_match