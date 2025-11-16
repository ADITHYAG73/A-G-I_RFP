"""Enhanced document processing with OCR support for scanned PDFs."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from pypdf import PdfReader
from docx import Document
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


class DocumentProcessorWithOCR:
    """Process various document formats with OCR fallback for scanned PDFs."""

    def __init__(self, use_ocr: bool = True, ocr_threshold: int = 100):
        """
        Initialize document processor.

        Args:
            use_ocr: Whether to use OCR for scanned PDFs
            ocr_threshold: Minimum characters needed, else trigger OCR
        """
        self.use_ocr = use_ocr
        self.ocr_threshold = ocr_threshold

    def extract_text_from_pdf(self, file_path: Path, force_ocr: bool = False) -> str:
        """
        Extract text from PDF file with OCR fallback.

        Args:
            file_path: Path to PDF file
            force_ocr: Force OCR even if text extraction works

        Returns:
            Extracted text content
        """
        text = ""

        # Try standard text extraction first (unless forced to use OCR)
        if not force_ocr:
            try:
                reader = PdfReader(file_path)
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        text += f"\n\n--- Page {page_num} ---\n\n{page_text}"
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num}: {e}")

                logger.info(f"Extracted {len(text)} characters from PDF: {file_path.name}")
            except Exception as e:
                logger.error(f"Error reading PDF {file_path}: {e}")

        # Check if we need OCR (no text found or forced)
        if force_ocr or (self.use_ocr and len(text.strip()) < self.ocr_threshold):
            logger.info(f"Text extraction insufficient ({len(text)} chars), using OCR for {file_path.name}")
            text = self._extract_text_with_ocr(file_path)

        return text

    def _extract_text_with_ocr(self, file_path: Path) -> str:
        """
        Extract text from PDF using OCR.

        Args:
            file_path: Path to PDF file

        Returns:
            OCR extracted text
        """
        try:
            # Convert PDF to images
            logger.info(f"Converting PDF to images for OCR: {file_path.name}")
            images = convert_from_path(file_path, dpi=300)

            text = ""
            for page_num, image in enumerate(images, 1):
                logger.info(f"Running OCR on page {page_num}/{len(images)}")

                # Run OCR on image
                page_text = pytesseract.image_to_string(image, lang='eng')
                text += f"\n\n--- Page {page_num} (OCR) ---\n\n{page_text}"

            logger.info(f"OCR extracted {len(text)} characters from {file_path.name}")
            return text

        except Exception as e:
            logger.error(f"Error during OCR processing {file_path}: {e}")
            logger.error("Make sure tesseract-ocr is installed: sudo apt-get install tesseract-ocr")
            logger.error("And poppler-utils: sudo apt-get install poppler-utils")
            return ""

    def extract_text_from_image(self, file_path: Path) -> str:
        """
        Extract text from image file using OCR.

        Args:
            file_path: Path to image file

        Returns:
            OCR extracted text
        """
        try:
            logger.info(f"Running OCR on image: {file_path.name}")
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='eng')

            logger.info(f"OCR extracted {len(text)} characters from {file_path.name}")
            return text

        except Exception as e:
            logger.error(f"Error during OCR on image {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_docx(file_path: Path) -> str:
        """
        Extract text from DOCX file.

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text content
        """
        try:
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs]
            text = "\n".join(paragraphs)

            logger.info(f"Extracted {len(text)} characters from DOCX: {file_path.name}")
            return text

        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_txt(file_path: Path) -> str:
        """
        Extract text from TXT file.

        Args:
            file_path: Path to TXT file

        Returns:
            Extracted text content
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            logger.info(f"Extracted {len(text)} characters from TXT: {file_path.name}")
            return text

        except Exception as e:
            logger.error(f"Error reading TXT {file_path}: {e}")
            return ""

    def extract_text(self, file_path: Path, force_ocr: bool = False) -> str:
        """
        Extract text from document based on file extension.

        Args:
            file_path: Path to document file
            force_ocr: Force OCR for PDFs

        Returns:
            Extracted text content
        """
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            return self.extract_text_from_pdf(file_path, force_ocr)
        elif suffix in [".docx", ".doc"]:
            return self.extract_text_from_docx(file_path)
        elif suffix == ".txt":
            return self.extract_text_from_txt(file_path)
        elif suffix in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            return self.extract_text_from_image(file_path)
        else:
            logger.warning(f"Unsupported file format: {suffix}")
            return ""

    def chunk_text(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> List[str]:
        """
        Split text into chunks for embedding.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or settings.chunk_size
        chunk_overlap = chunk_overlap or settings.chunk_overlap

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within last 200 chars
                last_period = text.rfind(".", start, end)
                last_newline = text.rfind("\n", start, end)

                break_point = max(last_period, last_newline)
                if break_point > start:
                    end = break_point + 1

            chunks.append(text[start:end].strip())
            start = end - chunk_overlap

        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

    def process_document(
        self,
        file_path: Path,
        force_ocr: bool = False,
        extract_metadata: bool = True
    ) -> Dict:
        """
        Process a document: extract text, chunk it, and extract metadata.

        Args:
            file_path: Path to document
            force_ocr: Force OCR for PDFs
            extract_metadata: Whether to extract metadata

        Returns:
            Dictionary with processed document data
        """
        logger.info(f"Processing document: {file_path.name}")

        # Extract text
        text = self.extract_text(file_path, force_ocr)

        if not text:
            logger.warning(f"No text extracted from {file_path.name}")
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "text": "",
                "chunks": [],
                "metadata": {}
            }

        # Chunk text
        chunks = self.chunk_text(text)

        # Extract metadata
        metadata = {
            "file_name": file_path.name,
            "file_type": file_path.suffix,
            "file_size": file_path.stat().st_size,
            "num_chunks": len(chunks),
            "text_length": len(text),
            "ocr_used": "OCR" in text  # Check if OCR markers are present
        }

        result = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "text": text,
            "chunks": chunks,
            "metadata": metadata
        }

        logger.info(f"Processed {file_path.name}: {len(chunks)} chunks, {len(text)} chars")
        return result


# Backward compatibility - use original processor as default
from src.data.document_processor import DocumentProcessor

def main():
    """Test OCR document processing."""
    import argparse

    parser = argparse.ArgumentParser(description="Process RFP documents with OCR")
    parser.add_argument("file_path", type=Path, help="Path to document file")
    parser.add_argument("--force-ocr", action="store_true", help="Force OCR for PDFs")
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR fallback")
    args = parser.parse_args()

    processor = DocumentProcessorWithOCR(use_ocr=not args.no_ocr)
    result = processor.process_document(args.file_path, force_ocr=args.force_ocr)

    print(f"\n✓ Processed: {result['file_name']}")
    print(f"  Text length: {result['metadata']['text_length']} characters")
    print(f"  Chunks: {result['metadata']['num_chunks']}")
    print(f"  OCR used: {result['metadata']['ocr_used']}")
    print(f"\n  First chunk preview:")
    if result['chunks']:
        print(f"  {result['chunks'][0][:200]}...")


if __name__ == "__main__":
    main()
