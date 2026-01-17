"""
AI Agent Tools: search_arxiv and calculate
Implements LangChain tools for the voice agent
"""

from langchain_core.tools import tool
from typing import Optional
import arxiv
import sympy
from loguru import logger


@tool
def search_arxiv(query: str, limit: int = 3) -> str:
    """
    Search arXiv for scientific papers and return summaries.

    Args:
        query: The search query string
        limit: Maximum number of results to return (default: 3, configurable via ARXIV_MAX_RESULTS)

    Returns:
        A formatted string with paper titles and summaries
    """
    try:
        logger.info(f"Searching arXiv for: {query} (limit: {limit})")

        # Search arXiv
        search = arxiv.Search(
            query=query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = []
        for paper in search.results():
            result = f"Title: {paper.title}\n"
            result += f"Authors: {', '.join(str(author) for author in paper.authors)}\n"
            result += f"Published: {paper.published.strftime('%Y-%m-%d')}\n"
            result += f"Summary: {paper.summary[:300]}...\n"
            result += f"URL: {paper.entry_id}\n"
            results.append(result)

        if not results:
            return f"No papers found for query: {query}"

        response = f"Found {len(results)} papers on arXiv:\n\n" + "\n---\n".join(results)
        logger.info(f"Found {len(results)} papers")
        return response

    except Exception as e:
        error_msg = f"Error searching arXiv: {str(e)}"
        logger.error(error_msg)
        return error_msg


@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.
    Supports basic arithmetic, algebra, calculus, and more via SymPy.

    Args:
        expression: A mathematical expression as a string (e.g., "2+2", "sqrt(16)", "integrate(x**2, x)")

    Returns:
        The result of the calculation as a string
    """
    try:
        logger.info(f"Calculating expression: {expression}")

        # Handle division by zero check
        if "1/0" in expression.replace(" ", "") or "/0" in expression:
            return "Error: Division by zero is undefined. Please provide a valid mathematical expression."

        # Use SymPy for safe evaluation
        result = sympy.sympify(expression)

        # Simplify and evaluate the result
        simplified = sympy.simplify(result)

        # Try to get a numerical value if possible
        try:
            numerical = float(simplified.evalf())
            if numerical.is_integer():
                response = f"The result is: {int(numerical)}"
            else:
                response = f"The result is: {numerical}"
        except:
            response = f"The result is: {simplified}"

        logger.info(f"Calculation result: {response}")
        return response

    except sympy.SympifyError as e:
        error_msg = f"Error: Invalid mathematical expression. {str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error calculating expression: {str(e)}"
        logger.error(error_msg)
        return error_msg


# Tool registry for easy access
TOOL_REGISTRY = {
    "search_arxiv": search_arxiv,
    "calculate": calculate
}

# List of all tools for LangChain
ALL_TOOLS = [search_arxiv, calculate]


if __name__ == "__main__":
    # Test the tools
    print("Testing calculate tool:")
    print(calculate.invoke({"expression": "2+2"}))
    print(calculate.invoke({"expression": "sqrt(16)"}))
    print(calculate.invoke({"expression": "1/0"}))

    print("\nTesting search_arxiv tool:")
    print(search_arxiv.invoke({"query": "quantum entanglement", "limit": 2}))
