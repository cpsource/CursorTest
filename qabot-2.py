# -*- coding: utf-8 -*-
"""
RAG Application with improved error handling, credential validation, and LangChain updates
"""

import os
from getpass import getpass
import warnings
warnings.filterwarnings('ignore')

# === CREDENTIAL SETUP WITH VALIDATION ===
def setup_credentials():
    """Setup and validate IBM Watson credentials - simplified sequential steps"""
    import os
    from getpass import getpass
    
    # Step 1: Try os.getenv first (checks if already in environment)
    print("🔍 Step 1: Checking environment variables...")
    ibm_api_key = os.getenv('IBM_API_KEY')
    ibm_project_id = os.getenv('IBM_PROJECT_ID')
    watsonx_apikey = os.getenv('WATSONX_APIKEY')
    
    if ibm_api_key and ibm_project_id:
        print("✅ Found credentials in environment variables")
        if not watsonx_apikey:
            watsonx_apikey = ibm_api_key
    else:
        # Step 2: Try dotenv to load .env file
        print("🔍 Step 2: Trying to load .env file...")
        try:
            from dotenv import load_dotenv
            from pathlib import Path
            
            # Try home directory first, then find_dotenv
            env_path = Path.home() / '.env'
            if env_path.exists():
                load_dotenv(env_path)
                print(f"📄 Loaded .env from {env_path}")
            else:
                from dotenv import find_dotenv
                env_file = find_dotenv()
                if env_file:
                    load_dotenv(env_file)
                    print(f"📄 Loaded .env from {env_file}")
            
            # Check environment again after loading .env
            ibm_api_key = os.getenv('IBM_API_KEY')
            ibm_project_id = os.getenv('IBM_PROJECT_ID')
            watsonx_apikey = os.getenv('WATSONX_APIKEY')
            
            if ibm_api_key and ibm_project_id:
                print("✅ Found credentials from .env file")
                if not watsonx_apikey:
                    watsonx_apikey = ibm_api_key
            else:
                print("⚠️  .env file loaded but missing required credentials")
                
        except ImportError:
            print("⚠️  python-dotenv not installed")
        except Exception as e:
            print(f"⚠️  Error loading .env: {e}")
    
    # Step 3: Manual input if still missing
    if not ibm_api_key or not ibm_project_id:
        print("🔍 Step 3: Manual input required...")
        ibm_api_key = getpass('IBM API Key: ')
        ibm_project_id = getpass('IBM Project ID: ')
        watsonx_apikey = ibm_api_key
    
    # Step 4: Validate and set
    if not ibm_api_key or len(ibm_api_key) < 40:
        raise ValueError("IBM API Key appears invalid (too short)")
    if not ibm_project_id or len(ibm_project_id) < 30:
        raise ValueError("IBM Project ID appears invalid (too short)")
    
    # Set environment variables
    os.environ['IBM_API_KEY'] = ibm_api_key
    os.environ['IBM_PROJECT_ID'] = ibm_project_id
    os.environ['WATSONX_APIKEY'] = watsonx_apikey
    
    print("✅ Credentials configured successfully")
    return ibm_api_key, ibm_project_id, watsonx_apikey

# === TEST CREDENTIALS FUNCTION ===
def test_credentials():
    """Test if credentials work by making a simple API call"""
    try:
        from ibm_watsonx_ai.foundation_models import ModelInference
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
        
        # Try to create a simple model instance
        model = ModelInference(
            model_id='mistralai/mixtral-8x7b-instruct-v01',
            params={GenParams.MAX_NEW_TOKENS: 10},
            credentials={
                "url": "https://us-south.ml.cloud.ibm.com",
                "apikey": os.environ['IBM_API_KEY']
            },
            project_id=os.environ['IBM_PROJECT_ID']
        )
        
        # Try a simple generation
        response = model.generate_text("Hello")
        print("✅ Credentials test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Credentials test failed: {e}")
        return False

