#!/usr/bin/env python3
"""
Debug script to check RAG system setup
"""

import os
from pathlib import Path

def check_setup():
    """Check if everything is set up correctly"""
    print("🔍 RAG System Setup Diagnostic")
    print("=" * 50)
    
    # Check files
    files_to_check = [
        "app.py",
        "static/index.html", 
        "static/styles.css"
    ]
    
    print("\n📁 File Structure:")
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (MISSING)")
    
    # Check directories
    print("\n📂 Directories:")
    dirs_to_check = ["static", "uploads"]
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        if dir_path.exists():
            writable = os.access(dir_path, os.W_OK)
            print(f"  ✅ {dir_name}/ (writable: {writable})")
        else:
            print(f"  ❌ {dir_name}/ (MISSING)")
            print(f"     Create with: mkdir {dir_name}")
    
    # Check Python packages
    print("\n📦 Python Packages:")
    required_packages = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("multipart", "File upload support")  # Fixed: python-multipart installs as 'multipart'
    ]
    
    optional_packages = [
        ("langchain_ibm", "IBM Watson integration"),
        ("langchain_community", "Document loaders"), 
        ("chromadb", "Vector database"),
        ("ibm_watsonx_ai", "Watson AI SDK"),
        ("docx", "Word document support")
    ]
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} - {description}")
        except ImportError:
            print(f"  ❌ {package} - {description}")
            print(f"     Install with: pip install {package}")
    
    print(f"\n📦 Optional RAG Packages:")
    rag_count = 0
    for package, description in optional_packages:
        try:
            if package == "docx":
                __import__("docx")  # python-docx imports as 'docx'
            else:
                __import__(package)
            print(f"  ✅ {package} - {description}")
            rag_count += 1
        except ImportError:
            print(f"  ⚠️  {package} - {description}")
    
    print(f"\n🧠 RAG Status: {rag_count}/{len(optional_packages)} packages available")
    if rag_count == len(optional_packages):
        print("  ✅ Full RAG functionality available")
    elif rag_count > 0:
        print("  ⚠️  Partial RAG functionality")
    else:
        print("  📋 Demo mode only")
    
    # Check environment variables
    print("\n🔐 Environment Variables:")
    env_vars = ["IBM_API_KEY", "IBM_PROJECT_ID"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var} (set)")
        else:
            print(f"  ⚠️  {var} (not set - demo mode)")
    
    # Port check
    print("\n🌐 Network:")
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 8000))
            print("  ✅ Port 8000 available")
    except OSError:
        print("  ⚠️  Port 8000 in use (stop other servers or use different port)")
    
    print("\n" + "=" * 50)
    print("🚀 Next Steps:")
    print("1. Fix any ❌ issues above")
    print("2. Run: python app.py")
    print("3. Visit: http://localhost:8000")
    print("4. Check browser console (F12) for errors")

def create_missing_files():
    """Create missing directories"""
    print("\n🔧 Creating missing directories...")
    
    directories = ["static", "uploads"]
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir()
            print(f"  ✅ Created {dir_name}/")
        else:
            print(f"  📁 {dir_name}/ already exists")

if __name__ == "__main__":
    check_setup()
    
    # Ask if user wants to create missing directories
    try:
        response = input("\n❓ Create missing directories? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            create_missing_files()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

