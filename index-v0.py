"""
Integrated RAG Application
Combines CrewAI CLI + FastAPI Backend + LlamaIndex + Qdrant + OpenAI
"""

import os
from dotenv import load_dotenv
import uuid
import shutil
from pathlib import Path
from typing import List, Optional

# Load environment variables
load_dotenv()

# ================== CONFIGURATION ==================
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_data")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
UPLOAD_DIR = Path("./uploads")

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
Path(QDRANT_PATH).mkdir(exist_ok=True)

# ================== CLI COMPONENTS (CrewAI) ==================
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from firecrawl import FirecrawlApp
import PyPDF2

# Initialize Ollama LLM
llm = Ollama(model=LLM_MODEL, temperature=0.7)

# Initialize embeddings
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

# Initialize CrewAI components
llm_crew = ChatOpenAI(model=LLM_MODEL, temperature=0.7, openai_api_key=OPENAI_API_KEY)
embeddings_crew = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)

# Initialize Qdrant client (local storage)
qdrant_client = QdrantClient(path=QDRANT_PATH)

qdrant_client_crew = QdrantClient(path=QDRANT_PATH)

# Initialize Firecrawl
firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

# CrewAI Tools
@tool("Document Search Tool")
def search_documents(query: str) -> str:
    """Search through local document database using vector similarity"""
    try:
        query_embedding = embeddings_crew.embed_query(query)
        
        results = qdrant_client_crew.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=3
        )
        
        if not results:
            return "No relevant documents found in local database."
        
        context = "\n\n---\n\n".join([
            f"Source: {r.payload['source']}\nContent: {r.payload['text']}"
            for r in results
        ])
        
        return f"Retrieved {len(results)} relevant documents:\n\n{context}"
    
    except Exception as e:
        return f"Error searching documents: {str(e)}"

@tool("Web Search Tool")
def search_web(query: str) -> str:
    """Search the web using Firecrawl when local documents don't have the answer"""
    try:
        search_results = firecrawl.search(query, limit=3)
        
        if not search_results:
            return "No web results found."
        
        context = "\n\n---\n\n".join([
            f"URL: {r.get('url', 'N/A')}\nContent: {r.get('content', '')[:500]}..."
            for r in search_results
        ])
        
        return f"Web search results:\n\n{context}"
    
    except Exception as e:
        return f"Error performing web search: {str(e)}\nPlease ensure FIRECRAWL_API_KEY is set."

# CrewAI Agents
retriever_agent = Agent(
    role="Information Retriever",
    goal="Find the most relevant information to answer user queries by searching local documents first, then falling back to web search if needed",
    backstory="""You are an expert at finding relevant information. You always start by 
    searching the local document database. If the local search doesn't yield sufficient 
    results, you then search the web to ensure the user gets a comprehensive answer.""",
    tools=[search_documents, search_web],
    llm=llm_crew,
    verbose=True
)

response_agent = Agent(
    role="Response Generator",
    goal="Generate accurate, coherent, and helpful responses based on retrieved context and user queries",
    backstory="""You are an expert at synthesizing information and creating clear, 
    accurate responses. You use the context provided by the retriever to craft responses 
    that directly answer the user's question. You cite sources when appropriate and 
    acknowledge when information is incomplete.""",
    llm=llm_crew,
    verbose=True
)

# ================== API COMPONENTS (FastAPI + LlamaIndex) ==================
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# LlamaIndex imports
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
    Document
)
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter

# Initialize FastAPI
app = FastAPI(title="Integrated RAG API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LlamaIndex Settings
Settings.llm = OpenAI(
    model=LLM_MODEL,
    temperature=0.1,
    api_key=OPENAI_API_KEY
)
Settings.embed_model = OpenAIEmbedding(
    model=EMBEDDING_MODEL,
    api_key=OPENAI_API_KEY
)
Settings.chunk_size = 512
Settings.chunk_overlap = 50

# Initialize Qdrant for API
qdrant_client_api = QdrantClient(url=QDRANT_URL)

# Initialize Vector Store for API
try:
    collections = qdrant_client_api.get_collections().collections
    collection_exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not collection_exists:
        qdrant_client_api.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
        print(f"✓ Created API collection: {COLLECTION_NAME}")
except Exception as e:
    print(f"API Qdrant initialization error: {e}")

vector_store_api = QdrantVectorStore(
    client=qdrant_client_api,
    collection_name=COLLECTION_NAME
)

storage_context_api = StorageContext.from_defaults(vector_store=vector_store_api)

# Global index for API
index_api: Optional[VectorStoreIndex] = None

# Pydantic Models for API
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

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


# ================== VECTOR DATABASE SETUP ==================

def initialize_collection():
    """Initialize Qdrant collection if it doesn't exist"""
    collections = qdrant_client.get_collections().collections
    collection_exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not collection_exists:
        # Get embedding dimension
        sample_embedding = embeddings.embed_query("test")
        vector_size = len(sample_embedding)
        
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"✓ Created collection '{COLLECTION_NAME}' with dimension {vector_size}")
    else:
        print(f"✓ Collection '{COLLECTION_NAME}' already exists")