# === IMPORTS ===
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames
from langchain_ibm import WatsonxLLM, WatsonxEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
import gradio as gr

# === CORE FUNCTIONS WITH ERROR HANDLING ===

def get_llm():
    """Initialize the LLM with error handling"""
    try:
        model_id = 'mistralai/mixtral-8x7b-instruct-v01'
        parameters = {
            GenParams.MAX_NEW_TOKENS: 256,
            GenParams.TEMPERATURE: 0.5,
        }
        
        watsonx_llm = WatsonxLLM(
            model_id=model_id,
            url="https://us-south.ml.cloud.ibm.com",
            project_id=os.environ['IBM_PROJECT_ID'],
            apikey=os.environ['IBM_API_KEY'],
            params=parameters,
        )
        return watsonx_llm
    except Exception as e:
        print(f"❌ Error initializing LLM: {e}")
        raise

def watsonx_embedding():
    """Initialize embeddings with error handling"""
    try:
        embed_params = {
            EmbedTextParamsMetaNames.TRUNCATE_INPUT_TOKENS: 3,
            EmbedTextParamsMetaNames.RETURN_OPTIONS: {"input_text": True},
        }
        
        watsonx_embedding = WatsonxEmbeddings(
            model_id="ibm/slate-125m-english-rtrvr",
            url="https://us-south.ml.cloud.ibm.com",
            project_id=os.environ['IBM_PROJECT_ID'],
            apikey=os.environ['IBM_API_KEY'],
            params=embed_params,
        )
        return watsonx_embedding
    except Exception as e:
        print(f"❌ Error initializing embeddings: {e}")
        raise

def document_loader(file):
    """
    Universal document loader that handles PDF, DOCX, and TXT files
    
    Args:
        file: File object with .name attribute (from Gradio file upload)
        
    Returns:
        list: List of Document objects loaded from the file
        
    Raises:
        ValueError: If file type is not supported or file is invalid
    """
    import os
    from pathlib import Path
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    from langchain_community.document_loaders import Docx2txtLoader
    
    try:
        # Validate file input
        if not file or not hasattr(file, 'name'):
            raise ValueError("Invalid file provided")
        
        file_path = file.name
        if not os.path.exists(file_path):
            raise ValueError(f"File does not exist: {file_path}")
        
        # Get file extension
        file_extension = Path(file_path).suffix.lower()
        
        # Route to appropriate loader based on file type
        if file_extension == '.pdf':
            print(f"📄 Loading PDF: {file_path}")
            loader = PyPDFLoader(file_path)
            
        elif file_extension == '.docx':
            print(f"📝 Loading DOCX: {file_path}")
            loader = Docx2txtLoader(file_path)
            
        elif file_extension == '.txt':
            print(f"📃 Loading TXT: {file_path}")
            loader = TextLoader(file_path, encoding='utf-8')
            
        else:
            supported_types = ['.pdf', '.docx', '.txt']
            raise ValueError(f"Unsupported file type: {file_extension}. Supported types: {supported_types}")
        
        # Load the document
        loaded_document = loader.load()
        
        # Validate content was loaded
        if not loaded_document:
            raise ValueError(f"No content found in file: {file_path}")
        
        # Check if documents have content
        total_chars = sum(len(doc.page_content) for doc in loaded_document)
        if total_chars == 0:
            raise ValueError(f"File appears to be empty: {file_path}")
        
        print(f"✅ Successfully loaded {len(loaded_document)} document(s) with {total_chars} characters")
        
        # Add metadata about file type and source
        for doc in loaded_document:
            doc.metadata.update({
                'file_type': file_extension,
                'source_file': os.path.basename(file_path),
                'total_documents': len(loaded_document)
            })
        
        return loaded_document
        
    except Exception as e:
        error_msg = f"Error loading document '{file_path if 'file_path' in locals() else 'unknown'}': {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)


