"""
Document Processing Module
Handles PDF, TXT, DOCX, and MD file processing
"""

import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
import python_docx
from config import Config

class DocumentProcessor:
    """Handles document ingestion and processing"""
    
    def __init__(self):
        self.upload_dir = Config.UPLOAD_DIR
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> tuple[str, Path]:
        """
        Save uploaded file to disk
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            tuple: (document_id, file_path)
        """
        doc_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{doc_id}_{filename}"
        
        with file_path.open("wb") as buffer:
            buffer.write(file_content)
        
        return doc_id, file_path
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"❌ PDF extraction failed: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            doc = python_docx.Document(str(file_path))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"❌ DOCX extraction failed: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"❌ TXT extraction failed: {e}")
            return ""
    
    def extract_text_from_md(self, file_path: Path) -> str:
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"❌ MD extraction failed: {e}")
            return ""
    
    def extract_text(self, file_path: Path) -> str:
        """
        Extract text from various file formats
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Extracted text
        """
        file_ext = file_path.suffix.lower()
        
        if file_ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_ext == ".docx":
            return self.extract_text_from_docx(file_path)
        elif file_ext == ".txt":
            return self.extract_text_from_txt(file_path)
        elif file_ext == ".md":
            return self.extract_text_from_md(file_path)
        else:
            print(f"❌ Unsupported file format: {file_ext}")
            return ""
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Input text
            
        Returns:
            List of text chunks
        """
        if not text.strip():
            return []
        
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size):
            chunk = " ".join(words[i:i + self.chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def process_document(self, file_path: Path, document_id: str, filename: str) -> Dict[str, Any]:
        """
        Process a document and return chunks with metadata
        
        Args:
            file_path: Path to the file
            document_id: Unique document identifier
            filename: Original filename
            
        Returns:
            Dict with processed document data
        """
        # Extract text
        text = self.extract_text(file_path)
        
        if not text:
            return {
                "success": False,
                "error": "Failed to extract text from document"
            }
        
        # Chunk text
        chunks = self.chunk_text(text)
        
        if not chunks:
            return {
                "success": False,
                "error": "No text chunks created"
            }
        
        # Create metadata for each chunk
        metadata_list = []
        for idx, chunk in enumerate(chunks):
            metadata = {
                "document_id": document_id,
                "filename": filename,
                "chunk_id": idx,
                "source": str(file_path),
                "total_chunks": len(chunks)
            }
            metadata_list.append(metadata)
        
        return {
            "success": True,
            "chunks": chunks,
            "metadata": metadata_list,
            "total_chunks": len(chunks)
        }
    
    def delete_document_files(self, document_id: str) -> bool:
        """
        Delete all files associated with a document
        
        Args:
            document_id: Document identifier
            
        Returns:
            bool: True if files were deleted
        """
        deleted = False
        for file_path in self.upload_dir.glob(f"{document_id}_*"):
            file_path.unlink()
            deleted = True
        return deleted
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents"""
        documents = []
        
        for file_path in self.upload_dir.glob("*"):
            if file_path.is_file():
                parts = file_path.name.split("_", 1)
                if len(parts) == 2:
                    doc_id, filename = parts
                    documents.append({
                        "id": doc_id,
                        "filename": filename,
                        "size": file_path.stat().st_size,
                        "upload_date": file_path.stat().st_mtime
                    })
        
        return documents
