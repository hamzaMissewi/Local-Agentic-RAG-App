"""
Embedding Module
Handles text embedding generation using different providers
"""

from typing import List, Union
from config import Config

class EmbeddingProvider:
    """Base class for embedding providers"""
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text"""
        raise NotImplementedError
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        raise NotImplementedError

class OpenAIEmbeddings(EmbeddingProvider):
    """OpenAI embedding provider"""
    
    def __init__(self):
        try:
            from langchain_openai import OpenAIEmbeddings
            self.client = OpenAIEmbeddings(
                model=Config.EMBEDDING_MODEL,
                openai_api_key=Config.OPENAI_API_KEY
            )
        except ImportError as e:
            print(f"❌ Failed to import OpenAI embeddings: {e}")
            self.client = None
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text"""
        if not self.client:
            raise RuntimeError("OpenAI embeddings client not initialized")
        
        try:
            return self.client.embed_query(text)
        except Exception as e:
            print(f"❌ Query embedding failed: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        if not self.client:
            raise RuntimeError("OpenAI embeddings client not initialized")
        
        try:
            return self.client.embed_documents(texts)
        except Exception as e:
            print(f"❌ Document embedding failed: {e}")
            raise

class OllamaEmbeddings(EmbeddingProvider):
    """Ollama embedding provider for local processing"""
    
    def __init__(self):
        try:
            from langchain_community.embeddings import OllamaEmbeddings
            self.client = OllamaEmbeddings(model=Config.EMBEDDING_MODEL)
        except ImportError as e:
            print(f"❌ Failed to import Ollama embeddings: {e}")
            self.client = None
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text"""
        if not self.client:
            raise RuntimeError("Ollama embeddings client not initialized")
        
        try:
            return self.client.embed_query(text)
        except Exception as e:
            print(f"❌ Query embedding failed: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        if not self.client:
            raise RuntimeError("Ollama embeddings client not initialized")
        
        try:
            return self.client.embed_documents(texts)
        except Exception as e:
            print(f"❌ Document embedding failed: {e}")
            raise

class EmbeddingManager:
    """Manages embedding providers and operations"""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize embedding manager
        
        Args:
            provider: Embedding provider ("openai" or "ollama")
        """
        self.provider_name = provider
        self.provider = self._create_provider(provider)
    
    def _create_provider(self, provider: str) -> EmbeddingProvider:
        """Create embedding provider instance"""
        if provider.lower() == "openai":
            return OpenAIEmbeddings()
        elif provider.lower() == "ollama":
            return OllamaEmbeddings()
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text"""
        return self.provider.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        return self.provider.embed_documents(texts)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        # Test with a simple query to get dimension
        test_embedding = self.embed_query("test")
        return len(test_embedding)
    
    def switch_provider(self, provider: str):
        """Switch to a different embedding provider"""
        self.provider_name = provider
        self.provider = self._create_provider(provider)
        print(f"✓ Switched to {provider} embeddings")