# Alternative version with automatic encoding detection for text files
def document_loader_advanced(file):
    """
    Enhanced document loader with automatic encoding detection for text files
    
    This version is more robust for text files with unknown encodings
    """
    import os
    from pathlib import Path
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    from langchain_community.document_loaders import Docx2txtLoader
    
    try:
        # Validate file input
        if not file or not hasattr(file, 'name'):
            raise ValueError("Invalid file provided")
        
        file_path = file.name
        if not os.path.exists(file_path):
            raise ValueError(f"File does not exist: {file_path}")
        
        # Get file extension
        file_extension = Path(file_path).suffix.lower()
        
        # Route to appropriate loader
        if file_extension == '.pdf':
            print(f"📄 Loading PDF: {file_path}")
            loader = PyPDFLoader(file_path)
            
        elif file_extension == '.docx':
            print(f"📝 Loading DOCX: {file_path}")
            loader = Docx2txtLoader(file_path)
            
        elif file_extension == '.txt':
            print(f"📃 Loading TXT: {file_path}")
            # Try different encodings for better compatibility
            encodings_to_try = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            loader = None
            for encoding in encodings_to_try:
                try:
                    loader = TextLoader(file_path, encoding=encoding)
                    # Test if it can actually load
                    test_load = loader.load()
                    print(f"✅ Successfully detected encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue
            
            if loader is None:
                raise ValueError(f"Could not determine text file encoding. Tried: {encodings_to_try}")
                
        else:
            supported_types = ['.pdf', '.docx', '.txt']
            raise ValueError(f"Unsupported file type: {file_extension}. Supported types: {supported_types}")
        
        # Load the document
        loaded_document = loader.load()
        
        # Validate content
        if not loaded_document:
            raise ValueError(f"No content found in file: {file_path}")
        
        total_chars = sum(len(doc.page_content) for doc in loaded_document)
        if total_chars == 0:
            raise ValueError(f"File appears to be empty: {file_path}")
        
        print(f"✅ Successfully loaded {len(loaded_document)} document(s) with {total_chars} characters")
        
        # Enhanced metadata
        for doc in loaded_document:
            doc.metadata.update({
                'file_type': file_extension,
                'source_file': os.path.basename(file_path),
                'file_size_bytes': os.path.getsize(file_path),
                'total_documents': len(loaded_document),
                'character_count': len(doc.page_content)
            })
        
        return loaded_document
        
    except Exception as e:
        error_msg = f"Error loading document: {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)


# Required installations (add to your requirements or install manually):
"""
pip install python-docx  # For .docx files
pip install langchain-community  # For document loaders
"""    
    
def text_splitter(data):
    """Split text into chunks with improved configuration"""
    try:
        if not data:
            raise ValueError("No document data provided")
        
        # Improved text splitter configuration
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,  # Increased overlap for better continuity
            length_function=len,
            separators=["\n\n", "\n", " ", ""]  # Better separation hierarchy
        )
        chunks = text_splitter.split_documents(data)
        
        if not chunks:
            raise ValueError("No chunks created from document")
        
        print(f"✅ Split document into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        print(f"❌ Error splitting text: {e}")
        raise

def vector_database(chunks):
    """Create vector database with improved configuration"""
    try:
        if not chunks:
            raise ValueError("No chunks provided for vector database")
        
        embedding_model = watsonx_embedding()
        
        # Configure Chroma with improved settings
        vectordb = Chroma.from_documents(
            documents=chunks, 
            embedding=embedding_model,
            collection_metadata={"hnsw:space": "cosine"}  # Better similarity metric
        )
        print("✅ Created vector database")
        return vectordb
    except Exception as e:
        print(f"❌ Error creating vector database: {e}")
        raise

def create_retriever(file):
    """Create retriever from file with improved configuration"""
    try:
        splits = document_loader_advanced(file)
        chunks = text_splitter(splits)
        vectordb = vector_database(chunks)
        
        # Configure retriever with dynamic k based on chunk count
        # This fixes the "Number of requested results greater than elements" warning
        max_chunks = len(chunks)
        k = min(4, max_chunks)  # Use minimum of 4 or available chunks
        
        retriever = vectordb.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}  # Dynamic k value
        )
        print(f"✅ Created retriever with k={k} (max available: {max_chunks})")
        return retriever
    except Exception as e:
        print(f"❌ Error creating retriever: {e}")
        raise

