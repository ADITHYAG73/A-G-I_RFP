># Deep Agents for RFP Response Generation

This module contains the core AI agents that power the RFP response generation system.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main RFP Agent                           │
│  (Orchestrator - Planning & Coordination)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌────────────────┐
│  Technical   │ │ Pricing  │ │ Qualifications │
│    Agent     │ │  Agent   │ │     Agent      │
└──────────────┘ └──────────┘ └────────────────┘
        │            │            │
        └────────────┴────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Executive Summary Agent│
        └────────────────────────┘
```

## Agents

### 1. Main RFP Agent (`rfp_agent.py`)

**Role**: Orchestrator and coordinator

**Capabilities**:
- Analyzes RFP documents
- Creates execution plan with todos
- Delegates to specialized subagents
- Compiles final response
- Manages workflow and coordination

**Tools**:
- `write_todos` - Break down complex tasks
- `task` - Spawn subagents
- `search_past_rfp_responses` - Vector search
- `get_company_info` - Retrieve company data
- `analyze_rfp_requirements` - Extract requirements
- File operations - Read/write documents

**Usage**:
```python
from src.agents.rfp_agent import create_rfp_agent, generate_rfp_response

# Create agent
agent = create_rfp_agent()

# Generate response
result = generate_rfp_response(
    rfp_document_path="path/to/rfp.pdf",
    agent=agent
)
```

### 2. Technical Agent (`specialized_agents.py`)

**Role**: Technical approach and architecture expert

**Specialization**:
- Cloud infrastructure design
- Software development methodology
- System architecture
- Security and compliance
- Integration strategies

**Output**:
- Solution overview
- Architecture diagrams
- Technology stack
- Implementation methodology
- Testing and QA strategy
- Security measures
- Deployment plan

### 3. Pricing Agent (`specialized_agents.py`)

**Role**: Financial and pricing expert

**Specialization**:
- Cost estimation
- Budget breakdown
- Resource allocation
- Pricing strategies
- Value justification

**Output**:
- Executive pricing summary
- Detailed cost breakdown
- Labor costs by role
- Infrastructure and tools
- Payment schedule
- Cost optimization options

### 4. Qualifications Agent (`specialized_agents.py`)

**Role**: Credentials and experience expert

**Specialization**:
- Team composition
- Past project showcase
- Certifications
- Client testimonials
- Track record demonstration

**Output**:
- Company overview
- Certifications and compliance
- Team qualifications
- Past performance examples
- Client references
- Quality metrics

### 5. Executive Summary Agent (`specialized_agents.py`)

**Role**: Strategic communication expert

**Specialization**:
- Value proposition articulation
- Executive-level writing
- Business case development
- Persuasive communication

**Output**:
- Compelling opening
- Problem understanding
- Solution overview
- Key differentiators
- Investment justification
- Clear call to action

## Tools

### Vector Search Tool (`rfp_tools.py`)

```python
from src.tools.rfp_tools import search_past_rfp_responses

# Search knowledge base
results = search_past_rfp_responses.invoke({
    "query": "cloud migration technical approach",
    "n_results": 5
})
```

### Company Info Tool (`rfp_tools.py`)

```python
from src.tools.rfp_tools import get_company_info

# Get company data
info = get_company_info.invoke({
    "category": "certifications"
})
```

### Requirements Analyzer Tool (`rfp_tools.py`)

```python
from src.tools.rfp_tools import analyze_rfp_requirements

