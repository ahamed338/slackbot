import json
import os
from datetime import datetime

class ConversationMemory:
    def __init__(self):
        self.memory_file = "conversation_memory.json"
        self.memory = self.load_memory()
    
    def load_memory(self):
        """Load conversation memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
        
        return {}
    
    def save_memory(self):
        """Save conversation memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def add_conversation(self, user_id: str, question: str, response: str):
        """Add a conversation to memory"""
        if user_id not in self.memory:
            self.memory[user_id] = []
        
        self.memory[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "response": response
        })
        
        # Keep only last 10 conversations per user
        if len(self.memory[user_id]) > 10:
            self.memory[user_id] = self.memory[user_id][-10:]
        
        self.save_memory()
    
    def get_user_history(self, user_id: str):
        """Get conversation history for a user"""
        return self.memory.get(user_id, [])