def retriever_qa(file, query):
    """Main QA function with comprehensive error handling and modern LangChain usage"""
    try:
        # Input validation
        if not file:
            return "Please upload a PDF file first."
        
        if not query or not query.strip():
            return "Please enter a question."
        
        print(f"🔍 Processing query: {query}")
        print(f"📄 File: {file.name if hasattr(file, 'name') else file}")
        
        # Initialize components
        llm = get_llm()
        retriever_obj = create_retriever(file)
        
        # Create QA chain
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever_obj,
            return_source_documents=False,
            verbose=False  # Reduce verbose output
        )
        
        # Use invoke instead of deprecated __call__ method
        try:
            response = qa.invoke({"query": query})
            result = response.get('result', response) if isinstance(response, dict) else response
        except AttributeError:
            # Fallback for older LangChain versions
            response = qa({"query": query})
            result = response['result']
        
        print("✅ Generated response successfully")
        return result
        
    except ValueError as ve:
        error_msg = f"Input Error: {str(ve)}"
        print(f"❌ {error_msg}")
        return error_msg
        
    except Exception as e:
        error_msg = f"Processing Error: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Sorry, I encountered an error while processing your request.\n\nError details: {str(e)}\n\nPlease check your file and try again."

# === ENHANCED GRADIO INTERFACE ===
def create_gradio_interface():
    """Create an enhanced Gradio interface"""
    
    def process_query(file, query, history):
        """Process query and maintain chat history"""
        if not file:
            response = "⚠️ Please upload a PDF file first."
        elif not query.strip():
            response = "⚠️ Please enter a question."
        else:
            response = retriever_qa(file, query)
        
        # Add to history
        history.append([query, response])
        return history, ""
    
    def clear_chat():
        """Clear chat history"""
        return []
    
    # Create the interface
    with gr.Blocks(title="RAG Resume Checker", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🤖 RAG Resume Checker (WatsonxLLM)")
        gr.Markdown("Upload your resume as a PDF document and ask questions about its content!")
        
        with gr.Row():
            with gr.Column(scale=1):
                file_upload = gr.File(
                    label="📄 Upload PDF File", 
                    file_count="single", 
                    file_types=['.pdf'],
                    type="filepath"
                )
                
                clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
                
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Chat History",
                    height=400,
                    show_label=True
                )
                
                with gr.Row():
                    query_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Ask a question about the uploaded document...",
                        lines=2,
                        scale=4
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
        
        # Event handlers
        submit_btn.click(
            process_query,
            inputs=[file_upload, query_input, chatbot],
            outputs=[chatbot, query_input]
        )
        
        query_input.submit(
            process_query,
            inputs=[file_upload, query_input, chatbot],
            outputs=[chatbot, query_input]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot]
        )
    
    return app

# === MAIN SETUP ===
def main():
    """Main setup function with enhanced error handling"""
    print("🚀 Setting up RAG Application...")
    
    try:
        # Setup credentials
        setup_credentials()
        
        # Test credentials
        if not test_credentials():
            print("❌ Credential test failed. Please check your IBM Watson credentials.")
            return None
        
        # Create Gradio interface
        app = create_gradio_interface()
        
        print("✅ RAG Application ready!")
        return app
        
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return None

# === LAUNCH ===
if __name__ == "__main__":
    # Setup and launch
    app = main()
    if app:
        print("🌐 Launching application...")
        app.launch(
            server_name="0.0.0.0", 
            server_port=7860, 
            share=False, 
            debug=False,
            show_error=True
        )
    else:
        print("❌ Failed to initialize application")

