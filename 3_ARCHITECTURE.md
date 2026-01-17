# AI Research Assistant - System Architecture

## 🏗️ High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                              │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      Streamlit Frontend                              │   │
│  │  - Audio Input (st.audio_input)                                      │   │
│  │  - Text Input (st.chat_input)                                        │   │
│  │  - Chat Display                                                      │   │
│  │  - TTS Backend Selector (system/pyttsx3/cosyvoice)                   │   │
│  │  - Audio Playback (st.audio)                                         │   │
│  └────────────────────┬─────────────────────────────────────────────────┘   │
│                       │                                                     │
└───────────────────────┼─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API LAYER (FastAPI)                              │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  GET /health │  │ GET /status  │  │  POST /ask   │  │POST /notion- │     │
│  │              │  │              │  │              │  │    sync      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                                             │
│  Data Models (api.py): AskRequest, AskResponse, NotionSyncRequest, etc.     │
│                                                                             │
└───────────────────────┬─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER                                 │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                     Session Manager                                │     │
│  │  - Creates unique session IDs (UUID)                               │     │
│  │  - Tracks conversation history                                     │     │
│  │  - Maintains context for follow-up questions                       │     │
│  │  - Query counting                                                  │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                     Function Router                                │     │
│  │  - Parses LLM output for function calls                            │     │
│  │  - Routes to appropriate tools                                     │     │
│  │  - Returns formatted results                                       │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└───────────────────────┬─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MODEL LAYER (models/)                              │
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐       │
│  │     ASR      │    │     TTS      │    │       LLM Service        │       │
│  │   (asr.py)   │    │   (tts.py)   │    │    (llm_service.py)      │       │
│  ├──────────────┤    ├──────────────┤    ├──────────────────────────┤       │
│  │ Whisper      │    │ - system     │    │ Ollama/Llama3.2          │       │
│  │ (base/large) │    │ - pyttsx3    │    │ - Function calling       │       │
│  │              │    │ - CosyVoice  │    │ - Context management     │       │
│  │ Device:      │    │              │    │                          │       │
│  │ CUDA/MPS/CPU │    │ Device:      │    │ System prompts           │       │
│  │              │    │ CUDA/MPS/CPU │    │                          │       │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TOOLS LAYER (tools/)                               │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐       │
│  │ Academic Search  │  │ Summarization    │  │   Notion Sync        │       │
│  │   (search.py)    │  │ (summarize.py)   │  │    (notion.py)       │       │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────────┤       │
│  │ - ArXiv API      │  │ HuggingFace      │  │ Notion API Client    │       │
│  │ - Semantic search│  │ Transformers     │  │ - Database creation  │       │
│  │ - Multi-source   │  │ BART/T5 models   │  │ - Page creation      │       │
│  │   support        │  │                  │  │ - Content appending  │       │
│  │                  │  │ Device:          │  │                      │       │
│  │ Top-K results    │  │ CUDA/MPS/CPU     │  │ Session persistence  │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       UTILITY LAYER (utils/)                                │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐       │
│  │ Hardware         │  │ Logger           │  │ Session Manager      │       │
│  │ Detection        │  │                  │  │                      │       │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────────┤       │
│  │ - CUDA check     │  │ - Tool call      │  │ - UUID generation    │       │
│  │ - MPS check      │  │   wrapping       │  │ - History buffer     │       │
│  │ - CPU fallback   │  │ - Timing         │  │ - Metadata storage   │       │
│  │                  │  │ - File logging   │  │                      │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Request Flow Diagram

### Flow 1: Voice Query with ArXiv Search

