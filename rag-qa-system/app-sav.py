from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
import uuid
from pathlib import Path
import shutil
from typing import Optional
import asyncio

# Create FastAPI app
app = FastAPI(title="RAG Document Q&A System", version="1.0.0")

# Serve static files (CSS, JS, HTML)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Store uploaded files info (in production, use a database)
uploaded_files = {}

class QueryRequest(BaseModel):
    query: str
    file_id: str

class QueryResponse(BaseModel):
    answer: str
    file_name: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Please make sure index.html is in the static/ directory</h1>")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload and basic processing"""
    
    # Validate file type
    allowed_types = {
        "application/pdf": ".pdf",
        "application/msword": ".doc", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "text/plain": ".txt"
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed types: {list(allowed_types.values())}"
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    # Create file path
    file_extension = allowed_types[file.content_type]
    file_path = UPLOAD_DIR / f"{file_id}{file_extension}"
    
    try:
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store file info
        uploaded_files[file_id] = {
            "original_name": file.filename,
            "file_path": str(file_path),
            "content_type": file.content_type,
            "processed": False
        }
        
        # In a real RAG system, you'd process the document here:
        # - Extract text from PDF/DOC
        # - Split into chunks
        # - Create embeddings
        # - Store in vector database
        
        # For now, we'll simulate processing
        await simulate_document_processing(file_id)
        
        return JSONResponse({
            "status": "success",
            "message": f"File '{file.filename}' uploaded successfully!",
            "file_id": file_id,
            "file_name": file.filename
        })
        
    except Exception as e:
        # Clean up file if something went wrong
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@app.post("/api/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """Process queries against uploaded documents"""
    
    if request.file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[request.file_id]
    
    if not file_info["processed"]:
        raise HTTPException(status_code=400, detail="File is still being processed")
    
    # In a real RAG system, you'd:
    # 1. Convert query to embeddings
    # 2. Search vector database for relevant chunks
    # 3. Use LLM to generate answer based on retrieved context
    
    # For demo purposes, we'll simulate this
    answer = await simulate_rag_query(request.query, file_info)
    
    return QueryResponse(
        answer=answer,
        file_name=file_info["original_name"]
    )

@app.get("/api/files")
async def list_files():
    """List all uploaded files"""
    return {
        "files": [
            {
                "file_id": file_id,
                "name": info["original_name"],
                "processed": info["processed"]
            }
            for file_id, info in uploaded_files.items()
        ]
    }

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete an uploaded file"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = uploaded_files[file_id]
    
    # Delete file from disk
    file_path = Path(file_info["file_path"])
    if file_path.exists():
        file_path.unlink()
    
    # Remove from memory
    del uploaded_files[file_id]
    
    return {"status": "success", "message": "File deleted successfully"}

async def simulate_document_processing(file_id: str):
    """Simulate document processing (chunking, embedding, etc.)"""
    # In a real system, you'd use libraries like:
    # - PyPDF2 or pdfplumber for PDFs
    # - python-docx for Word docs
    # - langchain for text splitting
    # - sentence-transformers for embeddings
    # - chromadb or pinecone for vector storage
    
    await asyncio.sleep(1)  # Simulate processing time
    uploaded_files[file_id]["processed"] = True

async def simulate_rag_query(query: str, file_info: dict) -> str:
    """Simulate RAG query processing"""
    # In a real system, you'd use:
    # - OpenAI API, Anthropic, or local LLM
    # - Vector similarity search
    # - Prompt engineering for better responses
    
    await asyncio.sleep(0.5)  # Simulate processing time
    
    # Demo response based on file type and query
    file_name = file_info["original_name"]
    
    responses = [
        f"Based on your document '{file_name}', here's what I found regarding your query: '{query}'",
        f"Great question! After analyzing '{file_name}', I can tell you that...",
        f"Looking at the content in '{file_name}', the answer to '{query}' appears to be...",
    ]
    
    import random
    base_response = random.choice(responses)
    
    # Add some motivational message as mentioned in the original
    motivation = "\n\n✨ Keep up the great work! Every step forward is progress! ✨"
    
    return base_response + "\n\n[This is a demo response. In a real RAG system, this would contain actual content from your document.]" + motivation

if __name__ == "__main__":
    import uvicorn
    print("Starting RAG Document Q&A System...")
    print("Make sure to:")
    print("1. Create a 'static' directory")
    print("2. Place index.html and styles.css in the static directory")
    print("3. Install required packages: pip install fastapi uvicorn python-multipart")
    uvicorn.run(app, host="0.0.0.0", port=7869, reload=True)
