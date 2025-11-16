# OCR Support for Scanned RFP Documents

## The Problem

Many RFP documents (especially government RFPs) are **scanned PDFs** - images of documents rather than text-based PDFs. The standard text extraction doesn't work on these.

## Our Solution

We've created **two document processors**:

### 1. **Standard Processor** (`document_processor.py`)
- ✅ Fast and lightweight
- ✅ Works for text-based PDFs
- ❌ Fails on scanned PDFs

### 2. **OCR-Enhanced Processor** (`document_processor_ocr.py`)
- ✅ Handles text-based PDFs
- ✅ Automatically detects scanned PDFs
- ✅ Falls back to OCR when needed
- ✅ Supports image files (PNG, JPG, TIFF)
- ⚠️ Requires system dependencies (Tesseract)

## How It Works

```python
# Smart hybrid approach:
1. Try text extraction first (fast)
2. Check if we got enough text (> 100 chars)
3. If not, automatically use OCR (slower but accurate)
4. Mark in metadata whether OCR was used
```

## Installation

### Step 1: Install Python Packages

```bash
pip install pytesseract pdf2image Pillow
```

### Step 2: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
- Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Download Poppler: http://blog.alivate.com.au/poppler-windows/

### Step 3: Verify Installation

```bash
tesseract --version
pdftoppm -v
```

## Testing with Your Indian RFP

Since the automated download was blocked, here's how to test manually:

### Option 1: Manual Download

1. **Download the PDF** from your browser:
   ```
   https://www.nsgm.gov.in/sites/default/files/Model-RfP-Final_0.pdf
   ```

2. **Save it to**:
   ```bash
   data/raw/india_model_rfp.pdf
   ```

3. **Test text extraction**:
   ```bash
   # Try standard extraction first
   python src/data/document_processor.py data/raw/india_model_rfp.pdf
   ```

4. **If text extraction fails, use OCR**:
   ```bash
   # Force OCR
   python src/data/document_processor_ocr.py data/raw/india_model_rfp.pdf --force-ocr
   ```

### Option 2: Use Any Sample RFP

You can test with **any RFP PDF** you have:

```bash
# Automatic detection (tries text extraction, falls back to OCR)
python src/data/document_processor_ocr.py /path/to/your/rfp.pdf

# Force OCR
python src/data/document_processor_ocr.py /path/to/your/rfp.pdf --force-ocr

# Disable OCR (text extraction only)
python src/data/document_processor_ocr.py /path/to/your/rfp.pdf --no-ocr
```

## Ingesting Documents with OCR

To use OCR in the ingestion pipeline, you need to modify `ingest_documents.py`:

```python
# Instead of:
from src.data.document_processor import DocumentProcessor

# Use:
from src.data.document_processor_ocr import DocumentProcessorWithOCR as DocumentProcessor
```

Then run normally:

```bash
python src/data/ingest_documents.py --file data/raw/india_model_rfp.pdf
```

## Performance Considerations

| Method | Speed | Accuracy | Best For |
|--------|-------|----------|----------|
| **Text Extraction** | Very Fast | 100% | Digital PDFs |
| **OCR** | Slow | 95-98% | Scanned PDFs |

**OCR Speed**: ~2-5 seconds per page at 300 DPI

**Recommendations**:
- Use hybrid approach (auto-detect)
- Process in batches overnight for large datasets
- Cache OCR results to avoid reprocessing

## Checking If Your PDF Needs OCR

Simple test:

```bash
# Method 1: Try to copy-paste text from PDF viewer
# If you CAN copy text → Text-based PDF ✅
# If you CAN'T copy text → Scanned PDF (needs OCR) ⚠️

# Method 2: Test extraction
python -c "
from pypdf import PdfReader
reader = PdfReader('data/raw/your_file.pdf')
text = reader.pages[0].extract_text()
print(f'Extracted {len(text)} characters')
print('Needs OCR!' if len(text) < 100 else 'Text-based PDF')
"
```

## Example Output

### Text-based PDF:
```
✓ Processed: sample_rfp.pdf
  Text length: 15234 characters
  Chunks: 12
  OCR used: False
```

### Scanned PDF (with OCR):
```
✓ Processed: scanned_rfp.pdf
  Text length: 14892 characters
  Chunks: 11
  OCR used: True
```

## Troubleshooting

### Error: "tesseract is not installed"
```bash
# Install Tesseract OCR
sudo apt-get install tesseract-ocr
```

### Error: "Unable to get page count"
```bash
# Install poppler-utils
sudo apt-get install poppler-utils
```

### Poor OCR Quality
- Increase DPI in `document_processor_ocr.py` (line with `dpi=300`)
- Try different languages: `pytesseract.image_to_string(image, lang='eng+hin')`
- Pre-process images (denoise, deskew)

### Very Slow Processing
- Reduce DPI to 150-200 (faster but less accurate)
- Process in parallel (future enhancement)
- Use GPU-accelerated OCR (advanced)

## Next Steps

1. **Test with your Indian RFP** (manually downloaded)
2. **Verify OCR quality** on scanned pages
3. **Ingest into vector DB**
4. **Test semantic search** with RFP questions

Once verified, we can integrate this into the main pipeline!
