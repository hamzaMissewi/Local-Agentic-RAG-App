"""
Vector Database Module
Handles Qdrant operations for both local and cloud storage
"""

import uuid
from typing import List, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import Config

class VectorDatabase:
    """Unified vector database handler"""
    
    def __init__(self, use_local: bool = True):
        """
        Initialize vector database
        
        Args:
            use_local: Use local storage (True) or remote Qdrant (False)
        """
        if use_local:
            self.client = QdrantClient(path=Config.QDRANT_PATH)
        else:
            self.client = QdrantClient(url=Config.QDRANT_URL)
        
        self.use_local = use_local
        self.collection_name = Config.COLLECTION_NAME
    
    def initialize_collection(self, vector_size: int = 1536) -> bool:
        """
        Initialize Qdrant collection if it doesn't exist
        
        Args:
            vector_size: Dimension of embeddings
            
        Returns:
            bool: True if collection exists or was created successfully
        """
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if not collection_exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                print(f"✓ Created collection '{self.collection_name}' with dimension {vector_size}")
            else:
                print(f"✓ Collection '{self.collection_name}' already exists")
            
            return True
        except Exception as e:
            print(f"❌ Collection initialization failed: {e}")
            return False
    
    def add_documents(self, texts: List[str], metadata: List[dict], embeddings: List[List[float]]) -> bool:
        """
        Add documents to vector database
        
        Args:
            texts: List of document texts
            metadata: List of metadata dictionaries
            embeddings: List of embedding vectors
            
        Returns:
            bool: True if successful
        """
        try:
            points = []
            for idx, (text, meta, embedding) in enumerate(zip(texts, metadata, embeddings)):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": text,
                        **meta
                    }
                )
                points.append(point)
            
            self.client.upsert(collection_name=self.collection_name, points=points)
            print(f"✓ Added {len(points)} documents to vector database")
            return True
        except Exception as e:
            print(f"❌ Failed to add documents: {e}")
            return False
    
    def search(self, query_embedding: List[float], limit: int = Config.TOP_K_RESULTS) -> List[dict]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query vector embedding
            limit: Maximum number of results
            
        Returns:
            List of search results with payloads and scores
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "text": result.payload.get("text", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"},
                    "score": result.score
                })
            
            return formatted_results
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"✓ Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            print(f"❌ Failed to delete collection: {e}")
            return False
    
    def get_collection_info(self) -> dict:
        """Get information about the collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "vector_size": info.config.params.vectors.size
            }
        except Exception as e:
            print(f"❌ Failed to get collection info: {e}")
            return {}
