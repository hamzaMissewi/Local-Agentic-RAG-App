@REM .\setup.bat

@REM what script does:
@REM ✅ Check Ollama installation
@REM 🔥 Start Ollama service if needed
@REM 📥 Pull Llama 3.2 model
@REM 🐍 Create Python virtual environment
@REM 📦 Install dependencies
@REM 📁 Create directories (documents, qdrant_data)
@REM ⚙️ Setup environment file

@echo off
echo 🚀 Setting up Local Agentic RAG Application
echo ==========================================

REM Check if Ollama is installed
echo 📋 Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama is not installed
    echo Please install Ollama from https://ollama.com/download
    pause
    exit /b 1
)
echo ✅ Ollama is installed

REM Check if Ollama is running
echo 📋 Checking Ollama service...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Ollama service is not running
    echo Starting Ollama service...
    start "Ollama" ollama serve
    timeout /t 10 /nobreak >nul
)
echo ✅ Ollama service is running

REM Pull Llama 3.2 model
echo 📋 Checking Llama 3.2 model...
ollama list | findstr "llama3.2" >nul
if %errorlevel% neq 0 (
    echo 📥 Pulling Llama 3.2 model...
    ollama pull llama3.2
) else (
    echo ✅ Llama 3.2 model is available
)

REM Create virtual environment
echo 📋 Setting up Python environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 📋 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📋 Installing Python dependencies...
pip install -r requirements_original.txt

REM Create necessary directories
echo 📋 Creating directories...
if not exist "documents" mkdir documents
if not exist "qdrant_data" mkdir qdrant_data

REM Setup environment file
echo 📋 Setting up environment...
if not exist ".env" (
    copy .env_original .env
    echo ✅ Created .env file from template
    echo ⚠️  Please update your FIRECRAWL_API_KEY in .env file
)

echo.
echo 🎉 Setup complete!
echo.
echo 📚 Next steps:
echo 1. Update your FIRECRAWL_API_KEY in .env file
echo 2. Add PDF files to the 'documents' folder
echo 3. Run the application: python agentic_rag.py
echo.
echo 🔗 Useful links:
echo - Ollama: https://ollama.com
echo - Firecrawl: https://firecrawl.dev
echo.
pause
