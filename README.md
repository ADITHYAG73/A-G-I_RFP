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

```bash
pip install -r requirements.txt
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

### 5. Run the Agent

```bash
python src/agents/rfp_agent.py --rfp-path data/raw/sample_rfp.pdf
```

## API Keys Required

- **SAM.gov API Key**: Free registration at https://sam.gov/
- **OpenAI API Key**: For embeddings (or use local models)
- **Anthropic API Key**: For Claude Sonnet 4.5

## Features

### Phase 1 - MVP (Current)
- [x] Data ingestion from SAM.gov
- [x] Document parsing (PDF, Word)
- [x] Vector database setup
- [ ] Basic deep agent with planning
- [ ] RFP response generation

### Phase 2 - Enterprise
- [ ] Multi-user support
- [ ] Workflow automation
- [ ] CRM integrations (Salesforce)
- [ ] Real-time collaboration

### Phase 3 - Advanced
- [ ] Win/loss analytics
- [ ] Compliance scoring
- [ ] Competitive intelligence

## License

MIT License - see LICENSE file
