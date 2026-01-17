"""
FastAPI Backend for AI Voice Agent
Provides REST API endpoints for voice interactions
"""

import os
import tempfile
import time
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from loguru import logger

# Import API models
from api import (
    TextQueryRequest,
    QueryResponse,
    AskRequest,
    AskResponse,
    NotionSyncRequest,
    NotionSyncResponse,
    StatusResponse,
    HealthResponse,
    TranscribeResponse
)

# Import our services
from llm_service import LLMService
from function_router import FunctionRouter
from audio_service import SpeechToTextService, TextToSpeechService
from utils.session_manager import SessionManager
from tools.summarize import ContentSummarizer
from tools.notion import NotionSync

# Configure logger
logger.add("logs/voice_agent_{time}.log", rotation="1 day", retention="7 days", level="INFO")

# Initialize FastAPI app
app = FastAPI(
    title="AI Research Assistant API",
    description="REST API for AI Research Assistant with function calling, summarization, and Notion sync",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_service = LLMService(model="llama3.2")
function_router = FunctionRouter()
stt_service = SpeechToTextService(model_name="base")
tts_service = TextToSpeechService(backend="system")
session_manager = SessionManager(max_history=10)
notion_sync = NotionSync()

# Initialize summarizer (lazy loading - only when needed)
summarizer = None


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Voice Agent API",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        services={
            "llm": "ollama/llama3.2",
            "stt": "whisper",
            "tts": "system",
            "tools": list(function_router.tool_registry.keys()),
            "notion_sync": notion_sync.is_enabled()
        }
    )


@app.get("/status", response_model=StatusResponse)
async def get_status(session_id: Optional[str] = None):
    """
    Get system status and session information.

    Args:
        session_id: Optional session ID to get specific session info

    Returns:
        Status dictionary with session info
    """
    logger.info(f"Status check requested (session_id={session_id})")

    if session_id:
        session_summary = session_manager.get_session_summary(session_id)
        if session_summary:
            return StatusResponse(
                status="healthy",
                session=session_summary
            )
        else:
            return StatusResponse(
                status="healthy",
                session=None,
                message=f"Session {session_id} not found"
            )
    else:
        return StatusResponse(
            status="healthy",
            total_sessions=len(session_manager.get_all_sessions()),
            services={
                "llm": "ollama/llama3.2",
                "stt": "whisper",
                "tts": "system",
                "notion_sync": notion_sync.is_enabled()
            }
        )


@app.post("/ask", response_model=AskResponse)
async def ask_endpoint(
    text: str = Form(...),
    session_id: Optional[str] = Form(None),
    include_summary: bool = Form(False)
):
    """
    Main research assistant endpoint.
    Accepts text or voice query, runs the full pipeline, and returns response.

    Args:
        text: User query text
        session_id: Optional session ID for conversation context
        include_summary: Whether to generate summary of the response

    Returns:
        Response with answer, session info, and optional summary
    """
    start_time = time.time()

    try:
        # Create or get session
        if not session_id:
            session_id = session_manager.create_session()
            logger.info(f"Created new session: {session_id}")
        else:
            if not session_manager.get_session(session_id):
                session_id = session_manager.create_session()
                logger.info(f"Session not found, created new one: {session_id}")

        logger.info(f"=== ASK REQUEST (Session: {session_id}) ===")
        logger.info(f"User Query: {text}")

        # Add user message to session
        session_manager.add_message(session_id, "user", text)

        # Step 1: Generate LLM response
        logger.info("Step 1: Generating LLM response...")
        llm_output = llm_service.generate_response(text)
        logger.info(f"Raw LLM Output: {llm_output}")

        # Step 2: Route the LLM output (detect and execute function calls)
        logger.info("Step 2: Routing LLM output...")
        routing_result = function_router.route_llm_output(llm_output)

        logger.info(f"Is Function Call: {routing_result['is_function_call']}")
        if routing_result['is_function_call']:
            logger.info(f"Function Name: {routing_result['function_name']}")
            logger.info(f"Function Args: {routing_result['function_args']}")

        response_text = routing_result['response']
        logger.info(f"Final Response: {response_text[:200]}...")

        # Add assistant message to session
        session_manager.add_message(
            session_id,
            "assistant",
            response_text,
            metadata={
                "is_function_call": routing_result['is_function_call'],
                "function_name": routing_result['function_name'],
                "function_args": routing_result['function_args']
            }
        )

        # Step 3: Generate summary if requested
        summary = None
        if include_summary:
            try:
                global summarizer
                if summarizer is None:
                    logger.info("Initializing summarizer...")
                    summarizer = ContentSummarizer()

                summary = summarizer.summarize(response_text)
                logger.info(f"Generated summary: {summary[:100]}...")
            except Exception as e:
                logger.error(f"Summarization failed: {e}")
                summary = None

        processing_time = time.time() - start_time

        # Build response
        logger.info(f"Processing completed in {processing_time:.2f}s")
        logger.info("=" * 50)

        return AskResponse(
            success=True,
            session_id=session_id,
            query_text=text,
            response_text=response_text,
            summary=summary,
            is_function_call=routing_result['is_function_call'],
            function_name=routing_result['function_name'],
            function_args=routing_result['function_args'],
            processing_time=processing_time,
            query_count=session_manager.get_session(session_id)["query_count"]
        )

    except Exception as e:
        logger.error(f"Error processing ask request: {str(e)}")
        processing_time = time.time() - start_time

        return AskResponse(
            success=False,
            session_id=session_id if 'session_id' in locals() else "",
            query_text=text,
            response_text=f"Error: {str(e)}",
            processing_time=processing_time,
            query_count=0,
            error=str(e)
        )


