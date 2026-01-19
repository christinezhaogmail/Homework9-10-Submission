"""
AI Agent Tools: search_arxiv and summarize_and_save
Implements LangChain tools for the voice agent with Notion integration
"""

from langchain_core.tools import tool
from typing import Optional, Dict, Any
import arxiv
from loguru import logger
from datetime import datetime


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
def summarize_and_save(
    session_content: str,
    arxiv_papers: Optional[str] = None,
    query_count: int = 0
) -> str:
    """
    Summarize a research session and save it to Notion database.
    Extracts arXiv links and creates a comprehensive summary.

    Args:
        session_content: The full conversation/session content to summarize
        arxiv_papers: Information about arXiv papers queried (optional)
        query_count: Number of queries made in the session

    Returns:
        A confirmation message with the Notion page URL
    """
    try:
        logger.info(f"Summarizing session with {query_count} queries")

        # Import NotionSync here to avoid circular imports
        from tools.notion import NotionSync
        import re

        # Initialize Notion sync
        notion_sync = NotionSync()

        if not notion_sync.is_enabled():
            return "Notion sync is not configured. Please set NOTION_TOKEN and NOTION_DATABASE_ID environment variables."

        # Generate session ID
        session_id = f"arxiv_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Extract arXiv links from the papers string
        arxiv_links = []
        paper_titles = []
        if arxiv_papers:
            # Find all arXiv URLs
            url_pattern = r'URL: (https?://arxiv\.org/[^\s]+)'
            urls = re.findall(url_pattern, arxiv_papers)
            arxiv_links.extend(urls)

            # Find all paper titles
            title_pattern = r'Title: ([^\n]+)'
            titles = re.findall(title_pattern, arxiv_papers)
            paper_titles.extend(titles)

        # Create comprehensive summary
        summary = f"Research Session Summary ({query_count} arXiv queries)\n\n"

        # Add queries from session content
        if session_content:
            summary += "Queries:\n"
            for line in session_content.split('\n'):
                if line.strip():
                    summary += f"  • {line}\n"
            summary += "\n"

        # Add papers with titles and links
        if paper_titles and arxiv_links:
            summary += f"Papers Found ({len(paper_titles)} papers):\n\n"
            for i, (title, url) in enumerate(zip(paper_titles, arxiv_links), 1):
                summary += f"{i}. {title}\n"
                summary += f"   Link: {url}\n\n"
        elif arxiv_links:
            summary += f"arXiv Links ({len(arxiv_links)} papers):\n"
            for i, url in enumerate(arxiv_links, 1):
                summary += f"{i}. {url}\n"

        # Prepare metadata
        metadata = {
            "query_count": query_count,
            "timestamp": datetime.now().isoformat(),
            "papers_count": len(arxiv_links)
        }

        # Prepare full content with links
        full_content = f"{session_content}\n\n{'='*50}\n\nDetailed Results:\n\n{arxiv_papers if arxiv_papers else 'No papers'}"

        # Sync to Notion
        page_url = notion_sync.sync_session(
            session_id=session_id,
            content=full_content,
            summary=summary,
            metadata=metadata
        )

        if page_url:
            response = f"✓ Session summarized and saved to Notion!\n"
            response += f"📊 {query_count} queries, {len(arxiv_links)} papers found\n"
            response += f"🔗 View at: {page_url}\n\n"
            response += f"Summary:\n{summary[:500]}..."
            logger.info(f"Session saved to Notion: {page_url}")
            return response
        else:
            return "Failed to save session to Notion. Check logs for details."

    except ImportError as e:
        error_msg = f"Error: Notion integration not available. {str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error summarizing and saving session: {str(e)}"
        logger.error(error_msg)
        return error_msg


# Tool registry for easy access
TOOL_REGISTRY = {
    "search_arxiv": search_arxiv,
    "summarize_and_save": summarize_and_save
}

# List of all tools for LangChain
ALL_TOOLS = [search_arxiv, summarize_and_save]


if __name__ == "__main__":
    # Test the tools
    print("Testing search_arxiv tool:")
    result = search_arxiv.invoke({"query": "quantum entanglement", "limit": 2})
    print(result)

    print("\n" + "="*50)
    print("Testing summarize_and_save tool:")
    test_content = "User queried about quantum entanglement and got 2 papers."
    test_papers = "Paper 1: Quantum Entanglement Overview\nPaper 2: Advanced Quantum States"
    print(summarize_and_save.invoke({
        "session_content": test_content,
        "arxiv_papers": test_papers,
        "query_count": 3
    }))
