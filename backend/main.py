"""
Main Entry Point
Unified entry point for both CLI and API modes
"""

import sys
from pathlib import Path

def run_cli_mode():
    """Run CLI mode"""
    try:
        from cli import main
        main()
    except ImportError as e:
        print(f"❌ Failed to import CLI module: {e}")
        sys.exit(1)

def run_api_mode():
    """Run API mode"""
    try:
        from api import app
        import uvicorn
        from config import Config
        
        print(f"🚀 Starting RAG API Server...")
        print(f"   API: http://{Config.API_HOST}:{Config.API_PORT}")
        print(f"   Docs: http://{Config.API_HOST}:{Config.API_PORT}/docs")
        
        uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
    except ImportError as e:
        print(f"❌ Failed to import API module: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode in ['cli', 'command', 'interactive']:
            run_cli_mode()
        elif mode in ['api', 'server', 'web']:
            run_api_mode()
        elif mode in ['help', '--help', '-h']:
            show_help()
        else:
            print(f"❌ Unknown mode: {mode}")
            show_help()
            sys.exit(1)
    else:
        # Default: run API mode
        run_api_mode()

def show_help():
    """Show help information"""
    help_text = """
🤖 RAG Application - Help

📋 Usage:
  python main.py [mode]

🎯 Modes:
  cli, command, interactive    - Run CLI interface
  api, server, web           - Run API server (default)
  help, --help, -h           - Show this help

📁 Examples:
  python main.py cli          # Start CLI mode
  python main.py api          # Start API server
  python main.py              # Start API server (default)

🔧 Configuration:
  - Edit config.py for settings
  - Set environment variables in .env file
  - Ensure API keys are configured

📚 Documentation:
  - API docs: http://localhost:8000/docs
  - Setup guides: docs/ folder
    """
    print(help_text)

if __name__ == "__main__":
    main()
