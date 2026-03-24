"""
Environment configuration using Pydantic Settings
"""
import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

# Resolve .env path relative to the repo root (one level above FastAPI/)
_ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    OPENAI_ENDPOINT: str = Field(..., description="Azure OpenAI endpoint URL")
    OPENAI_API_KEY: str = Field(..., description="Azure OpenAI API key")
    OPENAI_API_VERSION: str = Field(default="2024-02-15-preview", description="Azure OpenAI API version")
    CHATGPT_MODEL: str = Field(..., description="Azure OpenAI chat model deployment name")
    
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model name"
    )
    
    MEDIA_ROOT: str = Field(
        default="media/uploaded_pdfs/",
        description="Directory for uploaded PDFs"
    )
    
    AZURE_FORM_RECOGNIZER_ENDPOINT: str | None = Field(
        default=None,
        description="Azure Form Recognizer endpoint URL"
    )
    AZURE_FORM_RECOGNIZER_KEY: str | None = Field(
        default=None,
        description="Azure Form Recognizer API key"
    )
    
    CORS_ORIGINS: str = Field(
        default="http://localhost:4200",
        description="Comma-separated list of allowed CORS origins"
    )
    
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8010, description="Server port")
    
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
