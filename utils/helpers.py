import json
import re
import logging
from typing import Dict, List, Optional

def load_knowledge_base(file_path: str) -> Dict:
    """Load knowledge base from JSON file"""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Knowledge base file not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in knowledge base file: {file_path}")
        return {}

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration - SIMPLE FIX"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]  # ONLY CONSOLE LOGGING
    )

def clean_text(text: str) -> str:
    """Clean and normalize text for processing"""
    text = re.sub(r'<@[^>]+>', '', text)  # Remove user mentions
    text = re.sub(r'<#[^>]+>', '', text)  # Remove channel mentions
    text = re.sub(r'http\S+', '', text)   # Remove URLs
    text = re.sub(r'[^\w\s?]', '', text)  # Remove special chars
    return text.lower().strip()

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0