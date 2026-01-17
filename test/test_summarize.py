"""
Test script for Summarization Module
Tests HuggingFace summarization with various text lengths
"""

import sys
from loguru import logger

# Configure logger for testing
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

from tools.summarize import ContentSummarizer


# Sample texts for testing
SAMPLE_TEXT = """
Quantum entanglement is a physical phenomenon that occurs when a group of particles
are generated, interact, or share spatial proximity in a way such that the quantum
state of each particle of the group cannot be described independently of the state
of the others, including when the particles are separated by a large distance.
The topic of quantum entanglement is at the heart of the disparity between classical
and quantum physics: entanglement is a primary feature of quantum mechanics lacking
in classical mechanics. Measurements of physical properties such as position, momentum,
spin, and polarization performed on entangled particles can, in some cases, be found
to be perfectly correlated.
"""

LONG_TEXT = """
Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the
natural intelligence displayed by humans and animals. Leading AI textbooks define the field
as the study of intelligent agents: any device that perceives its environment and takes
actions that maximize its chance of successfully achieving its goals. Colloquially, the term
artificial intelligence is often used to describe machines that mimic cognitive functions that
humans associate with the human mind, such as learning and problem solving.

As machines become increasingly capable, tasks considered to require intelligence are often
removed from the definition of AI, a phenomenon known as the AI effect. A quip in Tesler's
Theorem says AI is whatever hasn't been done yet. For instance, optical character recognition
is frequently excluded from things considered to be AI, having become a routine technology.
Modern machine capabilities generally classified as AI include successfully understanding
human speech, competing at the highest level in strategic game systems, autonomously operating
cars, intelligent routing in content delivery networks, and military simulations.
"""


def test_basic_summarization():
    """Test basic summarization"""
    print("\n" + "=" * 70)
    print("TEST 1: Basic Summarization")
    print("=" * 70)

    print("\n[Test 1.1] Initialize summarizer")
    summarizer = ContentSummarizer()
    print(f"Model: {summarizer.model_name}")
    print(f"Device: {summarizer.device_id}")
    print("✅ Summarizer initialized")

    print("\n[Test 1.2] Summarize sample text")
    summary = summarizer.summarize(SAMPLE_TEXT)
    print(f"Original length: {len(SAMPLE_TEXT)} chars")
    print(f"Summary length: {len(summary)} chars")
    print(f"Summary: {summary}")

    assert len(summary) > 0, "Summary is empty"
    assert len(summary) < len(SAMPLE_TEXT), "Summary should be shorter than original"
    print("✅ Summary generated successfully")


def test_multiple_texts():
    """Test summarizing multiple texts"""
    print("\n" + "=" * 70)
    print("TEST 2: Multiple Text Summarization")
    print("=" * 70)

    summarizer = ContentSummarizer()
    texts = [SAMPLE_TEXT, LONG_TEXT]

    print("\n[Test 2.1] Summarize multiple texts (combine=True)")
    summary = summarizer.summarize_multiple(texts, combine=True)
    print(f"Combined summary length: {len(summary)} chars")
    print(f"Summary (first 200 chars): {summary[:200]}...")
    assert len(summary) > 0, "Combined summary is empty"
    print("✅ Combined summarization successful")

    print("\n[Test 2.2] Summarize multiple texts (combine=False)")
    summary = summarizer.summarize_multiple(texts, combine=False)
    print(f"Individual summaries length: {len(summary)} chars")
    print(f"Summary (first 200 chars): {summary[:200]}...")
    assert len(summary) > 0, "Individual summaries are empty"
    print("✅ Individual summarization successful")


def test_research_papers():
    """Test summarizing research papers"""
    print("\n" + "=" * 70)
    print("TEST 3: Research Paper Summarization")
    print("=" * 70)

    summarizer = ContentSummarizer()

    # Mock paper data
    papers = [
        {
            "title": "Quantum Entanglement in Multi-Particle Systems",
            "authors": ["John Doe", "Jane Smith", "Bob Johnson"],
            "summary": SAMPLE_TEXT
        },
        {
            "title": "Introduction to Artificial Intelligence",
            "authors": ["Alice Brown", "Charlie Davis"],
            "summary": LONG_TEXT
        }
    ]

    print("\n[Test 3.1] Summarize research papers with metadata")
    summary = summarizer.summarize_research_papers(papers, include_metadata=True)
    print(f"Paper summaries length: {len(summary)} chars")
    print(f"Summary (first 300 chars):\n{summary[:300]}...")

    assert "Paper 1" in summary, "Paper numbering missing"
    assert "Paper 2" in summary, "Paper numbering missing"
    assert "Authors:" in summary, "Author metadata missing"
    print("✅ Research paper summarization with metadata successful")

    print("\n[Test 3.2] Summarize research papers without metadata")
    summary = summarizer.summarize_research_papers(papers, include_metadata=False)
    print(f"Paper summaries (no metadata) length: {len(summary)} chars")
    assert len(summary) > 0, "Summary without metadata is empty"
    print("✅ Research paper summarization without metadata successful")


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "=" * 70)
    print("TEST 4: Edge Cases")
    print("=" * 70)

    summarizer = ContentSummarizer()

    print("\n[Test 4.1] Empty text")
    summary = summarizer.summarize("")
    print(f"Empty text summary: '{summary}'")
    assert summary == "", "Empty text should return empty summary"
    print("✅ Empty text handled correctly")

    print("\n[Test 4.2] Very short text")
    short_text = "Quantum entanglement is a physical phenomenon."
    summary = summarizer.summarize(short_text)
    print(f"Short text: {short_text}")
    print(f"Summary: {summary}")
    assert len(summary) > 0, "Short text summary is empty"
    print("✅ Short text handled correctly")

    print("\n[Test 4.3] Custom length parameters")
    summary = summarizer.summarize(SAMPLE_TEXT, max_length=50, min_length=20)
    print(f"Custom length summary: {summary}")
    assert len(summary) > 0, "Custom length summary is empty"
    print("✅ Custom length parameters work")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("SUMMARIZATION - TEST SUITE")
    print("=" * 70)
    print("\nNOTE: First run will download the summarization model (~1.6GB)")
    print("This may take a few minutes. Subsequent runs will be faster.")
    print("=" * 70)

    try:
        test_basic_summarization()
        test_multiple_texts()
        test_research_papers()
        test_edge_cases()

        print("\n" + "=" * 70)
        print("🎉 ALL SUMMARIZATION TESTS PASSED!")
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
