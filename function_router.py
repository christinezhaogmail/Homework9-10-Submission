"""
Function Router: Parse LLM output and route to appropriate tools
Handles function call detection and execution
"""

import json
import re
from typing import Dict, Any, Tuple
from loguru import logger
from agent_tools import TOOL_REGISTRY


class FunctionRouter:
    """
    Routes LLM outputs to appropriate tool functions
    Handles both function calls and regular text responses
    """

    def __init__(self):
        """Initialize the function router with tool registry"""
        self.tool_registry = TOOL_REGISTRY
        logger.info(f"Function router initialized with tools: {list(self.tool_registry.keys())}")

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

            logger.info(f"Function executed successfully. Result length: {len(str(result))}")
            return str(result)

        except Exception as e:
            error_msg = f"Error executing function '{function_name}': {str(e)}"
            logger.error(error_msg)
            return error_msg

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
        """
        logger.info("Routing LLM output...")

        result = {
            "response": "",
            "is_function_call": False,
            "function_name": None,
            "function_args": None,
            "raw_llm_output": llm_output
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
            else:
                result["response"] = "Error: Could not parse function call"

        else:
            # It's a regular text response
            logger.info("Regular text response detected")
            result["response"] = llm_output

        return result


if __name__ == "__main__":
    # Test the function router
    router = FunctionRouter()

    print("Test 1: Function call - calculate")
    test_output = '{"function": "calculate", "arguments": {"expression": "2+2"}}'
    result = router.route_llm_output(test_output)
    print(f"Result: {result}\n")

    print("Test 2: Function call - search_arxiv")
    test_output = '{"function": "search_arxiv", "arguments": {"query": "quantum entanglement", "limit": 2}}'
    result = router.route_llm_output(test_output)
    print(f"Result: {result}\n")

    print("Test 3: Regular text")
    test_output = "Hello! How can I help you today?"
    result = router.route_llm_output(test_output)
    print(f"Result: {result}\n")

    print("Test 4: Unknown function")
    test_output = '{"function": "unknown_func", "arguments": {}}'
    result = router.route_llm_output(test_output)
    print(f"Result: {result}\n")
