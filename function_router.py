"""
Function Router: Parse LLM output and route to appropriate tools
Handles function call detection and execution with workflow tracking
"""

import json
import re
from typing import Dict, Any, Tuple, List
from loguru import logger
from agent_tools import TOOL_REGISTRY
from config import Config


class FunctionRouter:
    """
    Routes LLM outputs to appropriate tool functions
    Handles both function calls and regular text responses
    Tracks arXiv queries and automatically triggers summarization after 3 queries
    """

    def __init__(self):
        """Initialize the function router with tool registry and session tracking"""
        self.tool_registry = TOOL_REGISTRY

        # Session tracking for workflow automation
        self.arxiv_query_count = 0
        self.arxiv_results: List[str] = []
        self.session_content: List[str] = []
        self.auto_save_threshold = Config.AUTO_SAVE_THRESHOLD  # Get from config

        logger.info(f"Function router initialized with tools: {list(self.tool_registry.keys())}")
        logger.info(f"Auto-save will trigger after {self.auto_save_threshold} arXiv queries")

    def is_function_call(self, llm_output: str) -> bool:
        """
        Check if the LLM output is a function call

        Args:
            llm_output: The raw output from the LLM

        Returns:
            True if it's a function call, False otherwise
        """
        try:
            # Try to parse as JSON
            parsed = json.loads(llm_output.strip())
            return "function" in parsed and "arguments" in parsed
        except (json.JSONDecodeError, TypeError):
            # Try to extract JSON from text
            json_match = re.search(r'\{[^{}]*"function"[^{}]*"arguments"[^{}]*\}', llm_output)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    return "function" in parsed and "arguments" in parsed
                except:
                    return False
            return False

    def extract_function_call(self, llm_output: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extract function name and arguments from LLM output

        Args:
            llm_output: The raw output from the LLM

        Returns:
            Tuple of (function_name, arguments_dict)
        """
        try:
            # First try direct JSON parsing
            try:
                parsed = json.loads(llm_output.strip())
            except json.JSONDecodeError:
                # Try to extract JSON from text
                json_match = re.search(r'\{[^{}]*"function"[^{}]*"arguments"[^{}]*\}', llm_output)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON function call found")

            function_name = parsed.get("function", "")
            arguments = parsed.get("arguments", {})

            logger.info(f"Extracted function call: {function_name} with args: {arguments}")
            return function_name, arguments

        except Exception as e:
            logger.error(f"Error extracting function call: {e}")
            return "", {}

    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute the specified function with given arguments

        Args:
            function_name: Name of the function to execute
            arguments: Dictionary of arguments to pass

        Returns:
            The function's output as a string
        """
        try:
            # Check if function exists in registry
            if function_name not in self.tool_registry:
                error_msg = f"Error: Unknown function '{function_name}'. Available functions: {list(self.tool_registry.keys())}"
                logger.error(error_msg)
                return error_msg

            # Get the tool function
            tool_func = self.tool_registry[function_name]

            # Execute the function
            logger.info(f"Executing function: {function_name}")
            result = tool_func.invoke(arguments)

            # Track arXiv queries for workflow automation
            if function_name == "search_arxiv":
                self.arxiv_query_count += 1
                self.arxiv_results.append(str(result))
                self.session_content.append(f"Query {self.arxiv_query_count}: {arguments.get('query', 'N/A')}")
                logger.info(f"arXiv query count: {self.arxiv_query_count}/{self.auto_save_threshold}")

            logger.info(f"Function executed successfully. Result length: {len(str(result))}")
            return str(result)

        except Exception as e:
            error_msg = f"Error executing function '{function_name}': {str(e)}"
            logger.error(error_msg)
            return error_msg

    def should_trigger_auto_save(self) -> bool:
        """
        Check if auto-save should be triggered

        Returns:
            True if threshold is reached, False otherwise
        """
        return self.arxiv_query_count >= self.auto_save_threshold

    def trigger_auto_save(self) -> str:
        """
        Trigger automatic summarization and save to Notion

        Returns:
            Result message from the summarize_and_save function
        """
        try:
            logger.info("Triggering auto-save workflow...")

            # Prepare session content
            full_session_content = "\n".join(self.session_content)
            all_papers = "\n---\n".join(self.arxiv_results)

            # Call summarize_and_save
            summarize_func = self.tool_registry.get("summarize_and_save")
            if not summarize_func:
                return "Error: summarize_and_save function not available"

            result = summarize_func.invoke({
                "session_content": full_session_content,
                "arxiv_papers": all_papers,
                "query_count": self.arxiv_query_count
            })

            # Reset session tracking after save
            self.reset_session()

            return str(result)

        except Exception as e:
            error_msg = f"Error during auto-save: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def reset_session(self):
        """Reset session tracking variables"""
        logger.info("Resetting session tracking")
        self.arxiv_query_count = 0
        self.arxiv_results = []
        self.session_content = []

    def route_llm_output(self, llm_output: str) -> Dict[str, Any]:
        """
        Main routing function: Process LLM output and return response

        Args:
            llm_output: The raw output from the LLM

        Returns:
            Dictionary with:
                - response: The final response text
                - is_function_call: Boolean indicating if a function was called
                - function_name: Name of function called (if any)
                - function_args: Arguments passed to function (if any)
                - raw_llm_output: The original LLM output
                - auto_save_triggered: Boolean indicating if auto-save was triggered
                - auto_save_result: Result from auto-save (if triggered)
        """
        logger.info("Routing LLM output...")

        result = {
            "response": "",
            "is_function_call": False,
            "function_name": None,
            "function_args": None,
            "raw_llm_output": llm_output,
            "auto_save_triggered": False,
            "auto_save_result": None
        }

        # Check if it's a function call
        if self.is_function_call(llm_output):
            logger.info("Detected function call")
            result["is_function_call"] = True

            # Extract function details
            function_name, arguments = self.extract_function_call(llm_output)
            result["function_name"] = function_name
            result["function_args"] = arguments

            # Execute the function
            if function_name:
                function_output = self.execute_function(function_name, arguments)
                result["response"] = function_output

                # Check if auto-save should be triggered
                if self.should_trigger_auto_save():
                    logger.info("Auto-save threshold reached!")
                    auto_save_result = self.trigger_auto_save()
                    result["auto_save_triggered"] = True
                    result["auto_save_result"] = auto_save_result
                    # Append auto-save result to response
                    result["response"] += f"\n\n{auto_save_result}"
            else:
                result["response"] = "Error: Could not parse function call"

        else:
            # It's a regular text response
            logger.info("Regular text response detected")
            result["response"] = llm_output

        return result


if __name__ == "__main__":
    # Test the function router with auto-save workflow
    router = FunctionRouter()

    print("="*60)
    print("Testing Auto-Save Workflow (3 arXiv queries)")
    print("="*60)

    # Test 1: First arXiv query
    print("\nTest 1: First arXiv query")
    test_output = '{"function": "search_arxiv", "arguments": {"query": "quantum computing", "limit": 2}}'
    result = router.route_llm_output(test_output)
    print(f"Auto-save triggered: {result['auto_save_triggered']}")
    print(f"Query count: {router.arxiv_query_count}/3\n")

    # Test 2: Second arXiv query
    print("Test 2: Second arXiv query")
    test_output = '{"function": "search_arxiv", "arguments": {"query": "machine learning", "limit": 2}}'
    result = router.route_llm_output(test_output)
    print(f"Auto-save triggered: {result['auto_save_triggered']}")
    print(f"Query count: {router.arxiv_query_count}/3\n")

    # Test 3: Third arXiv query (should trigger auto-save)
    print("Test 3: Third arXiv query (should trigger auto-save)")
    test_output = '{"function": "search_arxiv", "arguments": {"query": "neural networks", "limit": 2}}'
    result = router.route_llm_output(test_output)
    print(f"Auto-save triggered: {result['auto_save_triggered']}")
    print(f"Query count after save: {router.arxiv_query_count}/3")
    if result['auto_save_triggered']:
        print(f"\nAuto-save result:\n{result['auto_save_result']}\n")

    # Test 4: Regular text
    print("="*60)
    print("Test 4: Regular text response")
    test_output = "Hello! How can I help you with research today?"
    result = router.route_llm_output(test_output)
    print(f"Response: {result['response']}\n")

    # Test 5: Unknown function
    print("Test 5: Unknown function")
    test_output = '{"function": "unknown_func", "arguments": {}}'
    result = router.route_llm_output(test_output)
    print(f"Response: {result['response']}\n")
