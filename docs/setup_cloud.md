# Cloud Agentic RAG Setup Guide

## 🎯 Version: Cloud (OpenAI) - Hybrid Processing

### 📋 Requirements

```txt
crewai>=1.8.0
crewai-tools>=0.2.0
langchain-openai>=1.1.0
qdrant-client>=1.16.0
firecrawl-py>=4.13.0
PyPDF2>=3.0.1
python-dotenv>=1.1.0

# FastAPI Backend Dependencies
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6
pydantic>=2.0.0

# LlamaIndex Dependencies
llama-index>=0.9.48
llama-index-vector-stores-qdrant>=0.2.8
llama-index-embeddings-openai>=0.1.6
llama-index-llms-openai>=0.1.6

# Additional Document Processing
python-docx>=1.1.0
```

### 🚀 Installation Steps

#### 1. Get OpenAI API Key

1. Sign up at https://platform.openai.com/api-keys
2. Create a new API key
3. Set environment variable:

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

Or add to `.env` file:

```
OPENAI_API_KEY=sk-your-key-here
FIRECRAWL_API_KEY=fc-your-key-here
```

#### 2. Install Python Dependencies

```bash
pip install -r cloud/requirements.txt
```

#### 3. Prepare Your Documents

```bash
mkdir documents
# Add your PDF files to this folder
```

### 🎯 Usage

#### Run Application

```bash
# Use environment file
cp cloud/.env .env

# Run cloud version (API + CLI)
python cloud/index.py

# Or run integrated version
python cloud/index_integrated.py
```

#### Modes

**1. CLI Mode:**

```bash
python cloud/index.py cli
```

**2. API Mode:**

```bash
python cloud/index.py
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

**3. Integrated Mode:**

```bash
python cloud/index_integrated.py
# Both CLI and API available
```

### 🔧 Configuration

Environment variables in `.env`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here

# Firecrawl Configuration (for web search)
FIRECRAWL_API_KEY=fc-your-key-here

# Model Configuration
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo

# Vector Database Configuration
QDRANT_PATH=./qdrant_data
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=documents
```

### 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   CLI Mode      │    │   API Mode      │
│   (CrewAI)      │    │   (FastAPI)     │
└────────┬────────┘    └────────┬────────┘
         │                     │
         ▼                     ▼
┌─────────────────────────────────────┐
│         Qdrant Vector DB           │
│    (Shared Document Storage)        │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│        OpenAI LLM & Embeddings       │
└─────────────────────────────────────┘
```

### 📊 Features

✅ **Dual Architecture** - CLI + REST API
✅ **Multi-Agent System** - CrewAI for CLI mode
✅ **Production Ready** - FastAPI with auto-docs
✅ **Hybrid Search** - Local docs + web fallback
✅ **Multiple Formats** - PDF, TXT, DOCX, MD support
✅ **Docker Support** - Full containerization

### 🌐 API Endpoints

```bash
# Upload document
POST /upload
Content-Type: multipart/form-data

# Query documents
POST /query
{
  "question": "What is RAG?",
  "top_k": 3
}

# List documents
GET /documents

# Delete document
DELETE /documents/{id}

# Clear all
POST /clear

# Health check
GET /health
```

### 🐛 Troubleshooting

#### OpenAI API Errors

- Verify API key is set correctly in `.env`
- Check API quota and billing
- Ensure internet connection

#### Qdrant Connection Issues

```bash
# Check if Qdrant is running
curl http://localhost:6333/collections

# Start Qdrant with Docker
docker-compose up qdrant
```

#### Dependency Conflicts

```bash
# Reinstall with specific versions
pip install --force-reinstall -r cloud/requirements.txt
```

### 🐳 Docker Deployment

```bash
# Development
docker-compose up --build

# Production
docker-compose --profile production up -d
```

### 📚 Example Queries

```
"What is RAG and how does it work?"
"Explain the concept of vector databases"
"What are the latest developments in LLMs?" (uses web search)
"Summarize key points from uploaded document"
```

### 🔒 Privacy Note

Document processing and vector storage can be local or remote. LLM processing uses OpenAI cloud API. Web search uses Firecrawl when local documents don't have answers.
