"""
API Data Models
Pydantic models for FastAPI request/response schemas
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# Request Models
# ============================================================================

class TextQueryRequest(BaseModel):
    """Request model for text-based queries"""
    text: str = Field(..., description="User's query text")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    include_summary: bool = Field(False, description="Whether to generate a summary")
    include_audio: bool = Field(False, description="Whether to generate audio response")


class AskRequest(BaseModel):
    """Request model for the /ask endpoint"""
    text: str = Field(..., description="User's query text")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    include_summary: bool = Field(False, description="Whether to generate summary")


class NotionSyncRequest(BaseModel):
    """Request model for Notion sync endpoint"""
    session_id: str = Field(..., description="Session ID to sync")
    include_summary: bool = Field(True, description="Whether to include summary")


class TranscribeRequest(BaseModel):
    """Request model for audio transcription"""
    audio_format: Optional[str] = Field(None, description="Audio format (wav, mp3, etc.)")


class SynthesizeRequest(BaseModel):
    """Request model for text-to-speech synthesis"""
    text: str = Field(..., description="Text to synthesize")
    voice: Optional[str] = Field(None, description="Voice ID or name")


# ============================================================================
# Response Models
# ============================================================================

class QueryResponse(BaseModel):
    """Response model for query endpoints"""
    success: bool = Field(..., description="Whether the query was successful")
    session_id: Optional[str] = Field(None, description="Session identifier")
    query_text: str = Field(..., description="Original query text")
    response_text: str = Field(..., description="Assistant's response")
    summary: Optional[str] = Field(None, description="Optional summary of the response")

    # Function calling metadata
    is_function_call: bool = Field(False, description="Whether a function was called")
    function_name: Optional[str] = Field(None, description="Name of function called")
    function_args: Optional[Dict[str, Any]] = Field(None, description="Function arguments")

    # Metadata
    raw_llm_output: Optional[str] = Field(None, description="Raw LLM output for debugging")
    processing_time: float = Field(..., description="Processing time in seconds")
    query_count: Optional[int] = Field(None, description="Number of queries in this session")

    # Optional audio
    audio_path: Optional[str] = Field(None, description="Path to audio response file")

    # Error handling
    error: Optional[str] = Field(None, description="Error message if failed")


class AskResponse(BaseModel):
    """Response model for /ask endpoint"""
    success: bool = Field(..., description="Whether the request was successful")
    session_id: str = Field(..., description="Session identifier")
    query_text: str = Field(..., description="Original query text")
    response_text: str = Field(..., description="Assistant's response")
    summary: Optional[str] = Field(None, description="Optional summary")

    # Metadata
    is_function_call: bool = Field(False, description="Whether a function was called")
    function_name: Optional[str] = Field(None, description="Function name")
    function_args: Optional[Dict[str, Any]] = Field(None, description="Function arguments")
    processing_time: float = Field(..., description="Processing time in seconds")
    query_count: int = Field(..., description="Number of queries in session")

    # Error
    error: Optional[str] = Field(None, description="Error message if failed")


class NotionSyncResponse(BaseModel):
    """Response model for Notion sync endpoint"""
    success: bool = Field(..., description="Whether sync was successful")
    session_id: str = Field(..., description="Session identifier")
    notion_url: Optional[str] = Field(None, description="URL of Notion page")
    message: str = Field(..., description="Status message")


class StatusResponse(BaseModel):
    """Response model for /status endpoint"""
    status: str = Field(..., description="System status")
    session: Optional[Dict[str, Any]] = Field(None, description="Session information")
    total_sessions: Optional[int] = Field(None, description="Total active sessions")
    services: Optional[Dict[str, Any]] = Field(None, description="Service status")
    message: Optional[str] = Field(None, description="Additional message")


class HealthResponse(BaseModel):
    """Response model for /health endpoint"""
    status: str = Field(..., description="Health status")
    services: Dict[str, Any] = Field(..., description="Available services")


class TranscribeResponse(BaseModel):
    """Response model for transcription endpoint"""
    success: bool = Field(..., description="Whether transcription was successful")
    transcription: str = Field(..., description="Transcribed text")
    language: Optional[str] = Field(None, description="Detected language")


class SessionSummary(BaseModel):
    """Session summary information"""
    session_id: str = Field(..., description="Session identifier")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    query_count: int = Field(..., description="Number of queries")
    message_count: int = Field(..., description="Number of messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConversationMessage(BaseModel):
    """Single conversation message"""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Message metadata")


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")


if __name__ == "__main__":
    # Test the models
    print("API Models Test")
    print("-" * 50)

    # Test AskRequest
    request = AskRequest(
        text="What is quantum entanglement?",
        session_id="test-123",
        include_summary=True
    )
    print("AskRequest:")
    print(request.model_dump_json(indent=2))

    # Test AskResponse
    response = AskResponse(
        success=True,
        session_id="test-123",
        query_text="What is quantum entanglement?",
        response_text="Quantum entanglement is...",
        is_function_call=True,
        function_name="search_arxiv",
        function_args={"query": "quantum entanglement", "limit": 3},
        processing_time=2.5,
        query_count=1
    )
    print("\nAskResponse:")
    print(response.model_dump_json(indent=2))