```
┌──────────┐
│  User    │ Speaks: "What is quantum entanglement?"
│          │
└────┬─────┘
     │ 🎤 Audio Input
     ▼
┌─────────────────────────────────────────────────────────┐
│ Streamlit Frontend                                      │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ st.audio_input() captures audio bytes               │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 1: Speech-to-Text (ASR)                            │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ models/asr.py → VoiceTranscriber                    │ │
│ │ - Whisper model processes audio                     │ │
│ │ - Device: Auto-detect (CUDA/MPS/CPU)                │ │
│ │ - Output: "What is quantum entanglement?"           │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Transcribed Text
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: Session Management                              │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ utils/session_manager.py → SessionManager           │ │
│ │ - Create/Get session ID (e.g., "abc-123-def")       │ │
│ │ - Add user message to history                       │ │
│ │ - Query count: 1                                    │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Session ID + Message History
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: LLM Processing                                  │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ llm_service.py → LLMService                         │ │
│ │ - Send query to Ollama/Llama3.2                     │ │
│ │ - System prompt includes function definitions       │ │
│ │ - LLM decides to call search_arxiv()                │ │
│ │ - Output: {                                         │ │
│ │     "function": "search_arxiv",                     │ │
│ │     "args": {"query": "quantum entanglement", ...}  │ │
│ │   }                                                 │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Function Call Detected
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 4: Function Routing                                │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ function_router.py → FunctionRouter                 │ │
│ │ - Parse LLM output (JSON detection)                 │ │
│ │ - Validate function name: "search_arxiv"            │ │
│ │ - Extract arguments                                 │ │
│ │ - Route to appropriate tool                         │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Routed to search_arxiv
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 5: ArXiv Search                                    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ tools/search.py → AcademicSearch                    │ │
│ │ - Query ArXiv API                                   │ │
│ │ - Retrieve top-3 papers                             │ │
│ │ - Extract: title, authors, abstract, URL            │ │
│ │ - Return formatted results                          │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Search Results (3 papers)
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 6: Summarization (Optional)                        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ tools/summarize.py → ContentSummarizer              │ │
│ │ - HuggingFace Transformers (BART/T5)                │ │
│ │ - Condense paper abstracts                          │ │
│ │ - Generate concise summaries                        │ │
│ │ - Device: Auto-detect (CUDA/MPS/CPU)                │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Summarized Results
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 7: Response Generation                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ backend.py → /ask endpoint                          │ │
│ │ - Combine search results + summaries                │ │
│ │ - Format as readable text                           │ │
│ │ - Add to session history (assistant message)        │ │
│ │ - Prepare AskResponse model                         │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Response Text
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 8: Text-to-Speech (TTS)                            │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ models/tts.py → VoiceSynthesizer                    │ │
│ │ - Backend: system/pyttsx3/CosyVoice                 │ │
│ │ - Convert response text to audio                    │ │
│ │ - Save to temp file (.wav/.aiff)                    │ │
│ │ - Return audio path                                 │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Audio File Path
     ▼
┌─────────────────────────────────────────────────────────┐
│ Streamlit Frontend                                      │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Display response text in chat                       │ │
│ │ st.audio() plays audio response                     │ │
│ │ Show details (function calls, timing, etc.)         │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌──────────┐
│  User    │ Hears response and sees results
│          │
└──────────┘
```

---

## 🔄 Flow 2: Follow-up Question with Context

```
┌──────────┐
│  User    │ Types: "Tell me more about the second paper"
│          │
└────┬─────┘
     │ Text Input
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 1: Session Context Retrieval                       │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ SessionManager retrieves existing session           │ │
│ │ - Session ID: "abc-123-def"                         │ │
│ │ - Previous messages: [                              │ │
│ │     {user: "What is quantum entanglement?"},        │ │
│ │     {assistant: "Here are 3 papers..."}             │ │
│ │   ]                                                 │ │
│ │ - Query count: 2                                    │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Context-aware query
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: LLM with Context                                │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ LLMService receives:                                │ │
│ │ - Current query: "Tell me more about 2nd paper"     │ │
│ │ - Conversation history (last 10 turns)              │ │
│ │                                                     │ │
│ │ LLM understands "second paper" refers to:           │ │
│ │ - Paper #2 from previous search results             │ │
│ │                                                     │ │
│ │ LLM generates contextual response using history     │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Contextual Response
     ▼
┌─────────────────────────────────────────────────────────┐
│ Continue normal flow...                                 │
│ (Session update → Response → TTS → Display)             │
└─────────────────────────────────────────────────────────┘
```

---

## 💾 Flow 3: Notion Sync

```
┌──────────┐
│  User    │ Clicks "Sync to Notion" button
│          │
└────┬─────┘
     │ POST /notion-sync
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 1: Session Retrieval                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ SessionManager gets full conversation               │ │
│ │ - All messages (user + assistant)                   │ │
│ │ - Metadata (query_count, timestamps)                │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Conversation Data
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: Generate Summary                                │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ContentSummarizer                                   │ │
│ │ - Combine all messages into single text             │ │
│ │ - Generate 200-word summary                         │ │
│ │ - Extract key topics and findings                   │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Summary Text
     ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: Notion API Call                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ tools/notion.py → NotionSync                        │ │
│ │ - Authenticate with NOTION_TOKEN                    │ │
│ │ - Create page in database (NOTION_DATABASE_ID)      │ │
│ │ - Page structure:                                   │ │
│ │   • Title: "Research Session: abc-123-def"          │ │
│ │   • Properties: session_id, date, query_count       │ │
│ │   • Content blocks:                                 │ │
│ │     - Summary section                               │ │
│ │     - Full conversation                             │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Notion Page URL
     ▼
┌─────────────────────────────────────────────────────────┐
│ NotionSyncResponse                                      │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ {                                                   │ │
│ │   "success": true,                                  │ │
│ │   "session_id": "abc-123-def",                      │ │
│ │   "notion_url": "https://notion.so/...",            │ │
│ │   "message": "Session synced successfully"          │ │
│ │ }                                                   │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌──────────┐
│  User    │ Clicks URL to view in Notion
│          │
└──────────┘
```

---

## 🖥️ Platform-Specific Hardware Flow

