"""Custom tools for RFP deep agents."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from langchain.tools import tool

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings
from src.vectordb.vector_store import VectorStore

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


# Initialize global vector store
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


@tool
def search_past_rfp_responses(query: str, n_results: int = 5) -> str:
    """
    Search the knowledge base for similar past RFP responses.

    Use this tool to find relevant information from past RFPs, proposals,
    company documents, and knowledge base entries.

    Args:
        query: The search query (e.g., "cloud infrastructure technical approach")
        n_results: Number of results to return (default: 5)

    Returns:
        Formatted string with search results
    """
    try:
        store = get_vector_store()
        results = store.search(query, n_results=n_results)

        if not results['documents'][0]:
            return "No relevant information found in knowledge base."

        # Format results
        output = f"Found {len(results['documents'][0])} relevant passages:\n\n"

        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            source = metadata.get('source_file', metadata.get('source', 'Unknown'))
            section = metadata.get('section', '')

            output += f"[{i}] Relevance: {1 - distance:.2f}\n"
            output += f"Source: {source}"
            if section:
                output += f" (Section: {section})"
            output += f"\n{doc}\n\n"

        logger.info(f"Vector search for '{query}': found {len(results['documents'][0])} results")
        return output

    except Exception as e:
        logger.error(f"Error searching vector store: {e}")
        return f"Error searching knowledge base: {str(e)}"


@tool
def get_company_info(category: str) -> str:
    """
    Get company information for RFP responses.

    Use this to retrieve standard company information like certifications,
    past projects, team qualifications, security compliance, etc.

    Args:
        category: Type of information needed (e.g., "certifications",
                 "security_compliance", "past_projects", "team_qualifications")

    Returns:
        Company information for the requested category
    """
    # TODO: In production, this would pull from a company database
    # For now, return placeholder that guides agent to search vector DB

    company_data = {
        "certifications": "ISO 27001, SOC 2 Type II, FedRAMP Moderate",
        "security_compliance": "GDPR compliant, HIPAA certified, FISMA authorized",
        "past_projects": "Search vector database with query: 'past projects similar to [RFP topic]'",
        "team_qualifications": "Search vector database with query: 'team experience with [technology]'",
        "company_overview": "Leading technology solutions provider with 15+ years of experience in government and enterprise sectors.",
    }

    result = company_data.get(
        category.lower(),
        f"For '{category}' information, search the vector database with relevant keywords."
    )

    logger.info(f"Retrieved company info for category: {category}")
    return result


@tool
def analyze_rfp_requirements(rfp_text: str) -> Dict[str, List[str]]:
    """
    Analyze RFP document and extract key requirements.

    Parses the RFP to identify:
    - Technical requirements
    - Budget constraints
    - Timeline/deadlines
    - Compliance requirements
    - Evaluation criteria

    Args:
        rfp_text: The full text of the RFP document

    Returns:
        Dictionary with categorized requirements
    """
    # TODO: In production, use more sophisticated NLP/LLM-based extraction
    # For now, use keyword-based detection as placeholder

    requirements = {
        "technical": [],
        "budget": [],
        "timeline": [],
        "compliance": [],
        "qualifications": [],
        "evaluation_criteria": []
    }

    # Simple keyword detection (placeholder)
    lines = rfp_text.lower().split('\n')

    for line in lines:
        if any(kw in line for kw in ['must', 'require', 'shall', 'should']):
            if any(kw in line for kw in ['technical', 'technology', 'system', 'software', 'infrastructure']):
                requirements['technical'].append(line.strip())
            elif any(kw in line for kw in ['budget', 'cost', 'price', 'financial']):
                requirements['budget'].append(line.strip())
            elif any(kw in line for kw in ['deadline', 'timeline', 'schedule', 'duration']):
                requirements['timeline'].append(line.strip())
            elif any(kw in line for kw in ['compliance', 'regulation', 'standard', 'certification']):
                requirements['compliance'].append(line.strip())
            elif any(kw in line for kw in ['experience', 'qualification', 'expertise', 'credential']):
                requirements['qualifications'].append(line.strip())

    logger.info(f"Analyzed RFP: found {sum(len(v) for v in requirements.values())} requirements")
    return requirements


# Export all tools
__all__ = [
    'search_past_rfp_responses',
    'get_company_info',
    'analyze_rfp_requirements',
]
