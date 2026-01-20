"""
FastAPI Application Module
REST API endpoints for RAG system
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import shutil
from pathlib import Path

# Import our modules
from config import Config
from document_processor import DocumentProcessor
from vector_db import VectorDatabase
from embeddings import EmbeddingManager
from llm import LLMManager
from web_search import WebSearchManager
from crewai_agents import CrewAIRAGSystem

# Initialize FastAPI
app = FastAPI(title="RAG API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class QueryRequest(BaseModel):
    question: str
    top_k: int = Config.TOP_K_RESULTS

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: Optional[float] = None

class DocumentInfo(BaseModel):
    id: str
    filename: str
    size: int
    upload_date: str

class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    chunks_created: int

class HealthResponse(BaseModel):
    status: str
    embedding_provider: str
    vector_db_type: str
    web_search_available: bool
    documents_count: int

# Initialize components
doc_processor = DocumentProcessor()
vector_db = VectorDatabase(use_local=False)  # Use remote for API
embedding_manager = EmbeddingManager("openai")
llm_manager = LLMManager("openai")
web_search = WebSearchManager()
crewai_system = CrewAIRAGSystem("openai", use_local_db=False)

# Global index for LlamaIndex (if needed)
index_api = None

def initialize_api_system():
    """Initialize the API system"""
    global index_api
    
    # Initialize vector database
    vector_size = embedding_manager.get_embedding_dimension()
    vector_db.initialize_collection(vector_size)
    
    print("🚀 RAG API System initialized successfully")

@app.on_event("startup")
async def startup_event():
    """Initialize API system on startup"""
    initialize_api_system()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    collection_info = vector_db.get_collection_info()
    
    return HealthResponse(
        status="healthy",
        embedding_provider=embedding_manager.provider_name,
        vector_db_type="remote",
        web_search_available=web_search.is_available(),
        documents_count=collection_info.get("points_count", 0)
    )

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document (PDF, TXT, DOCX, MD)
    """
    # Validate file type
    allowed_extensions = {".pdf", ".txt", ".docx", ".md", ".doc"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {allowed_extensions}"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Save file
        doc_id, file_path = doc_processor.save_uploaded_file(file_content, file.filename)
        
        # Process document
        result = doc_processor.process_document(file_path, doc_id, file.filename)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Add to vector database
        success = crewai_system.add_documents(result["chunks"], result["metadata"])
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add documents to vector database")
        
        return UploadResponse(
            message="Document uploaded and indexed successfully",
            document_id=doc_id,
            filename=file.filename,
            chunks_created=result["total_chunks"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the RAG system with a question
    """
    try:
        # Use CrewAI system for query
        response = crewai_system.query(request.question)
        
        # Extract sources (simplified - in production, track sources better)
        sources = ["Uploaded documents"]
        
        return QueryResponse(
            answer=response,
            sources=sources,
            confidence=None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    List all uploaded documents
    """
    try:
        documents = doc_processor.list_documents()
        return [
            DocumentInfo(
                id=doc["id"],
                filename=doc["filename"],
                size=doc["size"],
                upload_date=str(doc["upload_date"])
            )
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document by ID
    """
    try:
        # Delete files
        deleted = doc_processor.delete_document_files(document_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Note: In production, you'd also delete from vector database
        
        return {"message": f"Document {document_id} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@app.post("/clear")
async def clear_all_documents():
    """
    Clear all documents and reset the system
    """
    try:
        # Delete all files
        for file_path in Config.UPLOAD_DIR.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        
        # Clear vector database
        vector_db.delete_collection()
        
        # Reinitialize
        vector_size = embedding_manager.get_embedding_dimension()
        vector_db.initialize_collection(vector_size)
        
        return {"message": "All documents cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RAG API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /upload",
            "query": "POST /query",
            "list": "GET /documents",
            "delete": "DELETE /documents/{id}",
            "clear": "POST /clear",
            "health": "GET /health"
        },
        "system_info": crewai_system.get_system_info()
    }

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting RAG API Server on http://{Config.API_HOST}:{Config.API_PORT}")
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
