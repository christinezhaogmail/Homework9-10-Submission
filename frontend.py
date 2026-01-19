"""
Streamlit Frontend for Research Assistant
Interactive web interface for the voice agent with audio input/output
"""

import streamlit as st
import requests
import json
import time
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

# Import audio services for direct interaction
from audio_service import VoiceAgentAudio, SpeechToTextService, TextToSpeechService
from llm_service import LLMService
from function_router import FunctionRouter
from config import Config
from loguru import logger

# Configure page
st.set_page_config(
    page_title="Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0
if 'use_api' not in st.session_state:
    st.session_state.use_api = False
if 'voice_mode' not in st.session_state:
    st.session_state.voice_mode = True  # Enable voice by default
if 'tts_backend' not in st.session_state:
    st.session_state.tts_backend = Config.TTS_BACKEND
if 'last_audio_response' not in st.session_state:
    st.session_state.last_audio_response = None
if 'processing_query' not in st.session_state:
    st.session_state.processing_query = False


def init_services():
    """Initialize local services if not using API"""
    if 'llm_service' not in st.session_state:
        st.session_state.llm_service = LLMService()
    if 'function_router' not in st.session_state:
        st.session_state.function_router = FunctionRouter()
    if 'voice_agent' not in st.session_state:
        st.session_state.voice_agent = VoiceAgentAudio()
    if 'stt_service' not in st.session_state:
        st.session_state.stt_service = SpeechToTextService(model_name=Config.WHISPER_MODEL)
    if 'tts_service' not in st.session_state:
        st.session_state.tts_service = TextToSpeechService(
            backend=st.session_state.tts_backend,
            cosyvoice_model_dir=Config.COSYVOICE_MODEL_DIR if st.session_state.tts_backend == "cosyvoice" else None
        )


def query_api(text: str, api_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """
    Query the FastAPI backend

    Args:
        text: User's query text
        api_url: Base URL of the API

    Returns:
        Response dictionary
    """
    try:
        response = requests.post(
            f"{api_url}/api/voice-query/",
            json={"text": text},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_text": f"Error connecting to API: {str(e)}"
        }


def query_local(text: str) -> Dict[str, Any]:
    """
    Query using local services (no API)

    Args:
        text: User's query text

    Returns:
        Response dictionary
    """
    try:
        start_time = time.time()

        # Get LLM response
        llm_output = st.session_state.llm_service.generate_response(text)

        # Route and execute
        routing_result = st.session_state.function_router.route_llm_output(llm_output)

        processing_time = time.time() - start_time

        return {
            "success": True,
            "query_text": text,
            "raw_llm_output": llm_output,
            "is_function_call": routing_result['is_function_call'],
            "function_name": routing_result['function_name'],
            "function_args": routing_result['function_args'],
            "response_text": routing_result['response'],
            "processing_time": processing_time
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_text": f"Error: {str(e)}"
        }


def transcribe_audio(audio_bytes: bytes) -> Optional[str]:
    """
    Transcribe audio bytes to text using Whisper

    Args:
        audio_bytes: Audio data as bytes

    Returns:
        Transcribed text or None if failed
    """
    try:
        # Save audio bytes to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        # Transcribe using Whisper
        transcription = st.session_state.stt_service.transcribe_audio(temp_path)

        # Clean up
        os.unlink(temp_path)

        return transcription

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        st.error(f"Transcription error: {e}")
        return None


def generate_audio_response(text: str) -> Optional[str]:
    """
    Generate audio from text using TTS

    Args:
        text: Text to convert to speech

    Returns:
        Path to audio file or None if failed
    """
    try:
        # Create temporary file for audio
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        audio_path = temp_file.name
        temp_file.close()

        # Generate audio using TTS
        success = st.session_state.tts_service.text_to_audio_file(text, audio_path)

        if success and os.path.exists(audio_path):
            return audio_path
        else:
            return None

    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        return None


def format_response_details(response: Dict[str, Any]) -> str:
    """Format response details for display"""
    details = []

    if response.get('is_function_call'):
        details.append(f"**Function Called:** `{response.get('function_name')}`")
        details.append(f"**Arguments:** `{json.dumps(response.get('function_args'), indent=2)}`")

    details.append(f"**Processing Time:** {response.get('processing_time', 0):.2f}s")

    return "\n\n".join(details)


# Main UI
st.title("🤖 Research Assistant")

# Show voice mode status
if st.session_state.voice_mode:
    st.success("🎙️ Voice Mode: **Enabled** - Audio input and output active")
else:
    st.info("💬 Text Mode: Voice mode disabled")

st.markdown("Ask me anything! I can search scientific papers on arXiv and automatically save sessions to Notion.")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # Mode selection
    use_api = st.checkbox(
        "Use API Mode",
        value=st.session_state.use_api,
        help="Enable to use FastAPI backend, disable for direct local processing"
    )
    st.session_state.use_api = use_api

    if use_api:
        api_url = st.text_input("API URL", value="http://localhost:8000")
        # Test API connection
        if st.button("Test Connection"):
            try:
                response = requests.get(f"{api_url}/health", timeout=5)
                if response.ok:
                    st.success("✅ API is reachable")
                    data = response.json()
                    st.json(data)
                else:
                    st.error("❌ API returned an error")
            except Exception as e:
                st.error(f"❌ Cannot connect to API: {str(e)}")
    else:
        st.info("Using local services (no API)")
        init_services()

    st.divider()

    # Voice Settings
    st.header("🎙️ Voice Settings")

    voice_mode = st.checkbox(
        "Enable Voice Mode",
        value=st.session_state.voice_mode,
        help="Enable audio input and output"
    )
    st.session_state.voice_mode = voice_mode

    if voice_mode and not use_api:
        tts_backend = st.selectbox(
            "TTS Backend",
            options=["system", "pyttsx3", "cosyvoice"],
            index=["system", "pyttsx3", "cosyvoice"].index(st.session_state.tts_backend),
            help="Text-to-Speech backend (system is fastest on macOS)"
        )

        if tts_backend != st.session_state.tts_backend:
            st.session_state.tts_backend = tts_backend
            # Reinitialize TTS service
            st.session_state.tts_service = TextToSpeechService(
                backend=tts_backend,
                cosyvoice_model_dir=Config.COSYVOICE_MODEL_DIR if tts_backend == "cosyvoice" else None
            )
            st.success(f"Switched to {tts_backend} TTS")

    st.divider()

    # Statistics
    st.header("📊 Statistics")
    st.metric("Total Queries", st.session_state.query_count)
    st.metric("Conversation Length", len(st.session_state.messages))

    st.divider()

    # Clear conversation
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.rerun()

    st.divider()

    # Example queries
    st.header("💡 Example Queries")
    st.markdown("""
    **arXiv Search (Auto-saves to Notion):**
    - What is quantum entanglement?
    - Search for papers on neural networks
    - Find research on climate change
    - Tell me about machine learning in healthcare
    - What are the latest papers on AI safety?
    - Search for quantum computing algorithms

    **General Chat:**
    - Hello, how are you?
    - What can you help me with?

    **Note:** Each arXiv search automatically saves to your Notion database!
    """)

# Display conversation history
st.subheader("💬 Conversation")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Show audio playback for assistant messages if available
        if msg["role"] == "assistant" and "audio_path" in msg and msg["audio_path"]:
            if os.path.exists(msg["audio_path"]):
                with open(msg["audio_path"], "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/wav")

        # Show details for assistant messages
        if msg["role"] == "assistant" and "details" in msg:
            with st.expander("📋 Details"):
                st.markdown(msg["details"])

            # Show raw LLM output if available
            if "raw_llm_output" in msg:
                with st.expander("🔍 Raw LLM Output"):
                    st.code(msg["raw_llm_output"], language='json')

# Audio input (if voice mode is enabled)
if st.session_state.voice_mode and not st.session_state.use_api:
    st.subheader("🎤 Voice Input")

    # Use query_count as part of the key to reset the widget after each query
    audio_input = st.audio_input("Record your question", key=f"audio_input_{st.session_state.query_count}")

    if audio_input is not None and not st.session_state.processing_query:
        with st.spinner("Transcribing audio..."):
            # Read audio bytes
            audio_bytes = audio_input.read()

            # Transcribe
            transcription = transcribe_audio(audio_bytes)

            if transcription:
                st.success(f"✅ Transcribed: {transcription}")

                # Set processing flag to prevent reprocessing
                st.session_state.processing_query = True

                # Add to messages and process immediately
                st.session_state.messages.append({
                    "role": "user",
                    "content": transcription,
                    "timestamp": datetime.now().isoformat()
                })

                # Process the query
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        # Query based on mode
                        if st.session_state.use_api:
                            response = query_api(transcription, api_url if 'api_url' in locals() else "http://localhost:8000")
                        else:
                            response = query_local(transcription)

                        # Display response
                        response_text = response.get('response_text', 'No response')
                        st.markdown(response_text)

                        # Generate audio response if voice mode is enabled
                        audio_path = None
                        if st.session_state.voice_mode:
                            with st.spinner("Generating audio..."):
                                audio_path = generate_audio_response(response_text)

                                if audio_path and os.path.exists(audio_path):
                                    st.success("🔊 Audio response generated")
                                    # Play the audio
                                    with open(audio_path, "rb") as audio_file:
                                        st.audio(audio_file.read(), format="audio/wav")
                                else:
                                    st.warning("Could not generate audio response")

                        # Show details
                        if response.get('success'):
                            details = format_response_details(response)

                            # Show details expander
                            with st.expander("📋 Details"):
                                st.markdown(details)

                            # Show raw LLM output expander
                            with st.expander("🔍 Raw LLM Output"):
                                st.code(response.get('raw_llm_output', ''), language='json')

                # Add assistant message to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "details": format_response_details(response) if response.get('success') else None,
                    "raw_llm_output": response.get('raw_llm_output', ''),
                    "audio_path": audio_path,
                    "timestamp": datetime.now().isoformat()
                })

                # Increment query count
                st.session_state.query_count += 1

                # Reset processing flag
                st.session_state.processing_query = False

                # Rerun to update UI
                st.rerun()
            else:
                st.error("Failed to transcribe audio")

