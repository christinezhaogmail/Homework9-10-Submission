"""
Quick Start Script for Research Assistant
Interactive command-line interface for testing the agent
"""

import sys
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="WARNING", format="<level>{level: <8}</level> | {message}")

from llm_service import LLMService
from function_router import FunctionRouter
from audio_service import VoiceAgentAudio

print("""
╔═══════════════════════════════════════════════════════════════════╗
║                    Research Assistant - QUICK START                   ║
╚═══════════════════════════════════════════════════════════════════╝

Welcome! This is a quick command-line interface to test the voice agent.

Features:
  🔢 Mathematical calculations
  📚 arXiv paper search
  💬 General conversation

Type your queries below or use these examples:
  - "What is 25 multiplied by 4?"
  - "What is quantum entanglement?"
  - "Hello, how are you?"

Commands:
  - Type 'quit' or 'exit' to quit
  - Type 'help' for more information
  - Type 'examples' to see example queries

""")

# Initialize services
print("Initializing services...")
try:
    llm = LLMService()
    router = FunctionRouter()
    voice_agent = VoiceAgentAudio()
    print("✅ All services initialized successfully!\n")
except Exception as e:
    print(f"❌ Error initializing services: {e}")
    print("\nMake sure:")
    print("1. Ollama is running: ollama serve")
    print("2. Llama3.2 is installed: ollama pull llama3.2")
    print("3. Dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Greet user with voice
print("🔊 Speaking greeting...")
voice_agent.greet_user()


def show_help():
    """Show help information"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                              HELP                                 ║
╚═══════════════════════════════════════════════════════════════════╝

The Research Assistant can:
1. Perform mathematical calculations using SymPy
2. Search for scientific papers on arXiv
3. Have general conversations

How it works:
1. You type a query
2. The LLM (Llama3.2) analyzes your query
3. If needed, it calls a tool (calculate or search_arxiv)
4. The response is displayed and optionally spoken

Available commands:
  - help: Show this help message
  - examples: Show example queries
  - quit/exit: Exit the program
  - clear: Clear the screen

""")


def show_examples():
    """Show example queries"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                          EXAMPLE QUERIES                          ║
╚═══════════════════════════════════════════════════════════════════╝

📊 Mathematical Calculations:
  - What is 15 plus 27?
  - Calculate the square root of 144
  - What is 100 divided by 5?
  - Compute 2 to the power of 10
  - What is 1 divided by 0? (tests error handling)

📚 arXiv Paper Search:
  - What is quantum entanglement?
  - Search for papers on neural networks
  - Find research about climate change
  - Show me papers on large language models
  - What are transformers in machine learning?

💬 General Conversation:
  - Hello, how are you?
  - Tell me about yourself
  - What can you do?
  - Thank you for your help

""")


def process_query(query: str):
    """Process a user query"""
    print(f"\n{'='*70}")
    print(f"📝 Query: {query}")
    print(f"{'='*70}\n")

    # Acknowledge
    print("🤔 Processing...")

    # Get LLM response
    llm_output = llm.generate_response(query)
    print(f"🧠 LLM Output: {llm_output}\n")

    # Route and execute
    result = router.route_llm_output(llm_output)

    # Display results
    if result['is_function_call']:
        print(f"⚡ Function Call Detected!")
        print(f"   Function: {result['function_name']}")
        print(f"   Arguments: {result['function_args']}\n")
        voice_agent.acknowledge_processing()
        voice_agent.announce_result()

    print(f"💬 Response:")
    print(f"{'─'*70}")
    print(result['response'])
    print(f"{'─'*70}\n")

    # Speak response (for short responses)
    if len(result['response']) < 500:
        print("🔊 Speaking response...")
        voice_agent.speak_response(result['response'])


def main():
    """Main interactive loop"""
    query_count = 0

    while True:
        try:
            # Get user input
            user_input = input("\n💭 You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Thank you for using the Research Assistant.")
                voice_agent.speak_response("Goodbye! Have a great day!")
                break

            elif user_input.lower() == 'help':
                show_help()
                continue

            elif user_input.lower() == 'examples':
                show_examples()
                continue

            elif user_input.lower() == 'clear':
                print("\033[H\033[J")  # Clear screen
                continue

            # Process the query
            query_count += 1
            process_query(user_input)

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user. Exiting...")
            break

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            logger.exception("Error processing query")

    print(f"\n📊 Total queries processed: {query_count}")
    print("\nTo use the web interface, run: streamlit run frontend.py")


if __name__ == "__main__":
    main()