# ================== SHARED FUNCTIONS ==================

def initialize_collection_crew():
    """Initialize CrewAI Qdrant collection if it doesn't exist"""
    collections = qdrant_client_crew.get_collections().collections
    collection_exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not collection_exists:
        sample_embedding = embeddings_crew.embed_query("test")
        vector_size = len(sample_embedding)
        
        qdrant_client_crew.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print(f"✓ Created CrewAI collection '{COLLECTION_NAME}' with dimension {vector_size}")
    else:
        print(f"✓ CrewAI collection '{COLLECTION_NAME}' already exists")


# ================== DOCUMENT INGESTION ==================

def ingest_pdf(pdf_path: str, chunk_size: int = 500):
    """Extract text from PDF and store in Qdrant"""
    print(f"\n📄 Processing PDF: {pdf_path}")
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    # Split text into chunks
    chunks = []
    words = text.split()
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    # Generate embeddings and store
    points = []
    for idx, chunk in enumerate(chunks):
        embedding = embeddings.embed_query(chunk)
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk,
                "source": pdf_path,
                "chunk_id": idx
            }
        )
        points.append(point)
    
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✓ Ingested {len(chunks)} chunks from {pdf_path}")
    
def ingest_pdf_crew(pdf_path: str, chunk_size: int = 500):
    """Extract text from PDF and store in Qdrant for CrewAI"""
    print(f"\n📄 Processing PDF for CrewAI: {pdf_path}")
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    # Split text into chunks
    chunks = []
    words = text.split()
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    # Generate embeddings and store
    points = []
    for idx, chunk in enumerate(chunks):
        embedding = embeddings_crew.embed_query(chunk)
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk,
                "source": pdf_path,
                "chunk_id": idx
            }
        )
        points.append(point)
    
    qdrant_client_crew.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✓ Ingested {len(chunks)} chunks from {pdf_path}")

def initialize_index_api():
    """Initialize or load the API index"""
    global index_api
    try:
        index_api = VectorStoreIndex.from_vector_store(
            vector_store=vector_store_api,
            storage_context=storage_context_api
        )
        print("✓ API Index loaded from Qdrant")
    except Exception as e:
        print(f"API Index initialization: {e}")
        index_api = VectorStoreIndex(
            [],
            storage_context=storage_context_api
        )

