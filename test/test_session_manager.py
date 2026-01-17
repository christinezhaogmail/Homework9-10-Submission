"""
Test script for Session Manager
Tests session creation, message handling, and history management
"""

import sys
from loguru import logger

# Configure logger for testing
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

from utils.session_manager import SessionManager


def test_session_creation():
    """Test session creation"""
    print("\n" + "=" * 70)
    print("TEST 1: Session Creation")
    print("=" * 70)

    manager = SessionManager(max_history=5)

    print("\n[Test 1.1] Create new session")
    session_id = manager.create_session()
    print(f"Created session ID: {session_id}")
    assert session_id is not None, "Session ID is None"
    assert len(session_id) > 0, "Session ID is empty"
    print("✅ Session created with valid ID")

    print("\n[Test 1.2] Retrieve session")
    session = manager.get_session(session_id)
    print(f"Retrieved session: {session['id']}")
    assert session is not None, "Session not found"
    assert session["id"] == session_id, "Session ID mismatch"
    assert session["query_count"] == 0, "Initial query count should be 0"
    print("✅ Session retrieved successfully")


def test_message_handling():
    """Test adding and retrieving messages"""
    print("\n" + "=" * 70)
    print("TEST 2: Message Handling")
    print("=" * 70)

    manager = SessionManager(max_history=5)
    session_id = manager.create_session()

    print("\n[Test 2.1] Add user message")
    success = manager.add_message(session_id, "user", "What is quantum entanglement?")
    assert success, "Failed to add user message"
    session = manager.get_session(session_id)
    assert session["query_count"] == 1, "Query count not incremented"
    print("✅ User message added, query count incremented")

    print("\n[Test 2.2] Add assistant message")
    success = manager.add_message(
        session_id,
        "assistant",
        "Quantum entanglement is...",
        metadata={"function_called": "search_arxiv"}
    )
    assert success, "Failed to add assistant message"
    print("✅ Assistant message added with metadata")

    print("\n[Test 2.3] Retrieve conversation history")
    history = manager.get_conversation_history(session_id)
    print(f"History length: {len(history)}")
    assert len(history) == 2, "History should have 2 messages"
    assert history[0]["role"] == "user", "First message should be from user"
    assert history[1]["role"] == "assistant", "Second message should be from assistant"
    print("✅ Conversation history retrieved correctly")

    print("\n[Test 2.4] Get conversation as text")
    text = manager.get_conversation_text(session_id)
    print(f"Conversation text (first 100 chars):\n{text[:100]}...")
    assert "user" in text.lower(), "User role not in text"
    assert "assistant" in text.lower(), "Assistant role not in text"
    print("✅ Conversation text formatted correctly")


def test_history_limit():
    """Test history limit enforcement"""
    print("\n" + "=" * 70)
    print("TEST 3: History Limit")
    print("=" * 70)

    manager = SessionManager(max_history=3)  # Keep only 3 conversation turns (6 messages)
    session_id = manager.create_session()

    print("\n[Test 3.1] Add messages exceeding limit")
    for i in range(5):
        manager.add_message(session_id, "user", f"Question {i+1}")
        manager.add_message(session_id, "assistant", f"Answer {i+1}")

    history = manager.get_conversation_history(session_id)
    print(f"History length after 5 turns: {len(history)}")
    assert len(history) <= 6, "History should be trimmed to max_history * 2"
    print(f"✅ History trimmed to {len(history)} messages")


def test_session_summary():
    """Test session summary"""
    print("\n" + "=" * 70)
    print("TEST 4: Session Summary")
    print("=" * 70)

    manager = SessionManager(max_history=5)
    session_id = manager.create_session()

    # Add some messages
    manager.add_message(session_id, "user", "Test question 1")
    manager.add_message(session_id, "assistant", "Test answer 1")
    manager.add_message(session_id, "user", "Test question 2")
    manager.add_message(session_id, "assistant", "Test answer 2")

    print("\n[Test 4.1] Get session summary")
    summary = manager.get_session_summary(session_id)
    print("Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    assert summary["session_id"] == session_id, "Session ID mismatch in summary"
    assert summary["query_count"] == 2, "Query count incorrect"
    assert summary["message_count"] == 4, "Message count incorrect"
    print("✅ Session summary correct")


def test_metadata():
    """Test session metadata"""
    print("\n" + "=" * 70)
    print("TEST 5: Session Metadata")
    print("=" * 70)

    manager = SessionManager(max_history=5)
    session_id = manager.create_session()

    print("\n[Test 5.1] Update metadata")
    success = manager.update_metadata(session_id, {"papers_found": 3, "notion_synced": False})
    assert success, "Failed to update metadata"

    session = manager.get_session(session_id)
    print(f"Metadata: {session['metadata']}")
    assert session["metadata"]["papers_found"] == 3, "Metadata not updated"
    print("✅ Metadata updated successfully")


def test_session_deletion():
    """Test session deletion"""
    print("\n" + "=" * 70)
    print("TEST 6: Session Deletion")
    print("=" * 70)

    manager = SessionManager(max_history=5)
    session_id = manager.create_session()

    print("\n[Test 6.1] Delete session")
    success = manager.delete_session(session_id)
    assert success, "Failed to delete session"

    session = manager.get_session(session_id)
    assert session is None, "Session still exists after deletion"
    print("✅ Session deleted successfully")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("SESSION MANAGER - TEST SUITE")
    print("=" * 70)

    try:
        test_session_creation()
        test_message_handling()
        test_history_limit()
        test_session_summary()
        test_metadata()
        test_session_deletion()

        print("\n" + "=" * 70)
        print("🎉 ALL SESSION MANAGER TESTS PASSED!")
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
