"""
Integrated RAG Application - Main Entry Point
Imports and orchestrates all modular components from cloud folder
"""

import sys
from pathlib import Path

# Add cloud folder to Python path
cloud_path = Path(__file__).parent / "cloud"
sys.path.insert(0, str(cloud_path))

# Import all modular components
from config import Config
from document_processor import DocumentProcessor
from vector_db import VectorDatabase
from embeddings import EmbeddingManager
from llm import LLMManager
from web_search import WebSearchManager
from crewai_agents import CrewAIRAGSystem
from api import app as fastapi_app
from cli import RAGCLI

class IntegratedRAGSystem:
    """Main integrated RAG system that combines all components"""
    
    def __init__(self):
        """Initialize the complete RAG system"""
        print("🚀 Initializing Integrated RAG System...")
        
        # Validate configuration
        errors = Config.validate_config()
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            sys.exit(1)
        
        # Create directories
        Config.create_directories()
        
        # Initialize core components
        self.doc_processor = DocumentProcessor()
        self.vector_db_local = VectorDatabase(use_local=True)
        self.vector_db_remote = VectorDatabase(use_local=False)
        self.embedding_manager = EmbeddingManager("openai")
        self.llm_manager = LLMManager("openai")
        self.web_search = WebSearchManager()
        
        # Initialize specialized systems
        self.crewai_system = CrewAIRAGSystem("openai", use_local_db=True)
        self.cli_system = RAGCLI()
        
        # Initialize vector databases
        vector_size = self.embedding_manager.get_embedding_dimension()
        self.vector_db_local.initialize_collection(vector_size)
        self.vector_db_remote.initialize_collection(vector_size)
        
        print("✅ Integrated RAG System initialized successfully")
    
    def get_system_status(self):
        """Get comprehensive system status"""
        return {
            "configuration": {
                "embedding_model": Config.EMBEDDING_MODEL,
                "llm_model": Config.LLM_MODEL,
                "qdrant_path": Config.QDRANT_PATH,
                "qdrant_url": Config.QDRANT_URL
            },
            "components": {
                "document_processor": "✅ Ready",
                "vector_db_local": "✅ Ready",
                "vector_db_remote": "✅ Ready", 
                "embedding_manager": f"✅ {self.embedding_manager.provider_name}",
                "llm_manager": f"✅ {self.llm_manager.provider_name}",
                "web_search": "✅ Ready" if self.web_search.is_available() else "⚠️ Not Available",
                "crewai_system": "✅ Ready",
                "cli_system": "✅ Ready"
            },
            "databases": {
                "local": self.vector_db_local.get_collection_info(),
                "remote": self.vector_db_remote.get_collection_info()
            }
        }
    
    def run_cli_mode(self):
        """Run CLI mode"""
        print("\n🤖 Starting CLI Mode...")
        self.cli_system.run_interactive_loop()
    
    def run_api_mode(self):
        """Run API mode"""
        print("\n🌐 Starting API Mode...")
        import uvicorn
        print(f"   API: http://{Config.API_HOST}:{Config.API_PORT}")
        print(f"   Docs: http://{Config.API_HOST}:{Config.API_PORT}/docs")
        uvicorn.run(fastapi_app, host=Config.API_HOST, port=Config.API_PORT)
    
    def show_status(self):
        """Display system status"""
        status = self.get_system_status()
        
        print("\n" + "="*60)
        print("📊 INTEGRATED RAG SYSTEM STATUS")
        print("="*60)
        
        print("\n🔧 Configuration:")
        for key, value in status["configuration"].items():
            print(f"   {key}: {value}")
        
        print("\n🧩 Components:")
        for key, value in status["components"].items():
            print(f"   {key}: {value}")
        
        print("\n🗄️  Databases:")
        for db_type, info in status["databases"].items():
            print(f"   {db_type.upper()}:")
            if info:
                for key, value in info.items():
                    print(f"     {key}: {value}")
            else:
                print("     Not initialized")

def main():
    """Main entry point"""
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode in ['cli', 'command', 'interactive']:
            system = IntegratedRAGSystem()
            system.run_cli_mode()
        elif mode in ['api', 'server', 'web']:
            system = IntegratedRAGSystem()
            system.run_api_mode()
        elif mode in ['status', 'info']:
            system = IntegratedRAGSystem()
            system.show_status()
        elif mode in ['help', '--help', '-h']:
            show_help()
        else:
            print(f"❌ Unknown mode: {mode}")
            show_help()
            sys.exit(1)
    else:
        # Default: show status and ask for mode
        system = IntegratedRAGSystem()
        system.show_status()
        
        print("\n" + "="*60)
        print("🚀 SELECT MODE:")
        print("1. CLI Mode (Interactive)")
        print("2. API Mode (Web Server)")
        print("3. Show Status")
        print("4. Exit")
        print("="*60)
        
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                system.run_cli_mode()
            elif choice == "2":
                system.run_api_mode()
            elif choice == "3":
                system.show_status()
            elif choice == "4":
                print("\n👋 Goodbye!")
            else:
                print("❌ Invalid choice")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")

def show_help():
    """Show help information"""
    help_text = """
🤖 Integrated RAG Application - Help

📋 Usage:
  python index.py [mode]

🎯 Modes:
  cli, command, interactive    - Run CLI interface
  api, server, web           - Run API server
  status, info              - Show system status
  help, --help, -h          - Show this help

📁 Examples:
  python index.py cli          # Start CLI mode
  python index.py api          # Start API server
  python index.py status       # Show system status
  python index.py              # Interactive mode selection

🧩 Components:
  - Config: Environment and settings management
  - Document Processor: Multi-format file handling
  - Vector Database: Local and remote Qdrant storage
  - Embeddings: OpenAI text vectorization
  - LLM: OpenAI language model integration
  - Web Search: Firecrawl web integration
  - CrewAI Agents: Multi-agent RAG system
  - API: FastAPI REST interface
  - CLI: Interactive command-line interface

🔧 Configuration:
  - Edit cloud/config.py for settings
  - Set environment variables in .env file
  - Ensure API keys are configured

📚 Documentation:
  - API docs: http://localhost:8000/docs
  - Training guide: cloud/TRAINING_GUIDE.md
    """
    print(help_text)

if __name__ == "__main__":
    main()