# Extract requirements
requirements = analyze_rfp_requirements.invoke({
    "rfp_text": rfp_content
})
```

## Workflow

### Standard RFP Response Generation Flow:

1. **Initialization**
   ```python
   agent = create_rfp_agent()
   ```

2. **Analysis**
   - Agent reads RFP document
   - Extracts requirements
   - Identifies key sections

3. **Planning**
   - Creates todo list
   - Breaks into sections
   - Prioritizes work

4. **Research**
   - Searches vector database
   - Retrieves company info
   - Finds relevant examples

5. **Delegation**
   - Spawns technical agent
   - Spawns pricing agent
   - Spawns qualifications agent
   - Each works in parallel

6. **Compilation**
   - Collects all sections
   - Executive summary agent synthesizes
   - Main agent formats and reviews

7. **Output**
   - Complete RFP response
   - Professionally formatted
   - Addresses all requirements

## Configuration

### Environment Variables

Required in `.env`:

```bash
# LLM Configuration
ANTHROPIC_API_KEY=your_key_here
LLM_MODEL=claude-sonnet-4.5-20250929

# Vector DB (for knowledge base)
VECTOR_DB_TYPE=chromadb
CHROMA_PERSIST_DIR=./data/vectordb/chroma

# Optional: Different models for different agents
TECHNICAL_AGENT_MODEL=claude-sonnet-4.5-20250929
PRICING_AGENT_MODEL=claude-sonnet-4.5-20250929
```

### Model Selection

Different agents can use different models based on their needs:

```python
# Main agent - balanced
agent = create_rfp_agent(model_name="claude-sonnet-4.5-20250929")

# Technical agent - lower temperature for precision
tech_agent = create_technical_agent(model_name="claude-sonnet-4.5-20250929")

# Executive summary - higher temperature for creativity
exec_agent = create_executive_summary_agent(model_name="claude-sonnet-4.5-20250929")
```

## Examples

See `examples/generate_rfp_response.py` for complete examples:

```bash
# View workflow walkthrough
python examples/generate_rfp_response.py

# Run specific examples
python examples/generate_rfp_response.py --example 1  # Basic usage
python examples/generate_rfp_response.py --example 2  # Subagents
python examples/generate_rfp_response.py --example 3  # Vector search
```

## CLI Usage

Generate RFP response from command line:

```bash
# Basic usage
python src/agents/rfp_agent.py path/to/rfp.pdf

# Save to file
python src/agents/rfp_agent.py path/to/rfp.pdf --output response.txt

# Stream output
python src/agents/rfp_agent.py path/to/rfp.pdf --stream
```

## Extending the System

### Adding New Subagents

1. Create agent prompt in `specialized_agents.py`:
```python
CUSTOM_AGENT_PROMPT = """Your custom agent instructions..."""
```

2. Create agent factory function:
```python
def create_custom_agent(model_name: Optional[str] = None) -> Any:
    model = ChatAnthropic(model=model_name or settings.llm_model)
    return create_deep_agent(
        model=model,
        system_prompt=CUSTOM_AGENT_PROMPT,
        tools=[search_past_rfp_responses, get_company_info],
    )
```

3. Register in `SUBAGENT_REGISTRY`:
```python
SUBAGENT_REGISTRY["custom"] = create_custom_agent
```

### Adding New Tools

1. Create tool in `rfp_tools.py`:
```python
@tool
def custom_tool(param: str) -> str:
    """Tool description for agent."""
    # Implementation
    return result
```

2. Add to agent's tools list:
```python
agent = create_rfp_agent(tools=[custom_tool])
```

## Performance Considerations

- **Parallel Execution**: Subagents run in parallel when possible
- **Caching**: Vector search results are cached per session
- **Streaming**: Use streaming for real-time feedback
- **Model Selection**: Use smaller models for simple tasks

## Troubleshooting

### Agent doesn't find relevant information
- Check vector database has documents: `python src/vectordb/vector_store.py`
- Verify API keys in `.env`
- Try different search queries

### Agent takes too long
- Enable streaming: `stream=True`
- Use smaller model for testing
- Reduce number of subagents

### Inconsistent responses
- Lower temperature for more deterministic output
- Add more examples to knowledge base
- Refine agent prompts

## Next Steps

- [ ] Add memory persistence across sessions
- [ ] Implement agent metrics and monitoring
- [ ] Add support for multi-turn conversations
- [ ] Create web UI for agent interaction
- [ ] Add evaluation metrics for response quality
