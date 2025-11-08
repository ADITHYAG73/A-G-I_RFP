"""Vector database management for RFP document storage and retrieval."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class VectorStore:
    """Vector database for storing and retrieving RFP document chunks."""

    def __init__(
        self,
        collection_name: str = "rfp_documents",
        persist_directory: Optional[Path] = None,
        embedding_model_name: Optional[str] = None
    ):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory for ChromaDB persistence
            embedding_model_name: Name of the embedding model
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory or settings.chroma_persist_dir
        self.embedding_model_name = embedding_model_name or "all-MiniLM-L6-v2"

        # Initialize ChromaDB client
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=str(self.persist_directory),
                anonymized_telemetry=False
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "RFP document chunks with embeddings"}
        )

        # Initialize embedding model
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        logger.info(
            f"Initialized vector store: {self.collection_name} "
            f"at {self.persist_directory}"
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text chunks.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()

    def add_documents(
        self,
        chunks: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> int:
        """
        Add document chunks to vector store.

        Args:
            chunks: List of text chunks
            metadatas: List of metadata dictionaries for each chunk
            ids: Optional list of IDs for each chunk

        Returns:
            Number of chunks added
        """
        if not chunks:
            logger.warning("No chunks to add")
            return 0

        # Generate IDs if not provided
        if ids is None:
            existing_count = self.collection.count()
            ids = [f"chunk_{existing_count + i}" for i in range(len(chunks))]

        # Generate metadata if not provided
        if metadatas is None:
            metadatas = [{} for _ in chunks]

        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)

        # Add to collection
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"Added {len(chunks)} chunks to vector store")
        return len(chunks)

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar documents.

        Args:
            query: Query text
            n_results: Number of results to return
            where: Metadata filter
            where_document: Document content filter

        Returns:
            Dictionary with search results
        """
        # Generate query embedding
        query_embedding = self.generate_embeddings([query])[0]

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            where_document=where_document
        )

        logger.info(f"Found {len(results['documents'][0])} results for query")
        return results

    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()

        stats = {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "persist_directory": str(self.persist_directory),
            "embedding_model": self.embedding_model_name
        }

        return stats

    def delete_collection(self):
        """Delete the collection."""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")

    def reset_collection(self):
        """Reset the collection by deleting and recreating it."""
        self.delete_collection()
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "RFP document chunks with embeddings"}
        )
        logger.info(f"Reset collection: {self.collection_name}")


def main():
    """Test vector store functionality."""
    # Initialize vector store
    store = VectorStore()

    # Test data
    test_chunks = [
        "The project requires cloud infrastructure deployment on AWS.",
        "Our team has 10+ years of experience in software development.",
        "The proposed timeline is 6 months with monthly deliverables.",
        "Budget estimate: $500,000 including all phases of development.",
    ]

    test_metadata = [
        {"source": "test_rfp_1", "section": "technical_requirements"},
        {"source": "test_rfp_1", "section": "qualifications"},
        {"source": "test_rfp_1", "section": "timeline"},
        {"source": "test_rfp_1", "section": "budget"},
    ]

    # Add documents
    print("\n=== Adding Test Documents ===")
    count = store.add_documents(test_chunks, test_metadata)
    print(f"✓ Added {count} chunks")

    # Get stats
    print("\n=== Collection Stats ===")
    stats = store.get_collection_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Search
    print("\n=== Search Test ===")
    query = "What is the project timeline?"
    results = store.search(query, n_results=2)

    print(f"Query: {query}")
    print(f"\nTop {len(results['documents'][0])} results:")
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    ), 1):
        print(f"\n{i}. [Distance: {distance:.4f}]")
        print(f"   Section: {metadata.get('section', 'N/A')}")
        print(f"   Text: {doc}")


if __name__ == "__main__":
    main()
