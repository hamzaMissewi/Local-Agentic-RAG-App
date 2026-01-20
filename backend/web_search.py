"""
Web Search Module
Handles web search operations using Firecrawl
"""

from typing import List, Dict, Any
from config import Config

class WebSearchProvider:
    """Base class for web search providers"""
    
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search the web for information"""
        raise NotImplementedError

class FirecrawlSearch(WebSearchProvider):
    """Firecrawl web search provider"""
    
    def __init__(self):
        try:
            from firecrawl import FirecrawlApp
            self.client = FirecrawlApp(api_key=Config.FIRECRAWL_API_KEY)
        except ImportError as e:
            print(f"❌ Failed to import Firecrawl: {e}")
            self.client = None
    
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search the web using Firecrawl
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        if not self.client:
            print("❌ Firecrawl client not initialized")
            return []
        
        try:
            search_results = self.client.search(query, limit=limit)
            
            if not search_results:
                return []
            
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "content": result.get("content", "")[:500],  # Limit content length
                    "score": result.get("score", 0.0)
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Web search failed: {e}")
            return []
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a specific URL
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with scraped content
        """
        if not self.client:
            print("❌ Firecrawl client not initialized")
            return {}
        
        try:
            result = self.client.scrape_url(url)
            return {
                "url": url,
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "success": True
            }
        except Exception as e:
            print(f"❌ URL scraping failed: {e}")
            return {
                "url": url,
                "error": str(e),
                "success": False
            }

class WebSearchManager:
    """Manages web search operations"""
    
    def __init__(self, provider: str = "firecrawl"):
        """
        Initialize web search manager
        
        Args:
            provider: Web search provider (currently only "firecrawl")
        """
        self.provider_name = provider
        self.provider = self._create_provider(provider)
    
    def _create_provider(self, provider: str) -> WebSearchProvider:
        """Create web search provider instance"""
        if provider.lower() == "firecrawl":
            return FirecrawlSearch()
        else:
            raise ValueError(f"Unsupported web search provider: {provider}")
    
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search the web for information"""
        return self.provider.search(query, limit)
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into readable text
        
        Args:
            results: List of search results
            
        Returns:
            Formatted string with search results
        """
        if not results:
            return "No web results found."
        
        context = "\n\n---\n\n".join([
            f"URL: {r.get('url', 'N/A')}\nContent: {r.get('content', '')}"
            for r in results
        ])
        
        return f"Web search results:\n\n{context}"
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a specific URL"""
        return self.provider.scrape_url(url)
    
    def is_available(self) -> bool:
        """Check if web search is available"""
        return self.provider is not None and Config.FIRECRAWL_API_KEY is not None