```
┌─────────────────────────────────────────────────────────┐
│                   System Startup                        │
└────┬────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ utils/hardware.py → get_device()                        │
│                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────┐    │
│  │ Check CUDA?  │──>│  Check MPS?  │──>│ Use CPU   │    │
│  │ (NVIDIA GPU) │   │ (Apple M3/M4)│   │           │    │
│  └──────┬───────┘   └──────┬───────┘   └─────┬─────┘    │
│         │ Yes              │ Yes              │         │
│         ▼                  ▼                  ▼         │
│    "cuda"              "mps"               "cpu"        │
└────┬────────────────────────────────────────────────────┘
     │ Device String
     ▼
┌─────────────────────────────────────────────────────────┐
│ All models use detected device:                         │
│                                                         │
│ ┌───────────────────────────────────────────────────┐   │
│ │ VoiceTranscriber(device="cuda")                   │   │
│ │ ContentSummarizer(device="cuda")                  │   │
│ │ VoiceSynthesizer(device="cuda")                   │   │
│ └───────────────────────────────────────────────────┘   │
│                                                         │
│ macOS M3/M4 Dev:     GPU Server Production:             │
│ ├─ Whisper on MPS    ├─ Whisper on CUDA                 │
│ ├─ BART on MPS       ├─ BART on CUDA                    │
│ ├─ System TTS        └─ CosyVoice on CUDA               │
│ └─ No CosyVoice                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Data Models Flow (api.py)

```
┌─────────────────────────────────────────────────────────┐
│                    api.py                               │
│                                                         │
│  Request Models                  Response Models        │
│  ┌──────────────┐               ┌──────────────┐        │
│  │ AskRequest   │──────────────>│ AskResponse  │        │
│  ├──────────────┤               ├──────────────┤        │
│  │ - text       │               │ - success    │        │
│  │ - session_id │               │ - session_id │        │
│  │ - include_   │               │ - response_  │        │
│  │   summary    │               │   text       │        │
│  └──────────────┘               │ - summary    │        │
│                                 │ - function_  │        │
│  ┌──────────────┐               │   metadata   │        │
│  │ NotionSync   │               │ - processing │        │
│  │ Request      │──┐            │   _time      │        │
│  ├──────────────┤  │            │ - query_count│        │
│  │ - session_id │  │            └──────────────┘        │
│  │ - include_   │  │                                    │
│  │   summary    │  │            ┌──────────────┐        │
│  └──────────────┘  └───────────>│ NotionSync   │        │
│                                 │ Response     │        │
│                                 ├──────────────┤        │
│                                 │ - success    │        │
│                                 │ - notion_url │        │
│                                 │ - message    │        │
│                                 └──────────────┘        │
│                                                         │
│  All requests/responses validated by Pydantic           │
│  FastAPI auto-generates OpenAPI docs from these models  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Configuration & Environment

```
┌─────────────────────────────────────────────────────────┐
│                  .env File                              │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ # LLM Configuration                                 │ │
│ │ OLLAMA_BASE_URL=http://localhost:11434              │ │
│ │ LLM_MODEL=llama3.2                                  │ │
│ │                                                     │ │
│ │ # ASR/TTS Configuration                             │ │
│ │ WHISPER_MODEL=base                                  │ │
│ │ TTS_BACKEND=system  # or pyttsx3, cosyvoice         │ │
│ │ COSYVOICE_PATH=/home/jovyan/CosyVoice                   │ │
│ │                                                     │ │
│ │ # Notion Integration                                │ │
│ │ NOTION_TOKEN=ntn_xyz123...                       │ │
│ │ NOTION_DATABASE_ID=abc123...                        │ │
│ │                                                     │ │
│ │ # ArXiv                                             │ │
│ │ ARXIV_MAX_RESULTS=3                                 │ │
│ └─────────────────────────────────────────────────────┘ │
└────┬────────────────────────────────────────────────────┘
     │ Loaded by config.py
     ▼
┌─────────────────────────────────────────────────────────┐
│                  config.py                              │
│ Provides configuration to all modules                   │
└─────────────────────────────────────────────────────────┘
```

---

## Summary

This architecture follows a **modular, layered design**:

1. **User Interface Layer**: Streamlit frontend for user interaction
2. **API Layer**: FastAPI with RESTful endpoints and Pydantic models
3. **Orchestration Layer**: Session management and function routing
4. **Model Layer**: AI models (ASR, TTS, LLM)
5. **Tools Layer**: Search, summarization, Notion sync
6. **Utility Layer**: Hardware detection, logging, helpers

**Key Features**:
- ✅ **Session-based conversations** with unique IDs and history
- ✅ **Function calling** for intelligent tool selection
- ✅ **Multi-modal I/O** (voice + text)
- ✅ **Platform-agnostic** (auto-detects CUDA/MPS/CPU)
- ✅ **Persistent storage** via Notion API
- ✅ **Automatic summarization** using HuggingFace
- ✅ **Type-safe APIs** with Pydantic validation
