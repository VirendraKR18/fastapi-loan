"""
RAG service - async wrapper for retrieval-augmented generation
"""
import asyncio
import os
from typing import List, Dict, Optional

try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_openai import AzureChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
except ImportError as e:
    print(f"LangChain import error: {e}")
    PyPDFLoader = None
    FAISS = None
    HuggingFaceEmbeddings = None
    AzureChatOpenAI = None
    ChatPromptTemplate = None
    create_stuff_documents_chain = None
    create_retrieval_chain = None

from ..config import settings
from ..utils.vector_store import vector_store_state, calculate_pdf_hash, get_latest_pdf_path
from ..utils.pdf_chunker import chunk_pdf_text, should_chunk_pdf
from ..exceptions import VectorizationException, AzureOpenAIException, PDFNotFoundException
import logging

logger = logging.getLogger(__name__)


def _create_embeddings():
    """Create HuggingFace embeddings"""
    if HuggingFaceEmbeddings is None:
        raise VectorizationException("LangChain HuggingFace not available")
    
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)


def _load_pdf_and_create_vectors(pdf_path: str):
    """Load PDF and create vector store with chunking support"""
    if PyPDFLoader is None or FAISS is None:
        raise VectorizationException("LangChain components not available")
    
    try:
        logger.info(f"Loading PDF and creating vectors: {pdf_path}")
        
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Check if PDF needs chunking
        pdf_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        page_count = len(documents)
        
        if should_chunk_pdf(pdf_size_mb, page_count):
            logger.info(f"Chunking large PDF: {page_count} pages, {pdf_size_mb:.2f} MB")
            # Use text splitter for large PDFs
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            documents = text_splitter.split_documents(documents)
            logger.info(f"Split into {len(documents)} chunks")
        
        if vector_store_state.embeddings is None:
            vector_store_state.embeddings = _create_embeddings()
        
        # Set batch size for optimal performance
        vector_store = FAISS.from_documents(
            documents, 
            vector_store_state.embeddings
        )
        
        logger.info("Vector store created successfully")
        return vector_store
        
    except Exception as e:
        logger.error(f"Failed to create vector store: {e}")
        raise VectorizationException(f"Failed to process document for Q&A. Please try re-uploading the PDF.")


def _create_rag_chain(vector_store, chat_history: Optional[List[Dict[str, str]]] = None):
    """Create RAG chain with Azure OpenAI and chat history support"""
    if AzureChatOpenAI is None or ChatPromptTemplate is None:
        raise AzureOpenAIException("LangChain OpenAI components not available")
    
    try:
        logger.info(f"Creating Azure OpenAI client with deployment: {settings.CHATGPT_MODEL}")
        llm = AzureChatOpenAI(
            azure_endpoint=settings.OPENAI_ENDPOINT,
            api_key=settings.OPENAI_API_KEY,
            api_version=settings.OPENAI_API_VERSION,
            deployment_name=settings.CHATGPT_MODEL,
            temperature=1  # gpt-5-mini only supports temperature=1
        )
        
        # Build prompt with chat history support
        history_text = ""
        if chat_history:
            history_items = []
            for item in chat_history[-3:]:  # Last 3 Q&A pairs
                q = item.get('question', '')
                a = item.get('answer', '')
                if q and a:
                    history_items.append(f"Q: {q}\nA: {a}")
            if history_items:
                history_text = "Previous conversation:\n" + "\n\n".join(history_items) + "\n\n"
        
        prompt_template = f"""{history_text}Answer the question based only on the following context:
        {{context}}
        
        Question: {{input}}
        
        Provide a detailed and accurate answer based on the context above. If the context doesn't contain relevant information, say "I couldn't find relevant information in the document to answer your question."
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})  # Top 4 chunks
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        return retrieval_chain
    except Exception as e:
        logger.error(f"Failed to create RAG chain: {e}")
        raise AzureOpenAIException(f"Failed to create RAG chain: {str(e)}")


async def _generate_rag_response(
    question: str, 
    pdf_path: str, 
    pdf_hash: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """Generate RAG response for question with concurrent access locking"""
    # Acquire lock for thread-safe access to global state
    await vector_store_state.acquire_lock()
    
    try:
        # Check if vectors need to be created or updated
        if vector_store_state.vector_store is None or vector_store_state.pdf_hash != pdf_hash:
            logger.info("Creating new vector store (PDF changed or first request)")
            vector_store = await asyncio.to_thread(_load_pdf_and_create_vectors, pdf_path)
            vector_store_state.vector_store = vector_store
            vector_store_state.pdf_hash = pdf_hash
        else:
            logger.info("Using cached vector store")
        
        # Create RAG chain with chat history
        chain = _create_rag_chain(vector_store_state.vector_store, chat_history)
        
        # Generate response
        logger.info(f"Invoking RAG chain with question: {question[:100]}...")
        try:
            response = await asyncio.to_thread(chain.invoke, {"input": question})
            return response.get("answer", "")
        except Exception as e:
            logger.error(f"RAG chain invocation failed: {type(e).__name__}: {str(e)}")
            raise AzureOpenAIException(f"Failed to generate response from Azure OpenAI: {str(e)}")
        
    finally:
        # Always release lock
        vector_store_state.release_lock()


async def generate_rag_response_async(
    question: str, 
    pdf_path: str = None,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Async wrapper for RAG response generation with chat history
    
    Args:
        question: User question
        pdf_path: Path to PDF file (optional, will use latest if not provided)
        chat_history: List of previous Q&A pairs (max 3)
        
    Returns:
        Answer string
    """
    # Get PDF path if not provided
    if pdf_path is None:
        pdf_path = get_latest_pdf_path(settings.MEDIA_ROOT)
    
    if not pdf_path or not os.path.exists(pdf_path):
        raise PDFNotFoundException("No document uploaded. Please upload a PDF before asking questions.")
    
    # Calculate PDF hash for change detection
    pdf_hash = await asyncio.to_thread(calculate_pdf_hash, pdf_path)
    
    # Generate response with chat history
    response = await _generate_rag_response(question, pdf_path, pdf_hash, chat_history)
    
    return response
