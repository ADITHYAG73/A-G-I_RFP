"""Configuration management for AGI RFP system."""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings."""

    # SAM.gov API
    sam_api_key: str = os.getenv("SAM_API_KEY", "")
    sam_api_base_url: str = os.getenv("SAM_API_BASE_URL", "https://api.sam.gov/prod/opportunities/v2")

    # LLM API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Vector Database
    vector_db_type: Literal["chromadb", "pinecone", "weaviate"] = os.getenv("VECTOR_DB_TYPE", "chromadb")
    vector_db_path: Path = Path(os.getenv("VECTOR_DB_PATH", "./data/vectordb"))
    chroma_persist_dir: Path = Path(os.getenv("CHROMA_PERSIST_DIR", "./data/vectordb/chroma"))

    # Pinecone (optional)
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "rfp-responses")

    # Application
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_documents_fetch: int = int(os.getenv("MAX_DOCUMENTS_FETCH", "20"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    llm_model: str = os.getenv("LLM_MODEL", "claude-sonnet-4.5-20250929")

    # Data directories
    data_dir: Path = PROJECT_ROOT / "data"
    raw_data_dir: Path = PROJECT_ROOT / "data" / "raw"
    processed_data_dir: Path = PROJECT_ROOT / "data" / "processed"
    embeddings_dir: Path = PROJECT_ROOT / "data" / "embeddings"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        settings.data_dir,
        settings.raw_data_dir,
        settings.processed_data_dir,
        settings.embeddings_dir,
        settings.vector_db_path,
        settings.chroma_persist_dir,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ensured: {directory}")


if __name__ == "__main__":
    ensure_directories()
    print("\n✓ Configuration loaded successfully")
    print(f"  - Vector DB Type: {settings.vector_db_type}")
    print(f"  - LLM Model: {settings.llm_model}")
    print(f"  - Embedding Model: {settings.embedding_model}")
