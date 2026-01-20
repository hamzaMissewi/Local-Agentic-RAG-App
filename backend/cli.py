"""
CLI Application Module
Command-line interface for RAG system
"""

import sys
from pathlib import Path
from config import Config
from document_processor import DocumentProcessor
from crewai_agents import CrewAIRAGSystem

class RAGCLI:
    """Command-line interface for RAG system"""
    
    def __init__(self):
        """Initialize CLI application"""
        # Validate configuration
        errors = Config.validate_config()
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            sys.exit(1)
        
        # Create directories
        Config.create_directories()
        
        # Initialize components
        self.doc_processor = DocumentProcessor()
        self.crewai_system = CrewAIRAGSystem("openai", use_local_db=True)
        
        print("🚀 Local Agentic RAG System initialized successfully")
    
    def ingest_document(self, file_path: str) -> bool:
        """
        Ingest a document into the RAG system
        
        Args:
            file_path: Path to the document file
            
        Returns:
            bool: True if successful
        """
        path = Path(file_path)
        
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        if not path.suffix.lower() in {".pdf", ".txt", ".docx", ".md"}:
            print(f"❌ Unsupported file format: {path.suffix}")
            return False
        
        try:
            print(f"\n📄 Processing document: {file_path}")
            
            # Process document
            result = self.doc_processor.process_document(path, "cli_doc", path.name)
            
            if not result["success"]:
                print(f"❌ Processing failed: {result['error']}")
                return False
            
            # Add to vector database
            success = self.crewai_system.add_documents(result["chunks"], result["metadata"])
            
            if success:
                print(f"✅ Successfully ingested {result['total_chunks']} chunks from {file_path}")
                return True
            else:
                print("❌ Failed to add documents to vector database")
                return False
                
        except Exception as e:
            print(f"❌ Ingestion failed: {e}")
            return False
    
    def ingest_documents_from_folder(self, folder_path: str = "./documents") -> int:
        """
        Ingest all documents from a folder
        
        Args:
            folder_path: Path to the documents folder
            
        Returns:
            Number of documents ingested
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            print(f"⚠️  Documents folder not found: {folder_path}")
            return 0
        
        ingested_count = 0
        supported_formats = {".pdf", ".txt", ".docx", ".md"}
        
        for file_path in folder.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                if self.ingest_document(str(file_path)):
                    ingested_count += 1
        
        if ingested_count > 0:
            print(f"✅ Successfully ingested {ingested_count} documents from {folder_path}")
        else:
            print(f"⚠️  No supported documents found in {folder_path}")
        
        return ingested_count
    
    def query_system(self, user_query: str) -> str:
        """
        Query the RAG system
        
        Args:
            user_query: User's question
            
        Returns:
            Generated response
        """
        if not user_query.strip():
            return "Please provide a valid query."
        
        try:
            print("\n🤖 Processing your query...")
            response = self.crewai_system.query(user_query)
            return response
        except Exception as e:
            return f"❌ Query failed: {str(e)}"
    
    def show_system_info(self):
        """Display system information"""
        info = self.crewai_system.get_system_info()
        
        print("\n📊 System Information:")
        print(f"   Embedding Provider: {info['embedding_provider']}")
        print(f"   Vector Database: {info['vector_db_type']}")
        print(f"   Web Search: {'Available' if info['web_search_available'] else 'Not Available'}")
        
        collection_info = info.get('collection_info', {})
        if collection_info:
            print(f"   Documents: {collection_info.get('points_count', 0)}")
            print(f"   Vector Size: {collection_info.get('vector_size', 'N/A')}")
    
    def show_help(self):
        """Display help information"""
        help_text = """
🤖 Local Agentic RAG System - Help

📋 Commands:
  help                    - Show this help message
  info                    - Show system information
  ingest <file_path>      - Ingest a single document
  ingest_folder <path>    - Ingest all documents from folder
  quit                    - Exit the application

💬 Usage:
  - Type your question directly to query the system
  - Use commands with the format: command [arguments]

📁 Supported Formats:
  PDF, TXT, DOCX, MD files

🔍 Search Strategy:
  1. Local document search first
  2. Web search fallback if needed

⚙️ Configuration:
  Edit config.py to modify settings
  Set environment variables in .env file
        """
        print(help_text)
    
    def run_interactive_loop(self):
        """Run the interactive CLI loop"""
        print("\n" + "="*60)
        print("📚 Local Agentic RAG System Ready!")
        print("="*60)
        print("\nCommands:")
        print("  - Type your question to search")
        print("  - Type 'help' for commands")
        print("  - Type 'quit' to exit")
        print("="*60 + "\n")
        
        # Auto-ingest documents from default folder
        self.ingest_documents_from_folder()
        
        while True:
            try:
                user_input = input("\n🔍 Your query: ").strip()
                
                if not user_input:
                    continue
                
                # Parse commands
                if user_input.lower() == 'quit':
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if user_input.lower() == 'info':
                    self.show_system_info()
                    continue
                
                if user_input.lower().startswith('ingest '):
                    file_path = user_input[7:].strip()
                    self.ingest_document(file_path)
                    continue
                
                if user_input.lower().startswith('ingest_folder '):
                    folder_path = user_input[13:].strip() or "./documents"
                    self.ingest_documents_from_folder(folder_path)
                    continue
                
                # Regular query
                response = self.query_system(user_input)
                print("\n" + "="*60)
                print("📝 RESPONSE:")
                print("="*60)
                print(response)
                print("="*60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

def main():
    """Main entry point for CLI application"""
    try:
        cli = RAGCLI()
        cli.run_interactive_loop()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
