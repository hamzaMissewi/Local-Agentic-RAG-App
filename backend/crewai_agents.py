"""
CrewAI Agents Module
Defines and manages multi-agent system for RAG operations
"""

from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from config import Config
from vector_db import VectorDatabase
from embeddings import EmbeddingManager
from web_search import WebSearchManager

class CrewAIRAGSystem:
    """Multi-agent RAG system using CrewAI"""
    
    def __init__(self, embedding_provider: str = "openai", use_local_db: bool = True):
        """
        Initialize CrewAI RAG system
        
        Args:
            embedding_provider: Embedding provider ("openai" or "ollama")
            use_local_db: Use local vector database
        """
        self.vector_db = VectorDatabase(use_local=use_local_db)
        self.embedding_manager = EmbeddingManager(embedding_provider)
        self.web_search = WebSearchManager()
        
        # Initialize LLM for CrewAI
        self.llm = self._create_crewai_llm()
        
        # Initialize vector database
        vector_size = self.embedding_manager.get_embedding_dimension()
        self.vector_db.initialize_collection(vector_size)
        
        # Create agents
        self.retriever_agent = self._create_retriever_agent()
        self.response_agent = self._create_response_agent()
    
    def _create_crewai_llm(self):
        """Create LLM for CrewAI agents"""
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=Config.LLM_MODEL,
                temperature=0.7,
                openai_api_key=Config.OPENAI_API_KEY
            )
        except ImportError as e:
            print(f"❌ Failed to create CrewAI LLM: {e}")
            return None
    
    def _create_retriever_agent(self) -> Agent:
        """Create the retriever agent"""
        
        @tool("Document Search Tool")
        def search_documents(query: str) -> str:
            """Search through local document database using vector similarity"""
            try:
                query_embedding = self.embedding_manager.embed_query(query)
                results = self.vector_db.search(query_embedding, limit=Config.TOP_K_RESULTS)
                
                if not results:
                    return "No relevant documents found in local database."
                
                context = "\n\n---\n\n".join([
                    f"Source: {r['metadata'].get('source', 'N/A')}\nContent: {r['text']}"
                    for r in results
                ])
                
                return f"Retrieved {len(results)} relevant documents:\n\n{context}"
            
            except Exception as e:
                return f"Error searching documents: {str(e)}"
        
        @tool("Web Search Tool")
        def search_web(query: str) -> str:
            """Search the web using Firecrawl when local documents don't have the answer"""
            try:
                results = self.web_search.search(query, limit=3)
                return self.web_search.format_search_results(results)
            except Exception as e:
                return f"Error performing web search: {str(e)}\nPlease ensure FIRECRAWL_API_KEY is set."
        
        return Agent(
            role="Information Retriever",
            goal="Find the most relevant information to answer user queries by searching local documents first, then falling back to web search if needed",
            backstory="""You are an expert at finding relevant information. You always start by 
            searching the local document database. If the local search doesn't yield sufficient 
            results, you then search the web to ensure the user gets a comprehensive answer.""",
            tools=[search_documents, search_web],
            llm=self.llm,
            verbose=True
        )
    
    def _create_response_agent(self) -> Agent:
        """Create the response generator agent"""
        
        return Agent(
            role="Response Generator",
            goal="Generate accurate, coherent, and helpful responses based on retrieved context and user queries",
            backstory="""You are an expert at synthesizing information and creating clear, 
            accurate responses. You use the context provided by the retriever to craft responses 
            that directly answer the user's question. You cite sources when appropriate and 
            acknowledge when information is incomplete.""",
            llm=self.llm,
            verbose=True
        )
    
    def add_documents(self, texts: List[str], metadata: List[dict]) -> bool:
        """
        Add documents to the RAG system
        
        Args:
            texts: List of document texts
            metadata: List of metadata dictionaries
            
        Returns:
            bool: True if successful
        """
        try:
            # Generate embeddings
            embeddings = self.embedding_manager.embed_documents(texts)
            
            # Add to vector database
            return self.vector_db.add_documents(texts, metadata, embeddings)
        except Exception as e:
            print(f"❌ Failed to add documents: {e}")
            return False
    
    def query(self, user_query: str) -> str:
        """
        Query the RAG system
        
        Args:
            user_query: User's question
            
        Returns:
            Generated response
        """
        try:
            # Task 1: Retrieval
            retrieval_task = Task(
                description=f"""Search for relevant information to answer this query: '{user_query}'
                
                Instructions:
                1. First, search the local document database
                2. If local results are insufficient or empty, perform a web search
                3. Return all relevant context found
                """,
                agent=self.retriever_agent,
                expected_output="Relevant context from documents or web search"
            )
            
            # Task 2: Response Generation
            response_task = Task(
                description=f"""Using the context retrieved, generate a comprehensive answer to: '{user_query}'
                
                Instructions:
                1. Synthesize information from the provided context
                2. Create a clear, accurate response
                3. Cite sources when possible
                4. If context is insufficient, acknowledge limitations
                """,
                agent=self.response_agent,
                expected_output="A well-formatted, accurate answer to the user's query"
            )
            
            # Create crew
            crew = Crew(
                agents=[self.retriever_agent, self.response_agent],
                tasks=[retrieval_task, response_task],
                process=Process.sequential,
                verbose=True
            )
            
            # Execute
            result = crew.kickoff()
            return str(result)
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return f"Error processing query: {str(e)}"
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the RAG system"""
        return {
            "embedding_provider": self.embedding_manager.provider_name,
            "vector_db_type": "local" if self.vector_db.use_local else "remote",
            "web_search_available": self.web_search.is_available(),
            "collection_info": self.vector_db.get_collection_info()
        }