st.divider()

# Text input
user_input = st.chat_input("Type your message here...")

if user_input and not st.session_state.processing_query:
    # Set processing flag
    st.session_state.processing_query = True

    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process query
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Query based on mode
            if st.session_state.use_api:
                response = query_api(user_input, api_url if 'api_url' in locals() else "http://localhost:8000")
            else:
                response = query_local(user_input)

            # Display response
            response_text = response.get('response_text', 'No response')
            st.markdown(response_text)

            # Generate audio response if voice mode is enabled
            audio_path = None
            if st.session_state.voice_mode and not st.session_state.use_api:
                with st.spinner("Generating audio..."):
                    audio_path = generate_audio_response(response_text)

                    if audio_path and os.path.exists(audio_path):
                        st.success("🔊 Audio response generated")
                        # Play the audio
                        with open(audio_path, "rb") as audio_file:
                            st.audio(audio_file.read(), format="audio/wav")
                    else:
                        st.warning("Could not generate audio response")

            # Show details
            if response.get('success'):
                details = format_response_details(response)

                # Show details expander
                with st.expander("📋 Details"):
                    st.markdown(details)

                # Show raw LLM output expander (separate, not nested)
                with st.expander("🔍 Raw LLM Output"):
                    st.code(response.get('raw_llm_output', ''), language='json')

    # Add assistant message to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "details": format_response_details(response) if response.get('success') else None,
        "raw_llm_output": response.get('raw_llm_output', ''),
        "audio_path": audio_path if st.session_state.voice_mode else None,
        "timestamp": datetime.now().isoformat()
    })

    # Increment query count
    st.session_state.query_count += 1

    # Reset processing flag
    st.session_state.processing_query = False

    # Rerun to update UI
    st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🎙️ Research Assistant with Speech I/O | Built with Streamlit, FastAPI, Llama3.2, LangChain, Whisper & CosyVoice</p>
    <p style='font-size: 0.8em;'>Audio Input: st.audio_input() | Audio Output: st.audio() | TTS: System/pyttsx3/CosyVoice</p>
</div>
""", unsafe_allow_html=True)
