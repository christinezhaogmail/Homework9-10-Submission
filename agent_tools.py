"""
AI Agent Tools: search_arxiv and calculate
Implements LangChain tools for the voice agent
"""

from langchain_core.tools import tool
from typing import List, Optional
import arxiv
import sympy
import requests
from loguru import logger
from config import Config

@tool
def summarize(texts: List[str]) -> str:
    """
    Return a concise summary of the given passages using local Ollama model.
    Uses the model configured in Config.LLM_MODEL.

    Args:
        texts: A list of text passages to summarize

    Returns:
        A concise summary combining all passages
    """
    try:
        if not texts:
            return "No text provided for summarization."

        logger.info(f"Summarizing {len(texts)} text passages using Ollama model: {Config.LLM_MODEL}")

        # Combine all texts into a single document
        combined_text = " ".join(texts)

        # Create a summarization prompt
        prompt = f"""Please provide a concise summary of the following text. Focus on the main points and key findings.

Text to summarize:
{combined_text}

Summary:"""

        # Prepare the request payload for Ollama
        payload = {
            "model": Config.LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "temperature": Config.SUMMARIZATION_TEMPERATURE,
            "options": {
                "num_predict": 200,  # Limit summary length
            }
        }

        logger.info(f"Sending summarization request to Ollama at {Config.OLLAMA_BASE_URL}")

        # Make the API request to Ollama
        response = requests.post(
            f"{Config.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        # Parse the response
        result = response.json()
        summary_text = result.get("response", "").strip()

        if not summary_text:
            return "Error: Received empty summary from model."

        logger.info(f"Generated summary: {summary_text[:100]}...")
        return summary_text

    except requests.exceptions.ConnectionError:
        error_msg = "Error: Cannot connect to Ollama. Make sure Ollama is running with 'ollama serve' and the model is loaded."
        logger.error(error_msg)
        return error_msg
    except requests.exceptions.Timeout:
        error_msg = "Error: Summarization request timed out."
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error generating summary: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def sync_to_notion(session_id: str, content: str):
    """Append the session content and summary to Notion."""
    pass

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
    "calculate": calculate,
    "summarize": summarize,
    "sync_to_notion": sync_to_notion,
}

# List of all tools for LangChain
ALL_TOOLS = [search_arxiv, calculate, summarize, sync_to_notion]

if __name__ == "__main__":
    # Test the tools
    print("Testing calculate tool:")
    print(calculate.invoke({"expression": "2+2"}))
    print(calculate.invoke({"expression": "sqrt(16)"}))
    print(calculate.invoke({"expression": "1/0"}))

    print("\nTesting search_arxiv tool:")
    print(search_arxiv.invoke({"query": "quantum entanglement", "limit": 2}))

    print("\nTesting summarize tool:")
    test_texts = [
        "Quantum entanglement is a physical phenomenon that occurs when pairs or groups of particles are generated or interact in ways such that the quantum state of each particle cannot be described independently of the state of the others.",
        "This phenomenon has been demonstrated experimentally with photons, neutrinos, electrons, molecules as large as buckyballs, and even small diamonds.",
        "Entanglement is at the heart of quantum computing and quantum cryptography, and has been used in experiments testing the foundations of quantum mechanics."
    ]
    print(summarize.invoke({"texts": test_texts}))
