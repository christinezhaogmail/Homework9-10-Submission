"""
Test script for API Data Models
Tests Pydantic models for request/response validation
"""

import sys
from loguru import logger

# Configure logger for testing
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

from api import (
    AskRequest,
    AskResponse,
    NotionSyncRequest,
    NotionSyncResponse,
    StatusResponse,
    HealthResponse,
    TranscribeResponse,
    SessionSummary,
    ConversationMessage
)


def test_ask_models():
    """Test Ask request/response models"""
    print("\n" + "=" * 70)
    print("TEST 1: Ask Request/Response Models")
    print("=" * 70)

    print("\n[Test 1.1] Create AskRequest")
    request = AskRequest(
        text="What is quantum entanglement?",
        session_id="test-123",
        include_summary=True
    )
    print(f"Request: {request.model_dump_json(indent=2)}")
    assert request.text == "What is quantum entanglement?"
    assert request.session_id == "test-123"
    assert request.include_summary == True
    print("✅ AskRequest created successfully")

    print("\n[Test 1.2] Create AskResponse")
    response = AskResponse(
        success=True,
        session_id="test-123",
        query_text="What is quantum entanglement?",
        response_text="Quantum entanglement is...",
        summary="A phenomenon in quantum mechanics",
        is_function_call=True,
        function_name="search_arxiv",
        function_args={"query": "quantum entanglement", "limit": 3},
        processing_time=2.5,
        query_count=1
    )
    print(f"Response keys: {list(response.model_dump().keys())}")
    assert response.success == True
    assert response.query_count == 1
    print("✅ AskResponse created successfully")


def test_notion_models():
    """Test Notion sync models"""
    print("\n" + "=" * 70)
    print("TEST 2: Notion Sync Models")
    print("=" * 70)

    print("\n[Test 2.1] Create NotionSyncRequest")
    request = NotionSyncRequest(
        session_id="test-123",
        include_summary=True
    )
    print(f"Request: {request.model_dump_json(indent=2)}")
    assert request.session_id == "test-123"
    print("✅ NotionSyncRequest created successfully")

    print("\n[Test 2.2] Create NotionSyncResponse")
    response = NotionSyncResponse(
        success=True,
        session_id="test-123",
        notion_url="https://notion.so/page-123",
        message="Session synced successfully"
    )
    print(f"Response: {response.model_dump_json(indent=2)}")
    assert response.notion_url == "https://notion.so/page-123"
    print("✅ NotionSyncResponse created successfully")


def test_status_models():
    """Test status models"""
    print("\n" + "=" * 70)
    print("TEST 3: Status Models")
    print("=" * 70)

    print("\n[Test 3.1] Create HealthResponse")
    response = HealthResponse(
        status="healthy",
        services={
            "llm": "ollama/llama3.2",
            "stt": "whisper",
            "tts": "system"
        }
    )
    print(f"Health response: {response.model_dump_json(indent=2)}")
    assert response.status == "healthy"
    print("✅ HealthResponse created successfully")

    print("\n[Test 3.2] Create StatusResponse")
    response = StatusResponse(
        status="healthy",
        total_sessions=5,
        services={"llm": "ollama"}
    )
    print(f"Status response: {response.model_dump_json(indent=2)}")
    assert response.total_sessions == 5
    print("✅ StatusResponse created successfully")


def test_session_models():
    """Test session-related models"""
    print("\n" + "=" * 70)
    print("TEST 4: Session Models")
    print("=" * 70)

    print("\n[Test 4.1] Create SessionSummary")
    summary = SessionSummary(
        session_id="test-123",
        created_at="2024-01-17T10:00:00",
        updated_at="2024-01-17T10:30:00",
        query_count=3,
        message_count=6,
        metadata={"papers_found": 5}
    )
    print(f"Session summary: {summary.model_dump_json(indent=2)}")
    assert summary.query_count == 3
    assert summary.metadata["papers_found"] == 5
    print("✅ SessionSummary created successfully")

    print("\n[Test 4.2] Create ConversationMessage")
    message = ConversationMessage(
        role="user",
        content="What is quantum entanglement?",
        timestamp="2024-01-17T10:00:00",
        metadata={"source": "voice"}
    )
    print(f"Message: {message.model_dump_json(indent=2)}")
    assert message.role == "user"
    print("✅ ConversationMessage created successfully")


def test_validation():
    """Test model validation"""
    print("\n" + "=" * 70)
    print("TEST 5: Model Validation")
    print("=" * 70)

    print("\n[Test 5.1] Test required fields")
    try:
        # This should fail - missing required field
        request = AskRequest(session_id="test")
        print("❌ Should have failed - text field is required")
        assert False, "Validation should have failed"
    except Exception as e:
        print(f"✅ Validation correctly caught missing field: {type(e).__name__}")

    print("\n[Test 5.2] Test default values")
    request = AskRequest(text="Hello")
    assert request.session_id is None, "session_id should default to None"
    assert request.include_summary == False, "include_summary should default to False"
    print("✅ Default values work correctly")


def test_json_serialization():
    """Test JSON serialization/deserialization"""
    print("\n" + "=" * 70)
    print("TEST 6: JSON Serialization")
    print("=" * 70)

    print("\n[Test 6.1] Serialize to JSON")
    request = AskRequest(text="Test query", session_id="abc-123")
    json_str = request.model_dump_json()
    print(f"JSON: {json_str}")
    assert '"text":"Test query"' in json_str or '"text": "Test query"' in json_str
    print("✅ Serialization successful")

    print("\n[Test 6.2] Deserialize from JSON")
    json_data = '{"text": "Test query", "session_id": "abc-123", "include_summary": false}'
    request = AskRequest.model_validate_json(json_data)
    assert request.text == "Test query"
    assert request.session_id == "abc-123"
    print("✅ Deserialization successful")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("API DATA MODELS - TEST SUITE")
    print("=" * 70)

    try:
        test_ask_models()
        test_notion_models()
        test_status_models()
        test_session_models()
        test_validation()
        test_json_serialization()

        print("\n" + "=" * 70)
        print("🎉 ALL API MODEL TESTS PASSED!")
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
