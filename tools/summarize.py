"""
Summarization Module: ContentSummarizer using HuggingFace Pipeline
Condenses research papers and long text into concise summaries
"""

from typing import List, Optional
from loguru import logger
from utils.logger import log_tool_call
from utils.hardware import get_device

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.error("Transformers not available. Install with: pip install transformers")


class ContentSummarizer:
    """
    Summarization service using HuggingFace transformers pipeline.
    Condenses long text passages into concise summaries.
    """

    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn",
        device: Optional[str] = None,
        max_length: int = 150,
        min_length: int = 50
    ):
        """
        Initialize the content summarizer.

        Args:
            model_name: HuggingFace model for summarization (default: facebook/bart-large-cnn)
            device: Target device (None=auto-detect, cuda/mps/cpu)
            max_length: Maximum summary length in tokens
            min_length: Minimum summary length in tokens
        """
        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError("Transformers not available. Install with: pip install transformers")

        self.model_name = model_name
        self.max_length = max_length
        self.min_length = min_length
        self.device_id = self._get_device_id(device)
        self.summarizer = None

        logger.info(f"Initializing ContentSummarizer: model={model_name}, device={self.device_id}")
        self._load_model()

    def _get_device_id(self, device: Optional[str] = None) -> int:
        """
        Convert device string to device ID for transformers pipeline.

        Args:
            device: Device string (None=auto-detect)

        Returns:
            Device ID: 0 for GPU, -1 for CPU
        """
        if device is None:
            device = get_device()

        # Transformers pipeline uses: 0 for GPU (CUDA/MPS), -1 for CPU
        if device in ["cuda", "mps"]:
            return 0
        else:
            return -1

    def _load_model(self):
        """Load the summarization model"""
        try:
            self.summarizer = pipeline(
                "summarization",
                model=self.model_name,
                device=self.device_id
            )
            logger.info(f"✓ Summarization model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
            raise

    @log_tool_call
    def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None
    ) -> str:
        """
        Summarize a single text passage.

        Args:
            text: Text to summarize
            max_length: Override default max_length
            min_length: Override default min_length

        Returns:
            Summarized text
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for summarization")
            return ""

        try:
            max_len = max_length or self.max_length
            min_len = min_length or self.min_length

            # Ensure min_length is less than max_length
            min_len = min(min_len, max_len - 10)

            result = self.summarizer(
                text,
                max_length=max_len,
                min_length=min_len,
                do_sample=False,
                truncation=True
            )

            summary = result[0]['summary_text']
            logger.info(f"Summary generated ({len(summary)} chars from {len(text)} chars)")
            return summary

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            # Return truncated original text as fallback
            return text[:self.max_length * 4] + "..." if len(text) > self.max_length * 4 else text

    @log_tool_call
    def summarize_multiple(
        self,
        texts: List[str],
        combine: bool = True
    ) -> str:
        """
        Summarize multiple text passages.

        Args:
            texts: List of texts to summarize
            combine: If True, combine and summarize together; if False, summarize individually then combine

        Returns:
            Combined summary
        """
        if not texts:
            logger.warning("Empty text list provided for summarization")
            return ""

        try:
            if combine:
                # Combine all texts and summarize once
                combined_text = "\n\n".join(texts)
                return self.summarize(combined_text)
            else:
                # Summarize each individually then combine
                summaries = [self.summarize(text) for text in texts]
                return "\n\n".join(summaries)

        except Exception as e:
            logger.error(f"Multiple text summarization failed: {e}")
            return "Error generating summary."

    @log_tool_call
    def summarize_research_papers(
        self,
        papers: List[dict],
        include_metadata: bool = True
    ) -> str:
        """
        Summarize research papers from ArXiv search results.

        Args:
            papers: List of paper dictionaries with 'title', 'summary', 'authors', etc.
            include_metadata: Include paper metadata in summary

        Returns:
            Formatted summary of research papers
        """
        if not papers:
            return "No papers to summarize."

        try:
            summaries = []

            for i, paper in enumerate(papers, 1):
                title = paper.get('title', 'Unknown Title')
                abstract = paper.get('summary', '')

                # Summarize the abstract
                if abstract:
                    paper_summary = self.summarize(abstract, max_length=100, min_length=30)
                else:
                    paper_summary = "No abstract available."

                if include_metadata:
                    authors = paper.get('authors', [])
                    author_str = ', '.join(str(a) for a in authors[:3])
                    if len(authors) > 3:
                        author_str += f" et al. ({len(authors)} total)"

                    formatted = f"**Paper {i}: {title}**\n"
                    formatted += f"Authors: {author_str}\n"
                    formatted += f"Summary: {paper_summary}"
                    summaries.append(formatted)
                else:
                    summaries.append(f"{i}. {title}: {paper_summary}")

            result = "\n\n".join(summaries)
            logger.info(f"Summarized {len(papers)} research papers")
            return result

        except Exception as e:
            logger.error(f"Research paper summarization failed: {e}")
            return f"Error summarizing papers: {str(e)}"


if __name__ == "__main__":
    # Test the summarizer
    print("ContentSummarizer Test")
    print("-" * 50)

    summarizer = ContentSummarizer()
    print(f"Model: {summarizer.model_name}")
    print(f"Device: {summarizer.device_id}")

    # Test with sample text
    test_text = """
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

    print("\nOriginal text length:", len(test_text))
    summary = summarizer.summarize(test_text)
    print("\nSummary:")
    print(summary)
    print("\nSummary length:", len(summary))
