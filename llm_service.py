"""
LLM Service: Integration with Ollama/my-lama3-finetuned-Q4_K_M
Handles LLM interactions with function calling support
"""

import json
from typing import Dict, Any, Optional
import requests
from loguru import logger
from config import Config


class LLMService:
    """
    Service for interacting with LLM (Ollama/my-lama3-finetuned-Q4_K_M)
    Supports function calling through structured prompts
    """

    def __init__(self, model: str = "my-lama3-finetuned-Q4_K_M", base_url: str = "http://localhost:11434"):
        """
        Initialize the LLM service

        Args:
            model: The model name to use (default: my-lama3-finetuned-Q4_K_M)
            base_url: The Ollama API base URL
        """
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        logger.info(f"Initialized LLM service with model: {model}")

    def get_system_prompt(self) -> str:
        """
        Get the system prompt that teaches the model to use function calling

        Returns:
            The system prompt string
        """
        # Get the arxiv limit from config
        arxiv_limit = Config.ARXIV_MAX_RESULTS

        return f"""You are a helpful AI assistant with access to tools. You can help users with:
1. Searching scientific papers on arXiv
2. Performing mathematical calculations
3. Summarizing text passages

When a user asks a question:
- If they want to search for scientific papers, academic research, or information about a specific topic that requires research, respond with a JSON function call to search_arxiv.
- If they want to perform a mathematical calculation, respond with a JSON function call to calculate.
- If you receive search results that are long or complex, call summarize to create a concise summary for the user.
- For general conversation or questions that don't require tools, respond normally with text.

Function call format (respond ONLY with the JSON, no additional text):
{{"function": "search_arxiv", "arguments": {{"query": "your search query", "limit": {arxiv_limit}}}}}
{{"function": "calculate", "arguments": {{"expression": "mathematical expression"}}}}
{{"function": "summarize", "arguments": {{"texts": ["text passage 1", "text passage 2"]}}}}

Examples:
User: "What is quantum entanglement?"
Response: {{"function": "search_arxiv", "arguments": {{"query": "quantum entanglement", "limit": {arxiv_limit}}}}}

Tool Result: [Long arXiv search results]
Response: {{"function": "summarize", "arguments": {{"texts": ["summary text from papers"]}}}}

User: "What is 25 multiplied by 4?"
Response: {{"function": "calculate", "arguments": {{"expression": "25*4"}}}}

User: "Hello, how are you?"
Response: Hello! I'm doing well, thank you for asking. How can I help you today?

Important rules:
- For research/scientific questions, FIRST use search_arxiv to find papers
- After receiving arXiv search results, use summarize to condense the information for the user
- For math problems, use calculate
- For general chat, respond normally
- When using a function, respond ONLY with the JSON, nothing else
- Be helpful and friendly
"""

    def generate_response(self, user_message: str, conversation_history: Optional[list] = None, use_full_prompt: bool = False) -> str:
        """
        Generate a response from the LLM

        Args:
            user_message: The user's message or full conversation context
            conversation_history: Optional list of previous messages (not currently used)
            use_full_prompt: If True, user_message is treated as a complete prompt; if False, system prompt is prepended

        Returns:
            The LLM's response (either function call JSON or text)
        """
        try:
            # Build the full prompt
            if use_full_prompt:
                # user_message already contains the full conversation context
                full_prompt = f"{self.get_system_prompt()}\n\n{user_message}"
            else:
                # Simple query - add system prompt and format
                full_prompt = f"{self.get_system_prompt()}\n\nUser: {user_message}\nAssistant:"

            # Prepare the request payload
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "temperature": 0.7,
            }

            logger.info(f"Sending request to LLM (use_full_prompt={use_full_prompt})")
            logger.debug(f"Prompt preview: {full_prompt[:200]}...")

            # Make the API request
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()

            # Parse the response
            result = response.json()
            llm_output = result.get("response", "").strip()

            logger.info(f"LLM raw response: {llm_output[:200]}...")

            return llm_output

        except requests.exceptions.ConnectionError:
            error_msg = "Error: Cannot connect to Ollama. Make sure Ollama is running with 'ollama serve'"
            logger.error(error_msg)
            return error_msg
        except requests.exceptions.Timeout:
            error_msg = "Error: Request to LLM timed out"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error generating LLM response: {str(e)}"
            logger.error(error_msg)
            return error_msg


class AlternativeLLMService:
    """
    Alternative LLM service that can be used with OpenAI or other providers
    Demonstrates flexibility for future LLM integration
    """

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize with OpenAI API

        Args:
            api_key: OpenAI API key
            model: Model name
        """
        self.api_key = api_key
        self.model = model
        logger.info(f"Initialized alternative LLM service with model: {model}")

    def generate_response(self, user_message: str) -> str:
        """
        Generate response using OpenAI API
        """
        try:
            import openai
            openai.api_key = self.api_key

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": LLMService(None).get_system_prompt()},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            error_msg = f"Error with alternative LLM: {str(e)}"
            logger.error(error_msg)
            return error_msg


if __name__ == "__main__":
    # Test the LLM service
    llm = LLMService()

    print("Testing LLM with math question:")
    response = llm.generate_response("What is 15 plus 27?")
    print(f"Response: {response}\n")

    print("Testing LLM with arXiv search:")
    response = llm.generate_response("What is quantum entanglement?")
    print(f"Response: {response}\n")

    print("Testing LLM with general question:")
    response = llm.generate_response("Hello, how are you?")
    print(f"Response: {response}\n")
