# LLM/SLM Training Guide for RAG System

## 🎯 Purpose

This guide explains how to use the modular RAG system files for training Large Language Models (LLMs) and Small Language Models (SLMs).

## 📁 Modular File Structure

### Core Modules (Perfect for Training)

#### 1. **cloud/config.py** - Configuration Management

```python
# Key concepts for training:
- Environment variable handling
- Directory management
- Configuration validation
- Default value management
```

#### 2. **cloud/vector_db.py** - Vector Database Operations

```python
# Training concepts:
- Vector similarity search
- Document indexing
- Collection management
- Embedding storage and retrieval
```

#### 3. **cloud/embeddings.py** - Text Embedding Generation

```python
# Training concepts:
- Multiple embedding providers (OpenAI, Ollama)
- Text vectorization
- Embedding dimension management
- Provider switching
```

#### 4. **cloud/llm.py** - Language Model Operations

```python
# Training concepts:
- Multiple LLM providers
- Response generation
- Prompt engineering
- Context-based answering
```

#### 5. **cloud/document_processor.py** - Document Handling

```python
# Training concepts:
- Multi-format document parsing
- Text chunking strategies
- Metadata extraction
- File processing pipelines
```

#### 6. **cloud/web_search.py** - Web Integration

```python
# Training concepts:
- Web search APIs
- Content scraping
- Result formatting
- Fallback mechanisms
```

#### 7. **cloud/crewai_agents.py** - Multi-Agent System

```python
# Training concepts:
- Agent orchestration
- Tool usage
- Task decomposition
- Collaborative AI systems
```

#### 8. **cloud/api.py** - REST API Implementation

```python
# Training concepts:
- FastAPI patterns
- File upload handling
- Error management
- API design principles
```

#### 9. **cloud/cli.py** - Command Line Interface

```python
# Training concepts:
- Interactive programming
- Command parsing
- User experience design
- Error handling
```

## 🎓 Training Use Cases

### 1. **Code Generation Training**

- **Files**: All modules
- **Focus**: Modular architecture patterns
- **Prompts**: "Generate a RAG system with modular components"

### 2. **API Development Training**

- **Files**: api.py, config.py
- **Focus**: FastAPI best practices
- **Prompts**: "Create a document processing API with upload and query endpoints"

### 3. **AI Agent Training**

- **Files**: crewai_agents.py, llm.py
- **Focus**: Multi-agent systems
- **Prompts**: "Build a multi-agent RAG system with retriever and response agents"

### 4. **Vector Database Training**

- **Files**: vector_db.py, embeddings.py
- **Focus**: Vector similarity and storage
- **Prompts**: "Implement a vector database for document search"

### 5. **Document Processing Training**

- **Files**: document_processor.py
- **Focus**: Multi-format file handling
- **Prompts**: "Create a document processor for PDF, TXT, DOCX, and MD files"

## 🔍 Training Prompts by Module

### Configuration Module

```
"Generate a Python configuration class that handles environment variables,
directory creation, and validation for a RAG system"
```

### Vector Database Module

```
"Create a vector database wrapper class that supports both local and remote
Qdrant instances with document indexing and similarity search"
```

### Embeddings Module

```
"Implement an embedding manager that supports multiple providers (OpenAI, Ollama)
with provider switching and dimension detection"
```

### LLM Module

```
"Build an LLM manager that supports multiple providers with context-based
response generation and prompt engineering"
```

### Document Processor Module

```
"Create a document processor that handles PDF, TXT, DOCX, and MD files with
text extraction, chunking, and metadata management"
```

### Web Search Module

```
"Implement a web search manager using Firecrawl API with result formatting
and URL scraping capabilities"
```

### CrewAI Agents Module

```
"Build a multi-agent RAG system using CrewAI with retriever and response
agents, tool usage, and task orchestration"
```

### API Module

```
"Create a FastAPI application for document upload, processing, and querying
with proper error handling and CORS configuration"
```

### CLI Module

```
"Build an interactive CLI application for a RAG system with command parsing,
document ingestion, and query processing"
```

## 📊 Training Data Structure

### Input Format for Training

```
Module: config.py
Purpose: Configuration management
Key Concepts: Environment variables, validation, defaults
Dependencies: python-dotenv, pathlib
Use Cases: Settings management, API keys, directory setup
```

### Output Format for Training

```
Generated Code:
- Class-based architecture
- Error handling patterns
- Type hints and docstrings
- Configuration validation
- Environment variable loading
```

## 🎯 Training Objectives

### For LLMs (Large Models)

- **Complexity**: Full system architecture
- **Context**: Entire codebase relationships
- **Output**: Production-ready applications
- **Focus**: Integration and best practices

### For SLMs (Small Models)

- **Complexity**: Single module at a time
- **Context**: Specific functionality
- **Output**: Modular components
- **Focus**: Core concepts and patterns

## 📈 Progressive Training Path

### Level 1: Basic Components

1. config.py - Configuration patterns
2. embeddings.py - Text vectorization
3. llm.py - Basic LLM usage

### Level 2: Data Processing

4. document_processor.py - File handling
5. vector_db.py - Storage operations
6. web_search.py - External APIs

### Level 3: System Integration

7. crewai_agents.py - Multi-agent systems
8. api.py - REST interfaces
9. cli.py - User interfaces

### Level 4: Full Application

10. main.py - Application orchestration
11. Integration patterns
12. Error handling and logging

## 🔧 Training Tips

### For Code Generation

- Use specific module names in prompts
- Include dependency requirements
- Specify error handling needs
- Mention integration points

### For Architecture Understanding

- Focus on module relationships
- Explain data flow
- Highlight design patterns
- Emphasize modularity benefits

### For Best Practices

- Include type hints
- Add comprehensive docstrings
- Implement proper error handling
- Follow Python conventions

## 📝 Example Training Session

### Prompt

```
"Generate a Python module for document processing that handles PDF, TXT, DOCX,
and MD files. Include text extraction, chunking, metadata management, and
error handling. Use the document_processor.py as a reference."
```

### Expected Output

- Complete module implementation
- Proper error handling
- Type hints and documentation
- Integration with other modules
- Test cases and examples

This modular structure provides perfect training material for both LLMs and SLMs, with clear separation of concerns and progressive complexity levels.
