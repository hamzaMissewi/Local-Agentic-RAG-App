#!/usr/bin/env python3
"""
Test script for Local Agentic RAG Application
"""

import sys
import os

def test_ollama():
    """Test Ollama installation and model"""
    print("🦙 Testing Ollama...")
    
    try:
        from langchain_community.llms import Ollama
        from langchain_community.embeddings import OllamaEmbeddings
        
        # Test LLM
        llm = Ollama(model="llama3.2", temperature=0.7)
        response = llm.invoke("Hello")
        print("✅ Ollama LLM connection successful")
        
        # Test Embeddings
        embeddings = OllamaEmbeddings(model="llama3.2")
        embedding = embeddings.embed_query("test")
        print(f"✅ Ollama Embeddings working (dimension: {len(embedding)})")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Make sure Ollama is running with: ollama serve")
        return False

def test_dependencies():
    """Test all required dependencies"""
    print("📦 Testing Dependencies...")
    
    dependencies = [
        ("crewai", "crewai"),
        ("crewai_tools", "crewai_tools"),
        ("langchain_community", "langchain_community"),
        ("qdrant_client", "qdrant-client"),
        ("firecrawl", "firecrawl-py"),
        ("PyPDF2", "PyPDF2"),
    ]
    
    all_ok = True
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {package_name} imported successfully")
        except ImportError as e:
            print(f"❌ {package_name} import failed: {e}")
            all_ok = False
    
    return all_ok

def test_firecrawl():
    """Test Firecrawl API"""
    print("🔥 Testing Firecrawl...")
    
    try:
        from firecrawl import FirecrawlApp
        api_key = os.getenv("FIRECRAWL_API_KEY")
        
        if not api_key:
            print("⚠️  FIRECRAWL_API_KEY not set")
            return False
        
        firecrawl = FirecrawlApp(api_key=api_key)
        # Test a simple search
        results = firecrawl.search("test", limit=1)
        print("✅ Firecrawl API connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Firecrawl test failed: {e}")
        return False

def test_qdrant():
    """Test Qdrant connection"""
    print("🗄️  Testing Qdrant...")
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        
        client = QdrantClient(path="./qdrant_data")
        collections = client.get_collections()
        print(f"✅ Qdrant connection successful (collections: {len(collections.collections)})")
        return True
        
    except Exception as e:
        print(f"❌ Qdrant test failed: {e}")
        return False

def test_directories():
    """Test required directories"""
    print("📁 Testing Directories...")
    
    from pathlib import Path
    
    required_dirs = ["documents", "qdrant_data"]
    all_ok = True
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"⚠️  {dir_name}/ directory missing")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    print("🔍 Testing Local Agentic RAG Application")
    print("=" * 50)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not installed, skipping .env loading")
    except Exception as e:
        print(f"⚠️  Failed to load .env: {e}")
    
    results = {
        "Dependencies": test_dependencies(),
        "Ollama": test_ollama(),
        "Qdrant": test_qdrant(),
        "Firecrawl": test_firecrawl(),
        "Directories": test_directories(),
    }
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Local Agentic RAG is ready!")
        print("\n🚀 Run: python agentic_rag.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("\n🔧 Fixes:")
        print("1. Install dependencies: pip install -r requirements_original.txt")
        print("2. Install Ollama: https://ollama.com/download")
        print("3. Pull model: ollama pull llama3.2")
        print("4. Start Ollama: ollama serve")
        print("5. Update .env file with FIRECRAWL_API_KEY")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
