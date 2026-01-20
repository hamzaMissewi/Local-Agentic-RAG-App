# 🚀 Integrated RAG Application

A comprehensive Retrieval-Augmented Generation (RAG) system that combines multiple AI frameworks for maximum flexibility and power.

## 🎯 Features

### 🤖 Dual Architecture

- **CrewAI CLI Interface**: Multi-agent system with web search fallback
- **FastAPI Backend**: RESTful API with LlamaIndex integration
- **Shared Vector Database**: Both systems use the same Qdrant instance

### 🛠️ Technology Stack

- **AI Frameworks**: CrewAI, LlamaIndex, LangChain
- **LLM**: OpenAI (GPT-3.5/4)
- **Vector Database**: Qdrant
- **Web Search**: Firecrawl
- **Backend**: FastAPI
- **Frontend**: Next.js (included)
- **Containerization**: Docker & Docker Compose

### 📚 Document Processing

- PDF, TXT, DOCX, MD support
- Automatic chunking and embedding
- Metadata tracking
- Batch processing

## 🏗️ Architecture

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

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Update with your API keys
# OPENAI_API_KEY=sk-your-key-here
# FIRECRAWL_API_KEY=fc-your-key-here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

#### CLI Mode (CrewAI)

```bash
python index_integrated.py cli
```

#### API Mode (FastAPI)

```bash
python index_integrated.py
# or
uvicorn index_integrated:app --reload
```

#### Docker Mode

```bash
docker-compose up --build
```

## 📖 Usage

### CLI Mode Features

- **Interactive Chat**: Ask questions about your documents
- **Web Search**: Automatic fallback when local docs don't have answers
- **Document Ingestion**: `ingest <pdf_path>` command
- **Multi-Agent Processing**: CrewAI agents for retrieval and response generation

### API Mode Features

- **REST Endpoints**: Full CRUD operations for documents
- **File Upload**: Multi-format document processing
- **Query Engine**: LlamaIndex-based retrieval
- **Health Checks**: System monitoring

#### API Endpoints

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

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here

# Firecrawl (for web search)
FIRECRAWL_API_KEY=fc-your-key-here

# Model Configuration
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo

# Vector Database
QDRANT_PATH=./qdrant_data
QDRANT_URL=http://localhost:6333
COLLECTION_NAME=documents
```

### Directory Structure

```
.
├── index_integrated.py      # Main application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── uploads/               # Uploaded documents
├── documents/             # CLI documents folder
├── qdrant_data/           # Local vector storage
├── frontend/              # Next.js frontend
├── Dockerfile             # Container definition
├── docker-compose.yml     # Multi-service setup
└── README.md              # This file
```

## 🐳 Docker Deployment

### Development

```bash
docker-compose up --build
```

### Production

```bash
docker-compose --profile production up -d
```

### Services

- **rag-app**: Main application (port 8000)
- **qdrant**: Vector database (port 6333)
- **frontend**: Next.js UI (port 3000)

## 🎯 Use Cases

### 📚 Research Assistant

- Upload academic papers
- Ask complex questions
- Get cited responses with sources

### 💼 Business Intelligence

- Process company documents
- Query internal knowledge base
- Generate reports and summaries

### 🎓 Educational Tool

- Upload course materials
- Student Q&A system
- Personalized learning assistance

## 🔍 Comparison

| Feature     | CLI Mode     | API Mode      |
| ----------- | ------------ | ------------- |
| Interface   | Terminal     | REST API      |
| Framework   | CrewAI       | LlamaIndex    |
| Web Search  | ✅ Firecrawl | ❌ Local only |
| Multi-Agent | ✅           | ❌            |
| File Upload | Manual       | ✅ Multipart  |
| Frontend    | ❌           | ✅ Next.js    |
| Production  | ❌           | ✅            |

## 🛠️ Development

### Adding New Features

1. **CLI**: Modify CrewAI agents and tools
2. **API**: Add FastAPI endpoints
3. **Shared**: Update Qdrant schema

### Testing

```bash
# Test CLI
python index_integrated.py cli

# Test API
curl http://localhost:8000/health

# Test with Docker
docker-compose exec rag-app python -c "import crewai; print('OK')"
```

## 🔒 Security

- **API Keys**: Stored in environment variables
- **File Upload**: Type validation and size limits
- **CORS**: Configured for frontend
- **Docker**: Non-root user execution

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**

   ```bash
   # Check .env file
   cat .env | grep OPENAI_API_KEY
   ```

2. **Qdrant Connection**

   ```bash
   # Check if Qdrant is running
   curl http://localhost:6333/collections
   ```

3. **Import Errors**

   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

4. **Docker Issues**
   ```bash
   # Clean rebuild
   docker-compose down -v
   docker-compose build --no-cache
   ```

## 📝 License

MIT License - feel free to use this project for your own RAG applications!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- 📧 Issues: Use GitHub Issues
- 📖 Documentation: Check the inline comments
- 🐳 Docker: Refer to Docker Guide
- 🔧 API: Visit `/docs` endpoint

---

**Built with ❤️ using CrewAI, LlamaIndex, FastAPI, and Qdrant**