@app.post("/notion-sync", response_model=NotionSyncResponse)
async def notion_sync_endpoint(
    session_id: str = Form(...),
    include_summary: bool = Form(True)
):
    """
    Sync session conversation to Notion.

    Args:
        session_id: Session ID to sync
        include_summary: Whether to generate and include a summary

    Returns:
        Sync result with Notion page URL
    """
    try:
        logger.info("=== NOTION SYNC REQUEST ===")
        logger.info(f"Session ID: {session_id}")

        # Check if session exists
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

        # Check if Notion sync is enabled
        if not notion_sync.is_enabled():
            return NotionSyncResponse(
                success=False,
                session_id=session_id,
                message="Notion sync is not enabled. Set NOTION_TOKEN and NOTION_DATABASE_ID environment variables."
            )

        # Get conversation text
        conversation_text = session_manager.get_conversation_text(session_id, include_metadata=True)

        # Generate summary if requested
        summary = None
        if include_summary:
            try:
                global summarizer
                if summarizer is None:
                    logger.info("Initializing summarizer...")
                    summarizer = ContentSummarizer()

                summary = summarizer.summarize(conversation_text, max_length=200)
                logger.info("Generated conversation summary")
            except Exception as e:
                logger.error(f"Summarization failed: {e}")
                summary = None

        # Sync to Notion
        page_url = notion_sync.sync_session(
            session_id=session_id,
            content=conversation_text,
            summary=summary,
            metadata={
                "query_count": session["query_count"],
                "created_at": session["created_at"]
            }
        )

        if page_url:
            logger.info(f"✓ Synced to Notion: {page_url}")
            return NotionSyncResponse(
                success=True,
                session_id=session_id,
                notion_url=page_url,
                message="Session synced successfully"
            )
        else:
            return NotionSyncResponse(
                success=False,
                session_id=session_id,
                message="Failed to sync to Notion"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing to Notion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice-query/", response_model=QueryResponse)
async def voice_query_endpoint(request: Dict[str, Any]):
    """
    Main voice query endpoint
    Processes user queries and returns responses

    Args:
        request: Dictionary with 'text' field containing the user's query

    Returns:
        QueryResponse with the agent's response
    """
    start_time = time.time()

    try:
        # Extract user query
        user_text = request.get("text", "")
        if not user_text:
            raise HTTPException(status_code=400, detail="No text provided in request")

        logger.info(f"=== NEW QUERY ===")
        logger.info(f"User Query: {user_text}")

        # Step 1: Generate LLM response
        logger.info("Step 1: Generating LLM response...")
        llm_output = llm_service.generate_response(user_text)
        logger.info(f"Raw LLM Output: {llm_output}")

        # Step 2: Route the LLM output (detect and execute function calls)
        logger.info("Step 2: Routing LLM output...")
        routing_result = function_router.route_llm_output(llm_output)

        logger.info(f"Is Function Call: {routing_result['is_function_call']}")
        if routing_result['is_function_call']:
            logger.info(f"Function Name: {routing_result['function_name']}")
            logger.info(f"Function Args: {routing_result['function_args']}")

        logger.info(f"Final Response: {routing_result['response'][:200]}...")

        # Calculate processing time
        processing_time = time.time() - start_time

        # Build response
        response = QueryResponse(
            success=True,
            query_text=user_text,
            raw_llm_output=llm_output,
            is_function_call=routing_result['is_function_call'],
            function_name=routing_result['function_name'],
            function_args=routing_result['function_args'],
            response_text=routing_result['response'],
            processing_time=processing_time
        )

        logger.info(f"Processing completed in {processing_time:.2f}s")
        logger.info("=" * 50)

        return response

    except Exception as e:
        logger.error(f"Error processing voice query: {str(e)}")
        processing_time = time.time() - start_time

        return QueryResponse(
            success=False,
            query_text=request.get("text", ""),
            raw_llm_output="",
            is_function_call=False,
            function_name=None,
            function_args=None,
            response_text=f"Error: {str(e)}",
            processing_time=processing_time,
            error=str(e)
        )


@app.post("/api/text-query/", response_model=QueryResponse)
async def text_query_endpoint(request: TextQueryRequest):
    """
    Text-only query endpoint (no audio processing)

    Args:
        request: TextQueryRequest with the user's text query

    Returns:
        QueryResponse with the agent's response
    """
    return await voice_query_endpoint({"text": request.text})


@app.post("/api/transcribe/", response_model=TranscribeResponse)
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe audio file to text

    Args:
        audio_file: Audio file upload

    Returns:
        Transcription result
    """
    try:
        logger.info(f"Transcribing audio file: {audio_file.filename}")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        # Transcribe
        transcription = stt_service.transcribe_audio(temp_path)

        # Clean up
        os.unlink(temp_path)

        return TranscribeResponse(
            success=True,
            transcription=transcription
        )

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/synthesize/")
async def synthesize_speech(text: str = Form(...)):
    """
    Convert text to speech and return audio file

    Args:
        text: Text to convert to speech

    Returns:
        Audio file
    """
    try:
        logger.info(f"Synthesizing speech for: {text[:100]}...")

        # Create temporary audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".aiff") as temp_file:
            output_path = temp_file.name

        # Generate audio
        success = tts_service.text_to_audio_file(text, output_path)

        if success and os.path.exists(output_path):
            return FileResponse(
                output_path,
                media_type="audio/aiff",
                filename="response.aiff"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio")

    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/full-voice-query/")
async def full_voice_query(audio_file: UploadFile = File(...)):
    """
    Complete voice query pipeline: Audio -> Text -> LLM -> Function -> Text -> Audio

    Args:
        audio_file: Audio file with user's voice query

    Returns:
        JSON with transcription, response text, and audio file path
    """
    start_time = time.time()

    try:
        logger.info(f"=== FULL VOICE QUERY ===")
        logger.info(f"Audio file: {audio_file.filename}")

        # Step 1: Transcribe audio to text
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            audio_path = temp_file.name

        transcription = stt_service.transcribe_audio(audio_path)
        os.unlink(audio_path)

        logger.info(f"Transcription: {transcription}")

        # Step 2: Process with LLM and functions
        query_response = await voice_query_endpoint({"text": transcription})

        # Step 3: Convert response to audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".aiff") as temp_file:
            output_path = temp_file.name

        tts_service.text_to_audio_file(query_response.response_text, output_path)

        processing_time = time.time() - start_time
        logger.info(f"Full voice query completed in {processing_time:.2f}s")

        return {
            "success": True,
            "transcription": transcription,
            "response": query_response.dict(),
            "audio_path": output_path,
            "total_processing_time": processing_time
        }

    except Exception as e:
        logger.error(f"Error in full voice query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting AI Voice Agent API server...")
    logger.info("API will be available at: http://localhost:8000")
    logger.info("API docs at: http://localhost:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
