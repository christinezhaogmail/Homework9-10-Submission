"""
Test script for multi-step agent with search_arxiv -> summarize flow
"""

import requests
import json
from loguru import logger

# Configure logger
logger.add("test_multistep_agent.log", rotation="1 day", level="INFO")

def test_arxiv_query():
    """
    Test the multi-step agent with an arXiv query
    Expected flow:
    1. User asks about quantum entanglement
    2. Agent calls search_arxiv
    3. Agent receives results
    4. Agent calls summarize on the results
    5. User gets summarized answer
    """

    # API endpoint
    url = "http://localhost:8000/api/text-query/"

    # Test query
    query = "What is quantum entanglement?"

    logger.info(f"Testing multi-step agent with query: {query}")
    print(f"\n{'='*60}")
    print(f"TEST: Multi-Step Agent (search_arxiv -> summarize)")
    print(f"{'='*60}")
    print(f"Query: {query}\n")

    try:
        # Send request
        response = requests.post(
            url,
            json={"text": query, "include_audio": False},
            timeout=120  # Allow more time for multi-step execution
        )

        response.raise_for_status()
        result = response.json()

        # Display results
        print(f"✓ Request successful!")
        print(f"\nResults:")
        print(f"  Success: {result['success']}")
        print(f"  Function Call Made: {result['is_function_call']}")
        if result['is_function_call']:
            print(f"  First Function: {result['function_name']}")
            print(f"  Function Args: {result['function_args']}")
        print(f"  Processing Time: {result['processing_time']:.2f}s")
        print(f"\nFinal Response:")
        print(f"  {result['response_text']}")
        print(f"\n{'='*60}\n")

        logger.info(f"Test completed successfully")
        logger.info(f"Response: {result['response_text'][:200]}...")

        return result

    except requests.exceptions.ConnectionError:
        error_msg = "Error: Cannot connect to API server. Make sure the backend is running on http://localhost:8000"
        print(f"\n✗ {error_msg}\n")
        logger.error(error_msg)
        return None

    except requests.exceptions.Timeout:
        error_msg = "Error: Request timed out"
        print(f"\n✗ {error_msg}\n")
        logger.error(error_msg)
        return None

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"\n✗ {error_msg}\n")
        logger.error(error_msg)
        return None


def test_calculation_query():
    """Test that simple calculations still work (single-step)"""

    url = "http://localhost:8000/api/text-query/"
    query = "What is 15 plus 27?"

    logger.info(f"Testing calculation query: {query}")
    print(f"\n{'='*60}")
    print(f"TEST: Single-Step Agent (calculate)")
    print(f"{'='*60}")
    print(f"Query: {query}\n")

    try:
        response = requests.post(
            url,
            json={"text": query, "include_audio": False},
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        print(f"✓ Request successful!")
        print(f"\nResults:")
        print(f"  Success: {result['success']}")
        print(f"  Function Call Made: {result['is_function_call']}")
        if result['is_function_call']:
            print(f"  Function: {result['function_name']}")
        print(f"  Processing Time: {result['processing_time']:.2f}s")
        print(f"\nFinal Response:")
        print(f"  {result['response_text']}")
        print(f"\n{'='*60}\n")

        logger.info(f"Calculation test completed successfully")
        return result

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"\n✗ {error_msg}\n")
        logger.error(error_msg)
        return None


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MULTI-STEP AGENT TESTING")
    print("="*60)
    print("\nMake sure the backend server is running:")
    print("  python backend.py")
    print("\nAnd Ollama is running with your model:")
    print("  ollama serve")
    print("="*60 + "\n")

    # Test 1: Multi-step arXiv query
    result1 = test_arxiv_query()

    # Test 2: Single-step calculation
    result2 = test_calculation_query()

    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)

    if result1 and result2:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed. Check the logs for details.")
