"""
Academic Search Module: AcademicSearch for multi-source research
Handles ArXiv search with potential for future expansion to other sources
"""

from typing import List, Dict, Any, Optional
import arxiv
from loguru import logger
from utils.logger import log_tool_call


class AcademicSearch:
    """
    Academic search service for finding research papers.
    Currently supports ArXiv, designed for easy expansion to other sources.
    """

    def __init__(self, device: Optional[str] = None):
        """
        Initialize the academic search service.

        Args:
            device: Target device (for future vector search implementations)
        """
        self.device = device
        logger.info("AcademicSearch initialized")

    @log_tool_call
    def search_arxiv(
        self,
        query: str,
        top_k: int = 3,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance
    ) -> List[Dict[str, Any]]:
        """
        Search ArXiv for academic papers.

        Args:
            query: Search query string
            top_k: Number of results to return (default: 3)
            sort_by: Sort criterion (Relevance, LastUpdatedDate, SubmittedDate)

        Returns:
            List of paper dictionaries with metadata
        """
        try:
            logger.info(f"Searching ArXiv: '{query}' (top_k={top_k})")

            # Search ArXiv
            search = arxiv.Search(
                query=query,
                max_results=top_k,
                sort_by=sort_by
            )

            results = []
            for paper in search.results():
                paper_dict = {
                    'title': paper.title,
                    'authors': [str(author) for author in paper.authors],
                    'summary': paper.summary,
                    'published': paper.published.strftime('%Y-%m-%d'),
                    'url': paper.entry_id,
                    'pdf_url': paper.pdf_url,
                    'categories': paper.categories,
                    'primary_category': paper.primary_category
                }
                results.append(paper_dict)

            logger.info(f"Found {len(results)} papers on ArXiv")
            return results

        except Exception as e:
            logger.error(f"ArXiv search failed: {e}")
            return []

    @log_tool_call
    def search_arxiv_formatted(
        self,
        query: str,
        top_k: int = 3
    ) -> str:
        """
        Search ArXiv and return formatted string results.

        Args:
            query: Search query string
            top_k: Number of results to return

        Returns:
            Formatted string with paper information
        """
        papers = self.search_arxiv(query, top_k)

        if not papers:
            return f"No papers found for query: {query}"

        formatted_results = []
        for i, paper in enumerate(papers, 1):
            result = f"**Paper {i}: {paper['title']}**\n"
            result += f"Authors: {', '.join(paper['authors'][:3])}"
            if len(paper['authors']) > 3:
                result += f" et al. ({len(paper['authors'])} total)"
            result += f"\nPublished: {paper['published']}\n"
            result += f"Summary: {paper['summary'][:300]}...\n"
            result += f"URL: {paper['url']}"
            formatted_results.append(result)

        return f"Found {len(papers)} papers on ArXiv:\n\n" + "\n\n---\n\n".join(formatted_results)

    @log_tool_call
    def multi_search(
        self,
        query: str,
        sources: List[str] = ["arxiv"],
        top_k: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across multiple academic sources.

        Args:
            query: Search query string
            sources: List of sources to search (currently only "arxiv")
            top_k: Number of results per source

        Returns:
            Dictionary mapping source names to result lists
        """
        results = {}

        if "arxiv" in sources:
            results["arxiv"] = self.search_arxiv(query, top_k)

        # Future expansion: add other sources here
        # if "pubmed" in sources:
        #     results["pubmed"] = self.search_pubmed(query, top_k)
        # if "semantic_scholar" in sources:
        #     results["semantic_scholar"] = self.search_semantic_scholar(query, top_k)

        return results


if __name__ == "__main__":
    # Test the search module
    print("AcademicSearch Test")
    print("-" * 50)

    searcher = AcademicSearch()

    # Test ArXiv search
    query = "quantum entanglement"
    print(f"\nSearching for: '{query}'")
    print("=" * 50)

    papers = searcher.search_arxiv(query, top_k=2)
    print(f"\nFound {len(papers)} papers:")

    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:2])}")
        print(f"   Published: {paper['published']}")
        print(f"   URL: {paper['url']}")

    # Test formatted search
    print("\n" + "=" * 50)
    print("Formatted Search:")
    print("=" * 50)
    formatted = searcher.search_arxiv_formatted(query, top_k=1)
    print(formatted)
