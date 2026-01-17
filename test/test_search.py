"""
Test script for Academic Search Module
Tests ArXiv search and multi-source search capabilities
"""

import sys
from loguru import logger

# Configure logger for testing
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

from tools.search import AcademicSearch


def test_arxiv_search():
    """Test ArXiv search functionality"""
    print("\n" + "=" * 70)
    print("TEST 1: ArXiv Search")
    print("=" * 70)

    searcher = AcademicSearch()

    print("\n[Test 1.1] Search for 'quantum entanglement'")
    papers = searcher.search_arxiv("quantum entanglement", top_k=2)
    print(f"Found {len(papers)} papers")

    assert len(papers) > 0, "No papers found"
    assert len(papers) <= 2, "Returned more papers than requested"
    print("✅ ArXiv search returned results")

    print("\n[Test 1.2] Verify paper structure")
    paper = papers[0]
    print(f"First paper: {paper['title'][:50]}...")

    required_keys = ['title', 'authors', 'summary', 'published', 'url']
    for key in required_keys:
        assert key in paper, f"Paper missing '{key}' field"
    print("✅ Paper has all required fields")

    print("\n[Test 1.3] Display paper details")
    print(f"  Title: {paper['title']}")
    print(f"  Authors: {', '.join(paper['authors'][:3])}")
    print(f"  Published: {paper['published']}")
    print(f"  URL: {paper['url']}")
    print(f"  Summary (first 100 chars): {paper['summary'][:100]}...")


def test_formatted_search():
    """Test formatted search output"""
    print("\n" + "=" * 70)
    print("TEST 2: Formatted Search")
    print("=" * 70)

    searcher = AcademicSearch()

    print("\n[Test 2.1] Get formatted search results")
    formatted = searcher.search_arxiv_formatted("machine learning", top_k=2)
    print(f"Formatted output length: {len(formatted)}")
    print(f"First 200 characters:\n{formatted[:200]}...")

    assert len(formatted) > 0, "Formatted output is empty"
    assert "Paper" in formatted, "Formatted output missing 'Paper' label"
    assert "URL:" in formatted, "Formatted output missing URL"
    print("✅ Formatted search output generated")


def test_multi_search():
    """Test multi-source search"""
    print("\n" + "=" * 70)
    print("TEST 3: Multi-Source Search")
    print("=" * 70)

    searcher = AcademicSearch()

    print("\n[Test 3.1] Multi-source search (ArXiv only for now)")
    results = searcher.multi_search("neural networks", sources=["arxiv"], top_k=2)
    print(f"Sources searched: {list(results.keys())}")

    assert "arxiv" in results, "ArXiv not in results"
    assert len(results["arxiv"]) > 0, "No ArXiv results"
    print("✅ Multi-source search completed")


def test_empty_query():
    """Test edge cases"""
    print("\n" + "=" * 70)
    print("TEST 4: Edge Cases")
    print("=" * 70)

    searcher = AcademicSearch()

    print("\n[Test 4.1] Search with very specific query")
    papers = searcher.search_arxiv("very_unlikely_paper_title_xyz123", top_k=1)
    print(f"Found {len(papers)} papers")
    # This might return 0 or some papers, just test it doesn't crash
    print("✅ Specific query handled")

    print("\n[Test 4.2] Search with top_k=1")
    papers = searcher.search_arxiv("deep learning", top_k=1)
    assert len(papers) <= 1, "Returned more than 1 paper"
    print("✅ top_k=1 respected")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("ACADEMIC SEARCH - TEST SUITE")
    print("=" * 70)

    try:
        test_arxiv_search()
        test_formatted_search()
        test_multi_search()
        test_empty_query()

        print("\n" + "=" * 70)
        print("🎉 ALL SEARCH TESTS PASSED!")
        print("=" * 70)

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FAILED: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
