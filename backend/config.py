"""
Configuration Module for RAG Application
Handles all environment variables and settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class"""
    
    # ================== DATABASE CONFIGURATION ==================
    QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_data")
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents")
    
    # ================== MODEL CONFIGURATION ==================
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # ================== API KEYS ==================
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    
    # ================== DIRECTORIES ==================
    UPLOAD_DIR = Path("./uploads")
    DOCUMENTS_DIR = Path("./documents")
    
    # ================== PROCESSING CONFIGURATION ==================
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50
    TOP_K_RESULTS = 3
    
    # ================== API CONFIGURATION ==================
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    CORS_ORIGINS = ["http://localhost:3000"]
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.DOCUMENTS_DIR.mkdir(exist_ok=True)
        Path(cls.QDRANT_PATH).mkdir(exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        
        if not cls.FIRECRAWL_API_KEY:
            errors.append("FIRECRAWL_API_KEY is recommended for web search")
        
        return errors
