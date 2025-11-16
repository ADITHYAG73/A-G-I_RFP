# AGI RFP - AI-Powered RFP Response Generation

An AI-powered deep research agent for automated RFP (Request for Proposal) response generation using LangGraph's deepagents framework.

## Overview

This system uses deep AI agents to analyze RFP documents and generate comprehensive, high-quality responses by:
- Breaking down RFPs into manageable sections
- Researching relevant information from knowledge bases
- Generating contextual, tailored responses
- Managing multi-step workflows with specialized subagents

## Architecture

- **Deep Agent Framework**: LangGraph's `deepagents` package
- **Vector Database**: ChromaDB (local) / Pinecone (production)
- **LLM**: Claude Sonnet 4.5 / GPT-4
- **Data Sources**:
  - SAM.gov public RFP database
  - Custom uploaded past RFP responses
  - Enterprise integrations (Google Drive, SharePoint)

## Project Structure

```
A-G-I_RFP/
├── src/
│   ├── agents/          # Deep agent configurations
│   ├── data/            # Data ingestion and processing
│   ├── vectordb/        # Vector database setup
│   ├── tools/           # Custom tools for agents
│   └── api/             # API endpoints
├── data/
│   ├── raw/             # Raw RFP documents
│   ├── processed/       # Processed documents
│   └── embeddings/      # Vector embeddings
├── tests/
├── notebooks/           # Jupyter notebooks for exploration
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

### 1. Install Dependencies

**Using uv (Recommended - Much Faster):**

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: brew install uv

# Install all dependencies
uv sync

# Install with OCR support for scanned PDFs
uv sync --extra ocr

# Install with dev tools
uv sync --extra dev

# Install everything
uv sync --all-extras
```

**Using pip:**

```bash
pip install -r requirements.txt

# For OCR support
pip install pytesseract pdf2image Pillow
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Download Sample RFP Data

```bash
python src/data/fetch_sam_data.py --limit 20
```

### 4. Process and Index Documents

```bash
python src/data/ingest_documents.py
```

### 5. Run the Deep Agent

```bash
# Generate RFP response
python src/agents/rfp_agent.py data/raw/sample_rfp.pdf

# Save output to file
python src/agents/rfp_agent.py data/raw/sample_rfp.pdf --output response.txt

# View examples and workflow
python examples/generate_rfp_response.py
```

## API Keys Required

- **SAM.gov API Key**: Free registration at https://sam.gov/
- **OpenAI API Key**: For embeddings (or use local models)
- **Anthropic API Key**: For Claude Sonnet 4.5

## Features

### Phase 1 - MVP (Current)
- [x] Data ingestion from SAM.gov
- [x] Document parsing (PDF, Word) with OCR support
- [x] Vector database setup with semantic search
- [x] Deep agent orchestrator with planning
- [x] Specialized subagents (Technical, Pricing, Qualifications, Executive Summary)
- [x] RFP response generation workflow
- [x] Vector-based knowledge retrieval

### Phase 2 - Enterprise (Planned)
- [ ] Multi-user support
- [ ] Workflow automation and approvals
- [ ] CRM integrations (Salesforce, HubSpot)
- [ ] Real-time collaboration
- [ ] API layer with async processing

### Phase 3 - Advanced (Planned)
- [ ] Win/loss analytics
- [ ] Compliance scoring
- [ ] Competitive intelligence
- [ ] Automated tender discovery

## License

MIT License - see LICENSE file
