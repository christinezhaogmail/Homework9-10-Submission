#!/usr/bin/env python3
"""
Run Script - Easy launcher for Research Assistant
Choose how you want to run the application
"""

import sys
import subprocess
import os

def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                       Research Assistant                              ║
║                      Easy Launcher                                ║
╚═══════════════════════════════════════════════════════════════════╝
""")

def check_ollama():
    """Check if Ollama is running"""
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print_banner()

    # Check if Ollama is running
    if not check_ollama():
        print("⚠️  WARNING: Ollama does not appear to be running!")
        print("   Please start Ollama with: ollama serve")
        print("   Then rerun this script.\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("✅ Ollama is running\n")

    print("Choose how you want to run the Research Assistant:\n")
    print("1. Quick Start CLI (Interactive command-line)")
    print("2. Streamlit Web Interface (Recommended)")
    print("3. FastAPI Backend Only")
    print("4. Run Tests")
    print("5. Exit\n")

    choice = input("Enter your choice (1-5): ").strip()

    print("")

    if choice == "1":
        print("Starting Quick Start CLI...")
        print("─" * 70)
        subprocess.run([sys.executable, "quick_start.py"])

    elif choice == "2":
        print("Starting Streamlit Web Interface...")
        print("The interface will open in your browser at: http://localhost:8501")
        print("─" * 70)
        subprocess.run(["streamlit", "run", "frontend.py"])

    elif choice == "3":
        print("Starting FastAPI Backend...")
        print("API will be available at: http://localhost:8000")
        print("API docs at: http://localhost:8000/docs")
        print("─" * 70)
        subprocess.run([sys.executable, "backend.py"])

    elif choice == "4":
        print("Running comprehensive test suite...")
        print("─" * 70)
        subprocess.run([sys.executable, "test_agent.py"])

    elif choice == "5":
        print("Goodbye! 👋")
        sys.exit(0)

    else:
        print("❌ Invalid choice. Please run the script again.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye! 👋")
        sys.exit(0)
