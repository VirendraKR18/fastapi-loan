"""
LangChain compatibility tests for version 0.3.7 with langchain-core 0.3.15
"""
import pytest
import os
from pathlib import Path


def test_langchain_imports():
    """Test that all required LangChain components can be imported"""
    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_community.vectorstores import FAISS
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_openai import AzureChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain.chains import create_retrieval_chain
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        assert PyPDFLoader is not None
        assert FAISS is not None
        assert HuggingFaceEmbeddings is not None
        assert AzureChatOpenAI is not None
        assert ChatPromptTemplate is not None
        assert create_stuff_documents_chain is not None
        assert create_retrieval_chain is not None
        assert RecursiveCharacterTextSplitter is not None
        
    except ImportError as e:
        pytest.fail(f"LangChain import failed: {e}")


def test_huggingface_embeddings_creation():
    """Test HuggingFace embeddings model can be instantiated"""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        assert embeddings is not None
        
        # Test embedding generation
        test_text = "This is a test document for embedding generation."
        embedding_vector = embeddings.embed_query(test_text)
        
        assert isinstance(embedding_vector, list)
        assert len(embedding_vector) == 384  # all-MiniLM-L6-v2 produces 384-dim vectors
        
    except Exception as e:
        pytest.fail(f"HuggingFace embeddings creation failed: {e}")


def test_chat_prompt_template():
    """Test ChatPromptTemplate creation"""
    try:
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt = ChatPromptTemplate.from_template("""
        Answer the question based only on the following context:
        {context}
        
        Question: {input}
        """)
        
        assert prompt is not None
        assert "context" in prompt.input_variables
        assert "input" in prompt.input_variables
        
    except Exception as e:
        pytest.fail(f"ChatPromptTemplate creation failed: {e}")


def test_text_splitter():
    """Test RecursiveCharacterTextSplitter for large PDF handling"""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        test_text = "This is a test. " * 200  # Create text > 1000 chars
        chunks = text_splitter.split_text(test_text)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 1000 + 200 for chunk in chunks)  # Allow overlap
        
    except Exception as e:
        pytest.fail(f"Text splitter creation failed: {e}")


@pytest.mark.skipif(
    not os.getenv("OPENAI_ENDPOINT") or not os.getenv("OPENAI_API_KEY"),
    reason="Azure OpenAI credentials not configured"
)
def test_azure_chat_openai_creation():
    """Test AzureChatOpenAI client can be instantiated"""
    try:
        from langchain_openai import AzureChatOpenAI
        
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
            deployment_name=os.getenv("CHATGPT_MODEL", "gpt-35-turbo"),
            temperature=0
        )
        
        assert llm is not None
        
    except Exception as e:
        pytest.fail(f"AzureChatOpenAI creation failed: {e}")


def test_langchain_version():
    """Test LangChain version is correct"""
    import langchain
    import langchain_core
    
    # Verify langchain-core is 0.3.15+
    core_version = langchain_core.__version__
    assert core_version >= "0.3.15", f"langchain-core version {core_version} is below 0.3.15"
    
    print(f"LangChain version: {langchain.__version__}")
    print(f"LangChain Core version: {core_version}")