def run_agentic_rag(user_query: str) -> str:
    """Execute the CrewAI agentic RAG pipeline"""
    
    # Task 1: Retrieval
    retrieval_task = Task(
        description=f"""Search for relevant information to answer this query: '{user_query}'
        
        Instructions:
        1. First, search the local document database
        2. If local results are insufficient or empty, perform a web search
        3. Return all relevant context found
        """,
        agent=retriever_agent,
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
        agent=response_agent,
        expected_output="A well-formatted, accurate answer to the user's query"
    )
    
    # Create crew
    crew = Crew(
        agents=[retriever_agent, response_agent],
        tasks=[retrieval_task, response_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute
    result = crew.kickoff()
    return result

# ================== API ENDPOINTS ==================

@app.on_event("startup")
async def startup_event():
    """Initialize API index on startup"""
    initialize_index_api()
    print("🚀 Integrated RAG Backend is ready!")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "qdrant_connected": True,
        "index_loaded": index_api is not None,
        "crewai_ready": True
    }

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF, TXT, DOCX, MD)"""
    global index_api
    
    # Validate file type
    allowed_extensions = {".pdf", ".txt", ".docx", ".md", ".doc"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {allowed_extensions}"
        )
    
    try:
        # Generate unique ID and save file
        doc_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Load and process document
        documents = SimpleDirectoryReader(
            input_files=[str(file_path)]
        ).load_data()
        
        # Add metadata
        for doc in documents:
            doc.metadata["document_id"] = doc_id
            doc.metadata["filename"] = file.filename
        
        # Parse into nodes
        node_parser = SentenceSplitter(
            chunk_size=512,
            chunk_overlap=50
        )
        nodes = node_parser.get_nodes_from_documents(documents)
        
        # Insert into API index
        if index_api is None:
            initialize_index_api()
        
        index_api.insert_nodes(nodes)
        
        # Also ingest into CrewAI if it's a PDF
        if file_ext == ".pdf":
            ingest_pdf_crew(str(file_path))
        
        return UploadResponse(
            message="Document uploaded and indexed successfully",
            document_id=doc_id,
            filename=file.filename,
            chunks_created=len(nodes)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system with a question"""
    global index_api
    
    if index_api is None:
        raise HTTPException(
            status_code=400,
            detail="No documents indexed yet. Please upload documents first."
        )
    
    try:
        # Create query engine
        query_engine = index_api.as_query_engine(
            similarity_top_k=request.top_k,
            response_mode="compact"
        )
        
        # Execute query
        response = query_engine.query(request.question)
        
        # Extract sources
        sources = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                filename = node.metadata.get('filename', 'Unknown')
                if filename not in sources:
                    sources.append(filename)
        
        return QueryResponse(
            answer=str(response),
            sources=sources,
            confidence=None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """List all uploaded documents"""
    documents = []
    
    for file_path in UPLOAD_DIR.glob("*"):
        if file_path.is_file():
            parts = file_path.name.split("_", 1)
            if len(parts) == 2:
                doc_id, filename = parts
                documents.append(DocumentInfo(
                    id=doc_id,
                    filename=filename,
                    size=file_path.stat().st_size,
                    upload_date=str(file_path.stat().st_mtime)
                ))
    
    return documents

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document by ID"""
    # Find and delete file
    deleted = False
    for file_path in UPLOAD_DIR.glob(f"{document_id}_*"):
        file_path.unlink()
        deleted = True
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": f"Document {document_id} deleted successfully"}

@app.post("/clear")
async def clear_all_documents():
    """Clear all documents and reset the index"""
    global index_api
    
    try:
        # Delete all files
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file():
                file_path.unlink()
        
        # Recreate collection
        qdrant_client_api.delete_collection(COLLECTION_NAME)
        qdrant_client_api.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
        
        # Reinitialize index
        initialize_index_api()
        
        return {"message": "All documents cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Integrated RAG API is running",
        "features": ["CrewAI CLI", "FastAPI Backend", "LlamaIndex", "Qdrant", "OpenAI"],
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /upload",
            "query": "POST /query",
            "list": "GET /documents",
            "delete": "DELETE /documents/{id}",
            "clear": "POST /clear",
            "health": "GET /health"
        }
    }

# ================== CLI INTERFACE ==================

def run_cli():
    """Run the CrewAI CLI interface"""
    print("🚀 Initializing Integrated RAG System (CLI Mode)...")
    
    # Check API key
    if not OPENAI_API_KEY:
        print("⚠️  Please set your OPENAI_API_KEY in the .env file")
        print("   1. Get an API key from: https://platform.openai.com/api-keys")
        print("   2. Update the .env file with your actual API key")
        print("   3. Restart the application")
        return
    
    # Initialize CrewAI collection
    initialize_collection_crew()
    
    # Example: Ingest documents from a folder
    docs_folder = Path("./documents")
    if docs_folder.exists():
        for pdf_file in docs_folder.glob("*.pdf"):
            ingest_pdf_crew(str(pdf_file))
    else:
        print(f"\n⚠️  No documents folder found at {docs_folder}")
        print("Create a './documents' folder and add PDF files to ingest them.")
    
    # Interactive query loop
    print("\n" + "="*60)
    print("📚 Integrated RAG System Ready! (CLI Mode)")
    print("="*60)
    print("\nCommands:")
    print("  - Type your question to search")
    print("  - Type 'ingest <pdf_path>' to add a new PDF")
    print("  - Type 'quit' to exit")
    print("="*60 + "\n")
    
    while True:
        user_input = input("\n🔍 Your query: ").strip()
        
        if user_input.lower() == 'quit':
            print("\n👋 Goodbye!")
            break
        
        if user_input.lower().startswith('ingest '):
            pdf_path = user_input[7:].strip()
            if Path(pdf_path).exists():
                ingest_pdf_crew(pdf_path)
            else:
                print(f"❌ File not found: {pdf_path}")
            continue
        
        if not user_input:
            continue
        
        print("\n🤖 Processing your query...\n")
        response = run_agentic_rag(user_input)
        print("\n" + "="*60)
        print("📝 RESPONSE:")
        print("="*60)
        print(response)
        print("="*60)

# ================== MAIN EXECUTION ==================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Run CLI mode
        run_cli()
    else:
        # Run API server (default)
        import uvicorn
        print("🚀 Starting Integrated RAG API Server...")
        print("   API: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs")
        print("   CLI: python index.py cli")
        uvicorn.run(app, host="0.0.0.0", port=8000)
