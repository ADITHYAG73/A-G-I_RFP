"""Example: Generate RFP response using the deep agent system."""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.rfp_agent import create_rfp_agent, generate_rfp_response
from src.agents.specialized_agents import create_subagent


def example_basic_usage():
    """Example 1: Basic RFP response generation."""
    print("\n" + "="*70)
    print("Example 1: Basic RFP Response Generation")
    print("="*70 + "\n")

    # Create the agent
    print("Creating RFP agent...")
    agent = create_rfp_agent()

    # Generate response for an RFP
    rfp_path = "data/raw/sample_rfp.txt"  # Replace with actual RFP path

    print(f"Generating response for: {rfp_path}")
    print("This may take a few minutes as the agent researches and generates content...\n")

    result = generate_rfp_response(
        rfp_document_path=rfp_path,
        agent=agent,
        stream=False
    )

    print("\n✓ Response generated successfully!")
    print(f"\nResult keys: {result.keys()}")


def example_using_subagents():
    """Example 2: Using specialized subagents directly."""
    print("\n" + "="*70)
    print("Example 2: Using Specialized Subagents")
    print("="*70 + "\n")

    # Create different types of subagents
    print("Creating specialized agents...")

    technical_agent = create_subagent("technical")
    pricing_agent = create_subagent("pricing")
    qualifications_agent = create_subagent("qualifications")

    print("✓ Technical agent created")
    print("✓ Pricing agent created")
    print("✓ Qualifications agent created")

    # Example: Use technical agent for a specific query
    print("\nExample query to technical agent:")
    query = """Generate a technical approach for a cloud infrastructure migration project.
    Requirements:
    - Migrate 50 legacy applications to AWS
    - Implement CI/CD pipelines
    - Ensure FedRAMP compliance
    - Timeline: 12 months
    """

    print(f"\nQuery: {query}\n")
    print("Invoking technical agent...")

    result = technical_agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })

    print("\n✓ Technical approach generated!")


def example_with_vector_search():
    """Example 3: Testing vector search integration."""
    print("\n" + "="*70)
    print("Example 3: Vector Search Integration")
    print("="*70 + "\n")

    from src.tools.rfp_tools import search_past_rfp_responses

    # Test vector search
    queries = [
        "cloud infrastructure technical approach",
        "pricing for software development projects",
        "team qualifications for AWS projects",
    ]

    for query in queries:
        print(f"\nSearching for: '{query}'")
        print("-" * 50)

        results = search_past_rfp_responses.invoke({"query": query, "n_results": 3})
        print(results[:500] + "..." if len(results) > 500 else results)


def example_agent_workflow():
    """Example 4: Complete agent workflow walkthrough."""
    print("\n" + "="*70)
    print("Example 4: Complete Agent Workflow")
    print("="*70 + "\n")

    workflow_steps = """
    STEP-BY-STEP RFP RESPONSE GENERATION WORKFLOW:

    1. INTAKE
       ├─ Upload RFP document
       ├─ Parse and extract requirements
       └─ Identify key sections needed

    2. PLANNING
       ├─ Main agent creates todo list
       ├─ Breaks down into sections:
       │  ├─ Executive Summary
       │  ├─ Technical Approach
       │  ├─ Pricing & Budget
       │  ├─ Team Qualifications
       │  └─ Additional sections as needed
       └─ Prioritizes based on evaluation criteria

    3. RESEARCH
       ├─ Vector search for similar past RFPs
       ├─ Retrieve company information
       ├─ Find relevant technical approaches
       └─ Gather pricing benchmarks

    4. DELEGATION
       ├─ Spawn Technical Agent → Generates technical approach
       ├─ Spawn Pricing Agent → Creates budget breakdown
       ├─ Spawn Qualifications Agent → Compiles team info
       └─ Spawn Executive Summary Agent → Writes summary

    5. COMPILATION
       ├─ Main agent collects all sections
       ├─ Ensures consistency and flow
       ├─ Formats professionally
       └─ Final review and adjustments

    6. OUTPUT
       └─ Complete RFP response document
    """

    print(workflow_steps)

    print("\nTo run this workflow:")
    print("  python src/agents/rfp_agent.py <path_to_rfp.pdf>")


def main():
    """Run all examples."""
    import argparse

    parser = argparse.ArgumentParser(description="RFP Agent Examples")
    parser.add_argument(
        "--example",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run specific example (1-4)"
    )

    args = parser.parse_args()

    examples = {
        1: example_basic_usage,
        2: example_using_subagents,
        3: example_with_vector_search,
        4: example_agent_workflow,
    }

    if args.example:
        examples[args.example]()
    else:
        # Run workflow walkthrough by default
        example_agent_workflow()

        print("\n" + "="*70)
        print("To run specific examples:")
        print("="*70)
        print("  python examples/generate_rfp_response.py --example 1  # Basic usage")
        print("  python examples/generate_rfp_response.py --example 2  # Subagents")
        print("  python examples/generate_rfp_response.py --example 3  # Vector search")
        print("  python examples/generate_rfp_response.py --example 4  # Workflow")


if __name__ == "__main__":
    main()
