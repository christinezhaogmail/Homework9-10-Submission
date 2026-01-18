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
if 'session_id' not in st.session_state:
    st.session_state.session_id = None  # Will be created on first query
if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"
if 'notion_sync_enabled' not in st.session_state:
    st.session_state.notion_sync_enabled = True  # Default: Notion sync enabled


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


def query_api(text: str) -> Dict[str, Any]:
    """
    Query the FastAPI backend with session support

    Args:
        text: User's query text

    Returns:
        Response dictionary
    """
    try:
        # Prepare form data
        data = {"text": text}

        # Add session_id if we have one
        if st.session_state.session_id:
            data["session_id"] = st.session_state.session_id

        api_url = st.session_state.api_url
        response = requests.post(
            f"{api_url}/ask",
            data=data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()

        # Update session_id if returned
        if "session_id" in result:
            st.session_state.session_id = result["session_id"]
            logger.info(f"Session ID updated: {result['session_id']}")

        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_text": f"Error connecting to API: {str(e)}"
        }


def query_local(text: str) -> Dict[str, Any]:
    """
    Query using local services (no API) with conversation context

    Args:
        text: User's query text

    Returns:
        Response dictionary
    """
    try:
        start_time = time.time()

        # Get conversation history from messages (last 10 for context)
        # Exclude the current user message which is already in the messages list
        conversation_history = []
        if st.session_state.messages:
            # Get messages except the last one (which is the current query)
            recent_messages = st.session_state.messages[:-1][-10:]  # Exclude last, then take last 10
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in recent_messages
            ]

        # Get LLM response with conversation history
        llm_output = st.session_state.llm_service.generate_response(
            text,
            conversation_history=conversation_history
        )

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


def sync_to_notion() -> Dict[str, Any]:
    """
    Sync current conversation to Notion

    Returns:
        Response dictionary with success status and Notion URL
    """
    try:
        if not st.session_state.session_id:
            return {
                "success": False,
                "message": "No active session to sync"
            }

        response = requests.post(
            f"{st.session_state.api_url}/notion-sync",
            data={
                "session_id": st.session_state.session_id,
                "include_summary": True
            },
            timeout=30
        )

        if response.ok:
            return response.json()
        else:
            return {
                "success": False,
                "message": f"API error: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


# Main UI
st.title("🤖 Research Assistant")

# Show voice mode status
if st.session_state.voice_mode:
    st.success("🎙️ Voice Mode: **Enabled** - Audio input and output active")
else:
    st.info("💬 Text Mode: Voice mode disabled")

st.markdown("Ask me anything! I can search scientific papers and perform calculations.")

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
        st.session_state.api_url = api_url  # Store in session state
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

    # Store previous state to detect changes
    previous_voice_mode = st.session_state.voice_mode

    voice_mode = st.checkbox(
        "Enable Voice Mode",
        value=st.session_state.voice_mode,
        help="Enable audio input and output"
    )

    # Detect change and trigger rerun if needed
    if voice_mode != previous_voice_mode:
        st.session_state.voice_mode = voice_mode
        st.rerun()

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

    # Session Management
    st.header("💬 Session Management")

    if st.session_state.session_id:
        st.success(f"🔗 Active Session")
        st.code(st.session_state.session_id, language="text")
        st.caption("Session ID is maintained across queries for conversation context")

        if st.button("🔄 Start New Session"):
            st.session_state.session_id = None
            st.session_state.messages = []
            st.session_state.query_count = 0
            st.success("New session created!")
            st.rerun()
    else:
        st.info("🆕 No active session - will be created on first query")

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
        st.session_state.session_id = None
        st.rerun()

    st.divider()

    # Notion Sync (always visible in API mode)
    if st.session_state.use_api:
        st.header("📝 Notion Sync")

        # Auto-sync toggle
        notion_sync_enabled = st.checkbox(
            "Auto-sync to Notion",
            value=st.session_state.notion_sync_enabled,
            help="Automatically save conversations to Notion after each query"
        )
        st.session_state.notion_sync_enabled = notion_sync_enabled

        # Show session status
        if st.session_state.session_id:
            st.caption(f"✅ Active session: `{st.session_state.session_id[:20]}...`")
        else:
            st.caption("⏳ No active session yet (will be created on first query)")

        # Manual sync button
        if st.button("💾 Sync Now"):
            if not st.session_state.session_id:
                st.warning("⚠️ No active session. Ask a question first!")
            else:
                with st.spinner("Syncing to Notion..."):
                    result = sync_to_notion()

                    if result.get("success"):
                        st.success("✅ Synced to Notion!")
                        if result.get("notion_url"):
                            st.markdown(f"[Open in Notion]({result['notion_url']})")
                    else:
                        st.error(f"❌ Sync failed: {result.get('message', 'Unknown error')}")

        if notion_sync_enabled:
            st.caption("🔄 Auto-sync is enabled - conversations will be saved automatically")

    st.divider()

    # Example queries
    st.header("💡 Example Queries")
    st.markdown("""
    **arXiv Search with Follow-ups:**
    - What is quantum entanglement?
    - *Then ask:* Tell me more about the second paper
    - *Then ask:* What are the practical applications?

    **Math Calculations:**
    - What is 25 multiplied by 4?
    - Calculate sqrt(144)
    - What is 1 divided by 0?

    **Conversation Context:**
    - Find papers on neural networks
    - *Then ask:* Which one is most recent?
    - *Then ask:* Summarize the first one

    **General Chat:**
    - Hello, how are you?
    - Tell me about yourself
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
                            response = query_api(transcription)
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

                # Auto-sync to Notion if enabled and using API mode
                if st.session_state.use_api and st.session_state.notion_sync_enabled and st.session_state.session_id:
                    logger.info("Auto-syncing to Notion...")
                    sync_result = sync_to_notion()
                    if sync_result.get("success"):
                        logger.info(f"✅ Auto-synced to Notion: {sync_result.get('notion_url', 'No URL')}")

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
                response = query_api(user_input)
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

    # Auto-sync to Notion if enabled and using API mode
    if st.session_state.use_api and st.session_state.notion_sync_enabled and st.session_state.session_id:
        logger.info("Auto-syncing to Notion...")
        sync_result = sync_to_notion()
        if sync_result.get("success"):
            logger.info(f"✅ Auto-synced to Notion: {sync_result.get('notion_url', 'No URL')}")

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
