# Local Agentic RAG Setup Guide

## 🎯 Version: Local (Ollama) - 100% Offline Processing

### 📋 Requirements

```txt
crewai==0.28.8
crewai-tools==0.2.6
langchain-community==0.0.38
qdrant-client==1.7.0
firecrawl-py==0.0.16
PyPDF2==3.0.1
```

### 🚀 Installation Steps

#### 1. Install Ollama (Local LLM)

**Windows:**
Download from https://ollama.com/download

**Linux/macOS:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. Pull Llama 3.2 Model

```bash
ollama pull llama3.2
```

#### 3. Install Python Dependencies

```bash
pip install -r local/requirements_local.txt
```

#### 4. Get Firecrawl API Key (Optional)

1. Sign up at https://firecrawl.dev
2. Get your API key from dashboard
3. Copy `local/.env_local` to `.env` and update with your key

#### 5. Prepare Your Documents

```bash
mkdir documents
# Add your PDF files to this folder
```

### 🎯 Usage

#### Run Application

```bash
# Copy environment file
cp local/.env_local .env

# Run local version
python local/agentic_rag.py
```

#### Commands

1. **Ask Questions:**

   ```
   Your query: What is RAG?
   ```

2. **Ingest New PDFs:**

   ```
   Your query: ingest path/to/document.pdf
   ```

3. **Exit:**
   ```
   Your query: quit
   ```

### 🔧 Configuration

Edit these variables in `local/agentic_rag.py`:

```python
QDRANT_PATH = "./qdrant_data"        # Vector DB storage
COLLECTION_NAME = "documents"         # Collection name
EMBEDDING_MODEL = "llama3.2"         # Embedding model
LLM_MODEL = "llama3.2"               # Response generation model
```

### 🏗️ Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Retriever Agent           │
│  ┌─────────────────────┐    │
│  │ 1. Search Local DB  │    │
│  │    (Qdrant)         │    │
│  └──────────┬──────────┘    │
│             │                │
│             ▼                │
│  ┌─────────────────────┐    │
│  │ 2. If needed, Web   │    │
│  │    Search           │    │
│  │    (Firecrawl)      │    │
│  └──────────┬──────────┘    │
└─────────────┼────────────────┘
              │
              ▼ (Context)
┌─────────────────────────────┐
│   Response Gen Agent        │
│  ┌─────────────────────┐    │
│  │ Generate coherent   │    │
│  │ response using      │    │
│  │ Llama 3.2           │    │
│  └──────────┬──────────┘    │
└─────────────┼────────────────┘
              │
              ▼
     ┌────────────────┐
     │ Final Response │
     └────────────────┘
```

### 📊 Features

✅ **100% Local Processing** - All LLM operations run on your machine
✅ **Persistent Vector Storage** - Qdrant stores embeddings locally
✅ **Multi-Agent System** - CrewAI orchestrates specialized agents
✅ **Fallback Mechanism** - Searches web when local docs insufficient
✅ **PDF Ingestion** - Automatically processes and indexes PDFs
✅ **Interactive CLI** - Easy-to-use command-line interface

### 🐛 Troubleshooting

#### Ollama Connection Error

```bash
# Make sure Ollama is running
ollama serve
```

#### Qdrant Issues

```bash
# Delete and reinitialize
rm -rf qdrant_data
```

#### Firecrawl Errors

- Verify API key is set correctly in `.env`
- Check internet connection
- Ensure API quota is available

### 📚 Example Queries

```
"What is RAG and how does it work?"
"Explain the concept of vector databases"
"What are the latest developments in LLMs?" (uses web search)
"Summarize key points from uploaded document"
```

### 🔒 Privacy Note

All document processing and embeddings are stored locally. Only web search queries (when local documents don't have answers) make external API calls via Firecrawl.
