"""
LLM Module
Handles language model operations for different providers
"""

# from typing import List, Optional
from config import Config

class LLMProvider:
    """Base class for LLM providers"""
    
    def invoke(self, prompt: str) -> str:
        """Generate response from LLM"""
        raise NotImplementedError
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response based on query and context"""
        raise NotImplementedError

class OpenAILLM(LLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self):
        try:
            from langchain_openai import ChatOpenAI
            self.client = ChatOpenAI(
                model=Config.LLM_MODEL,
                temperature=0.7,
                openai_api_key=Config.OPENAI_API_KEY
            )
        except ImportError as e:
            print(f"❌ Failed to import OpenAI LLM: {e}")
            self.client = None
    
    def invoke(self, prompt: str) -> str:
        """Generate response from LLM"""
        if not self.client:
            raise RuntimeError("OpenAI LLM client not initialized")
        
        try:
            response = self.client.invoke(prompt)
            return str(response)
        except Exception as e:
            print(f"❌ LLM invocation failed: {e}")
            raise
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response based on query and context"""
        prompt = f"""Based on the following context, please answer the question:

Context:
{context}

Question: {query}

Please provide a comprehensive and accurate answer based on the context provided. If the context doesn't contain enough information, please acknowledge that limitation."""
        
        return self.invoke(prompt)

class OllamaLLM(LLMProvider):
    """Ollama LLM provider for local processing"""
    
    def __init__(self):
        try:
            from langchain_community.llms import Ollama
            self.client = Ollama(model=Config.LLM_MODEL, temperature=0.7)
        except ImportError as e:
            print(f"❌ Failed to import Ollama LLM: {e}")
            self.client = None
    
    def invoke(self, prompt: str) -> str:
        """Generate response from LLM"""
        if not self.client:
            raise RuntimeError("Ollama LLM client not initialized")
        
        try:
            response = self.client.invoke(prompt)
            return str(response)
        except Exception as e:
            print(f"❌ LLM invocation failed: {e}")
            raise
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response based on query and context"""
        prompt = f"""Based on the following context, please answer the question:

Context:
{context}

Question: {query}

Please provide a comprehensive and accurate answer based on the context provided. If the context doesn't contain enough information, please acknowledge that limitation."""
        
        return self.invoke(prompt)

class LlamaIndexLLM(LLMProvider):
    """LlamaIndex LLM provider for advanced operations"""
    
    def __init__(self):
        try:
            from llama_index.llms.openai import OpenAI
            self.client = OpenAI(
                model=Config.LLM_MODEL,
                temperature=0.1,
                api_key=Config.OPENAI_API_KEY
            )
        except ImportError as e:
            print(f"❌ Failed to import LlamaIndex LLM: {e}")
            self.client = None
    
    def invoke(self, prompt: str) -> str:
        """Generate response from LLM"""
        if not self.client:
            raise RuntimeError("LlamaIndex LLM client not initialized")
        
        try:
            response = self.client.complete(prompt)
            return str(response)
        except Exception as e:
            print(f"❌ LLM invocation failed: {e}")
            raise
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response based on query and context"""
        prompt = f"""Based on the following context, please answer the question:

Context:
{context}

Question: {query}

Please provide a comprehensive and accurate answer based on the context provided. If the context doesn't contain enough information, please acknowledge that limitation."""
        
        return self.invoke(prompt)

class LLMManager:
    """Manages LLM providers and operations"""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize LLM manager
        
        Args:
            provider: LLM provider ("openai", "ollama", or "llamaindex")
        """
        self.provider_name = provider
        self.provider = self._create_provider(provider)
    
    def _create_provider(self, provider: str) -> LLMProvider:
        """Create LLM provider instance"""
        if provider.lower() == "openai":
            return OpenAILLM()
        elif provider.lower() == "ollama":
            return OllamaLLM()
        elif provider.lower() == "llamaindex":
            return LlamaIndexLLM()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def invoke(self, prompt: str) -> str:
        """Generate response from LLM"""
        return self.provider.invoke(prompt)
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response based on query and context"""
        return self.provider.generate_response(query, context)
    
    def switch_provider(self, provider: str):
        """Switch to a different LLM provider"""
        self.provider_name = provider
        self.provider = self._create_provider(provider)
        print(f"✓ Switched to {provider} LLM")
    
    def get_provider_info(self) -> dict:
        """Get information about current provider"""
        return {
            "provider": self.provider_name,
            "model": Config.LLM_MODEL,
            "initialized": self.provider is not None
        }
