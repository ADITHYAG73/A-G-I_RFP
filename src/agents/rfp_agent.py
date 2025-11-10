"""Main RFP response generation agent using LangGraph deepagents."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_anthropic import ChatAnthropic
from deepagents import create_deep_agent

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings
from src.tools.rfp_tools import (
    search_past_rfp_responses,
    get_company_info,
    analyze_rfp_requirements,
)

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


# System prompt for the main RFP agent
RFP_AGENT_SYSTEM_PROMPT = """You are an expert RFP (Request for Proposal) response generator.

Your role is to analyze RFP documents and generate comprehensive, winning proposal responses.

## Your Capabilities:

1. **Planning & Breakdown**: Use the write_todos tool to break complex RFPs into manageable sections
2. **Research**: Use search_past_rfp_responses to find relevant information from past proposals
3. **Delegation**: Use the task tool to spawn specialized subagents for different sections
4. **Knowledge Access**: Use get_company_info to retrieve standard company details
5. **Document Management**: Use file operations to read RFPs and write responses

## Your Process:

1. **Analyze the RFP**:
   - Read the RFP document carefully
   - Identify key requirements, deadlines, and evaluation criteria
   - Use analyze_rfp_requirements to extract structured requirements

2. **Plan Your Response**:
   - Create a todo list breaking the RFP into sections (e.g., Executive Summary, Technical Approach, Pricing, Qualifications)
   - Identify which sections need research vs. standard company info
   - Prioritize based on evaluation criteria

3. **Research & Gather Information**:
   - Search the knowledge base for relevant past responses
   - Retrieve company certifications, qualifications, past projects
   - Find technical approaches that worked well previously

4. **Delegate to Subagents**:
   - Spawn specialized subagents for complex sections:
     * Technical Agent: For technical approach, architecture, methodology
     * Pricing Agent: For budget breakdown, cost estimates, pricing strategy
     * Qualifications Agent: For team experience, past projects, credentials
   - Each subagent should focus deeply on their section with full context

5. **Compile & Review**:
   - Combine all sections into a cohesive response
   - Ensure consistency in tone and messaging
   - Verify all requirements are addressed
   - Format professionally

## Best Practices:

- **Be specific**: Use concrete examples from past projects
- **Be compliant**: Address all mandatory requirements
- **Be persuasive**: Highlight unique value propositions
- **Be professional**: Maintain formal business tone
- **Be thorough**: Don't skip sections, even if challenging

## Output Format:

Your final response should include:
- Executive Summary (1-2 pages)
- Technical Approach (detailed methodology)
- Project Timeline & Milestones
- Team Qualifications & Experience
- Pricing & Budget Breakdown
- Risk Management Strategy
- References & Past Performance

Remember: The goal is to win the contract by demonstrating expertise, capability, and value.
"""


def create_rfp_agent(
    model_name: Optional[str] = None,
    tools: Optional[List] = None,
) -> Any:
    """
    Create the main RFP response generation agent.

    Args:
        model_name: LLM model to use (default: from settings)
        tools: Additional tools to provide to agent

    Returns:
        Configured deep agent
    """
    # Initialize LLM
    model_name = model_name or settings.llm_model
    logger.info(f"Creating RFP agent with model: {model_name}")

    model = ChatAnthropic(
        model=model_name,
        api_key=settings.anthropic_api_key,
        temperature=0.7,  # Some creativity, but not too much
    )

    # Combine default tools with any additional tools
    default_tools = [
        search_past_rfp_responses,
        get_company_info,
        analyze_rfp_requirements,
    ]

    all_tools = default_tools + (tools or [])

    # Create deep agent
    agent = create_deep_agent(
        model=model,
        system_prompt=RFP_AGENT_SYSTEM_PROMPT,
        tools=all_tools,
    )

    logger.info(f"RFP agent created with {len(all_tools)} tools")
    return agent


def generate_rfp_response(
    rfp_document_path: str,
    agent: Optional[Any] = None,
    stream: bool = False,
) -> Dict[str, Any]:
    """
    Generate an RFP response from a document.

    Args:
        rfp_document_path: Path to RFP document
        agent: Pre-configured agent (creates new if None)
        stream: Whether to stream the response

    Returns:
        Dictionary with generated response and metadata
    """
    # Create agent if not provided
    if agent is None:
        agent = create_rfp_agent()

    # Read RFP document
    rfp_path = Path(rfp_document_path)
    if not rfp_path.exists():
        raise FileNotFoundError(f"RFP document not found: {rfp_document_path}")

    logger.info(f"Processing RFP: {rfp_path.name}")

    # Construct message to agent
    message = f"""I need you to generate a comprehensive RFP response.

The RFP document is located at: {rfp_document_path}

Please:
1. Read and analyze the RFP document
2. Break down the response into sections
3. Research relevant information from the knowledge base
4. Generate a complete, winning proposal response

Start by reading the RFP file and creating your plan.
"""

    # Invoke agent
    logger.info("Invoking RFP agent...")

    if stream:
        # Streaming response
        result = {"messages": [], "response": ""}
        for chunk in agent.stream({"messages": [{"role": "user", "content": message}]}):
            result["messages"].append(chunk)
            # Extract response text
            if "messages" in chunk:
                for msg in chunk["messages"]:
                    if hasattr(msg, "content"):
                        result["response"] += msg.content

        return result
    else:
        # Non-streaming response
        result = agent.invoke({"messages": [{"role": "user", "content": message}]})
        return result


def main():
    """CLI interface for RFP agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate RFP response using deep agent")
    parser.add_argument(
        "rfp_path",
        type=str,
        help="Path to RFP document"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream the response"
    )

    args = parser.parse_args()

    # Generate response
    print(f"\n{'='*60}")
    print(f"Generating RFP Response")
    print(f"{'='*60}\n")

    result = generate_rfp_response(
        rfp_document_path=args.rfp_path,
        stream=args.stream
    )

    # Output result
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(str(result))

        print(f"\n✓ Response saved to: {output_path}")
    else:
        print("\n" + "="*60)
        print("GENERATED RESPONSE")
        print("="*60 + "\n")
        print(result)


if __name__ == "__main__":
    main()
