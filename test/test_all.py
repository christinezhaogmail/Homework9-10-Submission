"""
Master Test Runner
Runs all component tests in sequence
"""

import sys
import subprocess
from pathlib import Path
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


def run_test(test_file: str) -> bool:
    """Run a single test file and return success status"""
    print(f"\n{'='*70}")
    print(f"Running: {test_file}")
    print(f"{'='*70}\n")

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_file} FAILED")
        return False
    except Exception as e:
        print(f"\n❌ Error running {test_file}: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("AI RESEARCH ASSISTANT - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    # Get test directory
    test_dir = Path(__file__).parent

    # Define test files in order of execution
    test_files = [
        "test_hardware.py",
        "test_api_models.py",
        "test_session_manager.py",
        "test_search.py",
        "test_summarize.py",
        "test_notion.py",
    ]

    # Track results
    results = {}

    # Run each test
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            success = run_test(str(test_path))
            results[test_file] = success
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results[test_file] = False

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for success in results.values() if success)
    total = len(results)

    for test_file, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_file}")

    print("\n" + "=" * 70)
    if passed == total:
        print(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
        print("=" * 70)
        print("\nYour AI Research Assistant is ready to use!")
        print("\nNext steps:")
        print("1. Set up environment variables (see .env.example)")
        print("2. Start the backend: python backend.py")
        print("3. Start the frontend: streamlit run frontend.py")
        sys.exit(0)
    else:
        print(f"⚠️  {total - passed} TEST(S) FAILED ({passed}/{total} passed)")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
