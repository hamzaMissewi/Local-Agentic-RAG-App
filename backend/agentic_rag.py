"""
Local Agentic RAG Application
Uses CrewAI + Llama 3.2 + Qdrant + Firecrawl
"""

import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from firecrawl import FirecrawlApp
import PyPDF2
from pathlib import Path
import uuid

# ================== CONFIGURATION ==================
QDRANT_PATH = "./qdrant_data"
COLLECTION_NAME = "documents"
EMBEDDING_MODEL = "llama3.2"
LLM_MODEL = "llama3.2"
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# ================== INITIALIZE COMPONENTS ==================

# Initialize Ollama LLM
llm = Ollama(model=LLM_MODEL, temperature=0.7)

# Initialize embeddings
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

# Initialize Qdrant client (local storage)
qdrant_client = QdrantClient(path=QDRANT_PATH)

# Initialize Firecrawl
firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

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

# ================== CREWAI TOOLS ==================

@tool("Document Search Tool")
def search_documents(query: str) -> str:
    """Search through local document database using vector similarity"""
    try:
        query_embedding = embeddings.embed_query(query)
        
        results = qdrant_client.search(
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
        # Use Firecrawl to search and scrape
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

# ================== AGENTS ==================

# 1️⃣ Retriever Agent
retriever_agent = Agent(
    role="Information Retriever",
    goal="Find the most relevant information to answer user queries by searching local documents first, then falling back to web search if needed",
    backstory="""You are an expert at finding relevant information. You always start by 
    searching the local document database. If the local search doesn't yield sufficient 
    results, you then search the web to ensure the user gets a comprehensive answer.""",
    tools=[search_documents, search_web],
    llm=llm,
    verbose=True
)

# 2️⃣ Response Generator Agent
response_agent = Agent(
    role="Response Generator",
    goal="Generate accurate, coherent, and helpful responses based on retrieved context and user queries",
    backstory="""You are an expert at synthesizing information and creating clear, 
    accurate responses. You use the context provided by the retriever to craft responses 
    that directly answer the user's question. You cite sources when appropriate and 
    acknowledge when information is incomplete.""",
    llm=llm,
    verbose=True
)

# ================== MAIN RAG FUNCTION ==================

def run_agentic_rag(user_query: str) -> str:
    """Execute the agentic RAG pipeline"""
    
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

# ================== MAIN EXECUTION ==================

if __name__ == "__main__":
    print("🚀 Initializing Local Agentic RAG System...")
    
    # Initialize Qdrant collection
    initialize_collection()
    
    # Example: Ingest documents from a folder
    docs_folder = Path("./documents")
    if docs_folder.exists():
        for pdf_file in docs_folder.glob("*.pdf"):
            ingest_pdf(str(pdf_file))
    else:
        print(f"\n⚠️  No documents folder found at {docs_folder}")
        print("Create a './documents' folder and add PDF files to ingest them.")
    
    # Interactive query loop
    print("\n" + "="*60)
    print("📚 Local Agentic RAG System Ready!")
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
                ingest_pdf(pdf_path)
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
