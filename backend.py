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
from pydantic import BaseModel

from loguru import logger

# Import our services
from llm_service import LLMService
from function_router import FunctionRouter
from audio_service import SpeechToTextService, TextToSpeechService

# Configure logger
logger.add("logs/voice_agent_{time}.log", rotation="1 day", retention="7 days", level="INFO")

# Initialize FastAPI app
app = FastAPI(
    title="AI Voice Agent API",
    description="REST API for AI Voice Agent with function calling",
    version="1.0.0"
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
llm_service = LLMService(model="my-lama3-finetuned-Q4_K_M")
function_router = FunctionRouter()
stt_service = SpeechToTextService(model_name="base")
tts_service = TextToSpeechService(backend="system")

# Request/Response models
class TextQueryRequest(BaseModel):
    """Request model for text-based queries"""
    text: str
    include_audio: bool = False


class VoiceQueryRequest(BaseModel):
    """Request model for voice queries"""
    text: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for all queries"""
    success: bool
    query_text: str
    raw_llm_output: str
    is_function_call: bool
    function_name: Optional[str]
    function_args: Optional[Dict[str, Any]]
    response_text: str
    audio_path: Optional[str] = None
    processing_time: float
    error: Optional[str] = None


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Voice Agent API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "llm": "ollama/my-lama3-finetuned-Q4_K_M",
            "stt": "whisper",
            "tts": "system",
            "tools": list(function_router.tool_registry.keys())
        }
    }


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


@app.post("/api/transcribe/")
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

        return {
            "success": True,
            "transcription": transcription
        }

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
