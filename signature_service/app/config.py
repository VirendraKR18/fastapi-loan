from pydantic_settings import BaseSettings
import os

# Get absolute path to model
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BASE_DIR, "..", "FastAPI", "media", "model", "best.pt")

class Settings(BaseSettings):
    SERVICE_NAME: str = "Signature Detection Service"
    SERVICE_PORT: int = 8001
    MODEL_PATH: str = os.path.abspath(_MODEL_PATH)
    class Config:
        env_file = ".env"

settings = Settings()
