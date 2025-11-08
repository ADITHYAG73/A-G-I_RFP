"""Main document ingestion pipeline for RFP documents."""

import argparse
import json
import logging
from pathlib import Path
from typing import List, Optional

from tqdm import tqdm

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings, ensure_directories
from src.data.document_processor import DocumentProcessor
from src.vectordb.vector_store import VectorStore

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class DocumentIngestionPipeline:
    """End-to-end pipeline for ingesting RFP documents."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        doc_processor: Optional[DocumentProcessor] = None
    ):
        """
        Initialize ingestion pipeline.

        Args:
            vector_store: VectorStore instance (creates new if None)
            doc_processor: DocumentProcessor instance (creates new if None)
        """
        self.vector_store = vector_store or VectorStore()
        self.doc_processor = doc_processor or DocumentProcessor()

        logger.info("Initialized document ingestion pipeline")

    def ingest_file(
        self,
        file_path: Path,
        metadata: Optional[dict] = None
    ) -> int:
        """
        Ingest a single document file.

        Args:
            file_path: Path to document file
            metadata: Optional metadata to attach to all chunks

        Returns:
            Number of chunks ingested
        """
        logger.info(f"Ingesting file: {file_path.name}")

        # Process document
        doc_data = self.doc_processor.process_document(file_path)

        if not doc_data["chunks"]:
            logger.warning(f"No chunks extracted from {file_path.name}")
            return 0

        # Prepare metadata for each chunk
        base_metadata = metadata or {}
        base_metadata.update({
            "source_file": file_path.name,
            "file_type": file_path.suffix,
            **doc_data["metadata"]
        })

        chunk_metadatas = [
            {**base_metadata, "chunk_index": i}
            for i in range(len(doc_data["chunks"]))
        ]

        # Generate unique IDs
        file_id = file_path.stem.replace(" ", "_")
        chunk_ids = [
            f"{file_id}_chunk_{i}"
            for i in range(len(doc_data["chunks"]))
        ]

        # Add to vector store
        count = self.vector_store.add_documents(
            chunks=doc_data["chunks"],
            metadatas=chunk_metadatas,
            ids=chunk_ids
        )

        logger.info(f"Successfully ingested {count} chunks from {file_path.name}")
        return count

    def ingest_directory(
        self,
        directory: Path,
        file_patterns: List[str] = None,
        recursive: bool = False,
        metadata: Optional[dict] = None
    ) -> int:
        """
        Ingest all documents from a directory.

        Args:
            directory: Path to directory
            file_patterns: List of file patterns to match (default: ["*.pdf", "*.docx", "*.txt"])
            recursive: Whether to search recursively
            metadata: Optional metadata to attach to all chunks

        Returns:
            Total number of chunks ingested
        """
        if file_patterns is None:
            file_patterns = ["*.pdf", "*.docx", "*.txt"]

        logger.info(f"Ingesting documents from {directory}")

        # Find all matching files
        files = []
        for pattern in file_patterns:
            if recursive:
                files.extend(directory.rglob(pattern))
            else:
                files.extend(directory.glob(pattern))

        if not files:
            logger.warning(f"No files found in {directory} matching {file_patterns}")
            return 0

        logger.info(f"Found {len(files)} files to ingest")

        # Ingest each file
        total_chunks = 0
        failed_files = []

        for file_path in tqdm(files, desc="Ingesting documents"):
            try:
                count = self.ingest_file(file_path, metadata)
                total_chunks += count
            except Exception as e:
                logger.error(f"Error ingesting {file_path.name}: {e}")
                failed_files.append(str(file_path))

        logger.info(f"Ingestion complete: {total_chunks} total chunks from {len(files)} files")

        if failed_files:
            logger.warning(f"Failed to ingest {len(failed_files)} files: {failed_files}")

        return total_chunks

    def ingest_sam_data(
        self,
        sam_json_file: Path,
        include_description: bool = True,
        include_full_text: bool = False
    ) -> int:
        """
        Ingest RFP data from SAM.gov JSON file.

        Args:
            sam_json_file: Path to JSON file from SAM.gov
            include_description: Whether to include description in chunks
            include_full_text: Whether to include full text if available

        Returns:
            Number of chunks ingested
        """
        logger.info(f"Ingesting SAM.gov data from {sam_json_file.name}")

        # Load JSON data
        with open(sam_json_file, "r", encoding="utf-8") as f:
            opportunities = json.load(f)

        if not isinstance(opportunities, list):
            opportunities = [opportunities]

        logger.info(f"Found {len(opportunities)} opportunities in JSON")

        total_chunks = 0

        for opp in tqdm(opportunities, desc="Processing SAM opportunities"):
            try:
                # Extract text content
                text_parts = []

                # Title
                if title := opp.get("title"):
                    text_parts.append(f"Title: {title}")

                # Description
                if include_description and (desc := opp.get("description")):
                    text_parts.append(f"Description: {desc}")

                # Full text if available
                if include_full_text and (full_text := opp.get("fullText")):
                    text_parts.append(full_text)

                if not text_parts:
                    continue

                # Combine text
                full_text = "\n\n".join(text_parts)

                # Chunk the text
                chunks = self.doc_processor.chunk_text(full_text)

                # Prepare metadata
                metadata = {
                    "source": "sam_gov",
                    "notice_id": opp.get("noticeId", ""),
                    "title": opp.get("title", ""),
                    "type": opp.get("type", ""),
                    "posted_date": opp.get("postedDate", ""),
                    "department": opp.get("department", {}).get("name", ""),
                    "office": opp.get("officeAddress", {}).get("city", ""),
                }

                chunk_metadatas = [
                    {**metadata, "chunk_index": i}
                    for i in range(len(chunks))
                ]

                # Generate IDs
                notice_id = opp.get("noticeId", "unknown")
                chunk_ids = [
                    f"sam_{notice_id}_chunk_{i}"
                    for i in range(len(chunks))
                ]

                # Add to vector store
                count = self.vector_store.add_documents(
                    chunks=chunks,
                    metadatas=chunk_metadatas,
                    ids=chunk_ids
                )

                total_chunks += count

            except Exception as e:
                logger.error(f"Error processing opportunity: {e}")

        logger.info(f"Ingested {total_chunks} chunks from SAM.gov data")
        return total_chunks

    def get_stats(self) -> dict:
        """Get ingestion pipeline statistics."""
        return self.vector_store.get_collection_stats()


def main():
    """CLI interface for document ingestion."""
    parser = argparse.ArgumentParser(description="Ingest RFP documents into vector store")

    parser.add_argument(
        "--file",
        type=Path,
        help="Single file to ingest"
    )
    parser.add_argument(
        "--directory",
        type=Path,
        help="Directory of files to ingest"
    )
    parser.add_argument(
        "--sam-json",
        type=Path,
        help="SAM.gov JSON file to ingest"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search directory recursively"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset vector store before ingesting"
    )

    args = parser.parse_args()

    # Ensure directories exist
    ensure_directories()

    # Initialize pipeline
    pipeline = DocumentIngestionPipeline()

    # Reset if requested
    if args.reset:
        print("\n⚠ Resetting vector store...")
        pipeline.vector_store.reset_collection()
        print("✓ Vector store reset\n")

    # Ingest data
    total_chunks = 0

    if args.file:
        print(f"\n=== Ingesting File: {args.file.name} ===")
        total_chunks = pipeline.ingest_file(args.file)

    elif args.directory:
        print(f"\n=== Ingesting Directory: {args.directory} ===")
        total_chunks = pipeline.ingest_directory(
            args.directory,
            recursive=args.recursive
        )

    elif args.sam_json:
        print(f"\n=== Ingesting SAM.gov Data: {args.sam_json.name} ===")
        total_chunks = pipeline.ingest_sam_data(args.sam_json)

    else:
        # Default: ingest from raw data directory
        print(f"\n=== Ingesting from {settings.raw_data_dir} ===")
        total_chunks = pipeline.ingest_directory(settings.raw_data_dir)

    # Print stats
    print(f"\n✓ Ingestion complete: {total_chunks} chunks added")

    stats = pipeline.get_stats()
    print("\n=== Vector Store Stats ===")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
