# Quick Start Guide

## What We've Built

A complete **data ingestion pipeline** for RFP documents with:

1. **SAM.gov Integration** - Pull real government RFP data
2. **Document Processing** - Parse PDF, Word, and text files
3. **Vector Database** - Store and search documents using embeddings
4. **End-to-End Pipeline** - Automated ingestion workflow

## Architecture

```
RFP Documents → Document Processor → Text Chunks → Embeddings → Vector DB
     ↓                                                              ↓
SAM.gov API                                                  Semantic Search
```

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# 3. Test the setup
python src/config.py
```

## Usage Examples

### 1. Fetch Sample RFPs from SAM.gov

**Note**: You need a free SAM.gov API key first:
- Register at https://sam.gov/
- Go to Account Settings → API Key
- Add to `.env` file

```bash
# Fetch 20 recent RFP opportunities
python src/data/fetch_sam_data.py --limit 20

# Output: data/raw/sam_opportunities_TIMESTAMP.json
```

### 2. Process a Local PDF Document

```bash
# Test document processing
python src/data/document_processor.py path/to/your/rfp.pdf
```

### 3. Test Vector Database

```bash
# Run the vector store test
python src/vectordb/vector_store.py

# This creates a test collection with sample data
```

### 4. Ingest Documents into Vector DB

```bash
# Option A: Ingest from SAM.gov JSON
python src/data/ingest_documents.py --sam-json data/raw/sam_opportunities_*.json

# Option B: Ingest PDF/Word files from directory
python src/data/ingest_documents.py --directory path/to/rfp/documents

# Option C: Ingest a single file
python src/data/ingest_documents.py --file path/to/document.pdf

# Reset database before ingesting
python src/data/ingest_documents.py --reset --directory data/raw
```

## Testing Without SAM.gov API Key

If you don't have a SAM.gov API key yet, you can still test:

1. **Create a test RFP document** (text file):
```bash
cat > data/raw/test_rfp.txt << 'EOF'
Request for Proposal: Cloud Infrastructure Modernization

Project Overview:
The Department of Technology seeks proposals for modernizing our cloud infrastructure.
The project requires migration of 50+ legacy applications to AWS cloud platform.

Technical Requirements:
- AWS certified solutions architect
- Experience with containerization (Docker, Kubernetes)
- CI/CD pipeline implementation
- Security compliance (FedRAMP, FISMA)

Timeline: 12 months
Budget: $2,000,000

Proposal Deadline: December 31, 2025
EOF
```

2. **Ingest the test document**:
```bash
python src/data/ingest_documents.py --file data/raw/test_rfp.txt
```

3. **Search the vector database**:
```python
from src.vectordb.vector_store import VectorStore

# Initialize
store = VectorStore()

# Search
results = store.search("What are the technical requirements?", n_results=3)

# Print results
for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
    print(f"\nSource: {metadata.get('source_file')}")
    print(f"Text: {doc[:200]}...")
```

## Next Steps

**Phase 1 - Deep Agent** (Next):
1. Integrate LangGraph's `deepagents` package
2. Create RFP analysis agent with planning tool
3. Build specialized subagents (technical, pricing, qualifications)
4. Implement response generation workflow

**Phase 2 - API Layer**:
1. FastAPI endpoint for RFP upload
2. Async task queue for processing
3. WebSocket for progress updates
4. Response download endpoint

**Phase 3 - Enterprise Features**:
1. Multi-tenancy support
2. User authentication
3. CRM integrations
4. Workflow automation

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Missing Dependencies
```bash
# Install specific packages
pip install chromadb sentence-transformers pypdf python-docx
```

### Vector DB Issues
```bash
# Reset the vector database
python src/data/ingest_documents.py --reset
```

## File Structure

```
A-G-I_RFP/
├── src/
│   ├── config.py                    # Configuration management
│   ├── data/
│   │   ├── fetch_sam_data.py       # SAM.gov API client
│   │   ├── document_processor.py   # Document parsing
│   │   └── ingest_documents.py     # Main pipeline
│   └── vectordb/
│       └── vector_store.py         # Vector database wrapper
├── data/
│   ├── raw/                        # Raw documents
│   ├── processed/                  # Processed data
│   └── embeddings/                 # Vector embeddings
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md                       # Project overview
```

## Questions?

- Check the main README.md for architecture details
- Review individual module docstrings
- Test each module independently before running the full pipeline
