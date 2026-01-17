"""
Test script for Notion Sync Module
Tests Notion API integration for session persistence

NOTE: This test requires NOTION_TOKEN and NOTION_DATABASE_ID environment variables
"""

import sys
import os
from datetime import datetime
from loguru import logger

# Configure logger for testing
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

from tools.notion import NotionSync


def test_notion_initialization():
    """Test Notion client initialization"""
    print("\n" + "=" * 70)
    print("TEST 1: Notion Initialization")
    print("=" * 70)

    print("\n[Test 1.1] Initialize Notion client")
    notion_sync = NotionSync()

    if notion_sync.is_enabled():
        print("✅ Notion client initialized successfully")
        print(f"   Database ID: {notion_sync.database_id[:10]}...")
    else:
        print("⚠️  Notion sync not enabled (missing credentials)")
        print("   Set NOTION_TOKEN and NOTION_DATABASE_ID to enable")
        print("   Tests will be skipped.")
        return False

    return True


def test_session_sync():
    """Test syncing a session to Notion"""
    print("\n" + "=" * 70)
    print("TEST 2: Session Sync")
    print("=" * 70)

    notion_sync = NotionSync()

    if not notion_sync.is_enabled():
        print("⚠️  Skipping test - Notion not configured")
        return

    # Create test data
    session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    content = """User: What is quantum entanglement?
Assistant: Quantum entanglement is a physical phenomenon where particles become correlated.

User: Tell me more about applications.
Assistant: Applications include quantum computing, quantum cryptography, and quantum teleportation."""

    summary = "A conversation about quantum entanglement and its applications."

    print("\n[Test 2.1] Sync session to Notion")
    page_url = notion_sync.sync_session(
        session_id=session_id,
        content=content,
        summary=summary,
        metadata={"query_count": 2, "papers_found": 3}
    )

    if page_url:
        print(f"✅ Session synced successfully")
        print(f"   Notion URL: {page_url}")
    else:
        print("❌ Failed to sync session")
        assert False, "Session sync failed"


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("NOTION SYNC - TEST SUITE")
    print("=" * 70)
    print("\nNOTE: These tests require Notion credentials:")
    print("  - NOTION_TOKEN environment variable")
    print("  - NOTION_DATABASE_ID environment variable")
    print("=" * 70)

    try:
        enabled = test_notion_initialization()

        if enabled:
            test_session_sync()

            print("\n" + "=" * 70)
            print("🎉 ALL NOTION TESTS PASSED!")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("⚠️  NOTION TESTS SKIPPED (credentials not configured)")
            print("=" * 70)
            print("\nTo enable Notion sync:")
            print("1. Create a Notion integration at https://www.notion.so/my-integrations")
            print("2. Share your database with the integration")
            print("3. Set environment variables:")
            print("   export NOTION_TOKEN='your_token_here'")
            print("   export NOTION_DATABASE_ID='your_database_id_here'")
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
