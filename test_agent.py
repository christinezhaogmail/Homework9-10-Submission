"""
Test script for the AI Voice Agent
Tests all components: tools, LLM, routing, and integration
"""

import sys
from loguru import logger

# Configure logger for testing
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

from llm_service import LLMService
from function_router import FunctionRouter
from agent_tools import calculate, search_arxiv


def test_tools():
    """Test individual tools"""
    print("\n" + "=" * 70)
    print("TEST 1: Testing Tools Directly")
    print("=" * 70)

    # Test calculate tool
    print("\n[Test 1.1] Calculate: 2+2")
    result = calculate.invoke({"expression": "2+2"})
    print(f"Result: {result}")
    assert "4" in result, "Calculate test failed"

    print("\n[Test 1.2] Calculate: sqrt(16)")
    result = calculate.invoke({"expression": "sqrt(16)"})
    print(f"Result: {result}")
    assert "4" in result, "Calculate sqrt test failed"

    print("\n[Test 1.3] Calculate: 1/0 (error handling)")
    result = calculate.invoke({"expression": "1/0"})
    print(f"Result: {result}")
    assert "Error" in result or "undefined" in result, "Division by zero handling failed"

    print("\n[Test 1.4] Search arXiv: quantum entanglement")
    result = search_arxiv.invoke({"query": "quantum entanglement", "limit": 2})
    print(f"Result (first 200 chars): {result[:200]}...")
    assert len(result) > 0, "arXiv search test failed"

    print("\n✅ All tool tests passed!")


def test_llm_service():
    """Test LLM service"""
    print("\n" + "=" * 70)
    print("TEST 2: Testing LLM Service")
    print("=" * 70)

    llm = LLMService()

    print("\n[Test 2.1] Math query: What is 15 plus 27?")
    response = llm.generate_response("What is 15 plus 27?")
    print(f"LLM Response: {response}")

    print("\n[Test 2.2] Search query: What is quantum entanglement?")
    response = llm.generate_response("What is quantum entanglement?")
    print(f"LLM Response: {response}")

    print("\n[Test 2.3] General query: Hello, how are you?")
    response = llm.generate_response("Hello, how are you?")
    print(f"LLM Response: {response}")

    print("\n✅ LLM service tests completed!")


def test_function_router():
    """Test function routing"""
    print("\n" + "=" * 70)
    print("TEST 3: Testing Function Router")
    print("=" * 70)

    router = FunctionRouter()

    print("\n[Test 3.1] Route function call: calculate")
    llm_output = '{"function": "calculate", "arguments": {"expression": "25*4"}}'
    result = router.route_llm_output(llm_output)
    print(f"Result: {result}")
    assert result['is_function_call'], "Function call detection failed"
    assert result['function_name'] == 'calculate', "Function name extraction failed"
    assert '100' in result['response'], "Calculate execution failed"

    print("\n[Test 3.2] Route function call: search_arxiv")
    llm_output = '{"function": "search_arxiv", "arguments": {"query": "machine learning", "limit": 2}}'
    result = router.route_llm_output(llm_output)
    print(f"Result (is_function_call): {result['is_function_call']}")
    print(f"Result (function_name): {result['function_name']}")
    print(f"Result (response length): {len(result['response'])}")
    assert result['is_function_call'], "Function call detection failed"
    assert result['function_name'] == 'search_arxiv', "Function name extraction failed"

    print("\n[Test 3.3] Route regular text")
    llm_output = "Hello! How can I help you today?"
    result = router.route_llm_output(llm_output)
    print(f"Result: {result}")
    assert not result['is_function_call'], "False positive function call"
    assert result['response'] == llm_output, "Text passthrough failed"

    print("\n✅ Function router tests passed!")


def test_end_to_end():
    """Test end-to-end integration"""
    print("\n" + "=" * 70)
    print("TEST 4: End-to-End Integration Tests")
    print("=" * 70)

    llm = LLMService()
    router = FunctionRouter()

    test_queries = [
        "What is 100 divided by 5?",
        "Search for papers on neural networks",
        "Tell me a joke"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test 4.{i}] Query: {query}")
        print("-" * 70)

        # Get LLM response
        llm_response = llm.generate_response(query)
        print(f"LLM Response: {llm_response}")

        # Route the response
        result = router.route_llm_output(llm_response)
        print(f"Is Function Call: {result['is_function_call']}")
        if result['is_function_call']:
            print(f"Function: {result['function_name']}")
            print(f"Arguments: {result['function_args']}")
        print(f"Final Response (first 200 chars): {result['response'][:200]}...")

    print("\n✅ End-to-end tests completed!")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("AI VOICE AGENT - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    try:
        # Run all tests
        test_tools()
        test_llm_service()
        test_function_router()
        test_end_to_end()

        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 70)
        print("\nThe AI Voice Agent is ready to use.")
        print("\nNext steps:")
        print("1. Start the FastAPI backend: python backend.py")
        print("2. Start the Streamlit frontend: streamlit run frontend.py")
        print("3. Or use the test commands in the README.md")
        print("\n" + "=" * 70)

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FAILED: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
