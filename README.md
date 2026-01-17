# AI Research Assistant

A full-stack AI-powered research assistant that accepts voice queries, searches academic papers, generates summaries, and persists conversations to Notion. Built with Whisper (ASR), Llama 3.2 (LLM), HuggingFace Transformers (Summarization), and CosyVoice (TTS).

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Features

- **🎤 Multi-Modal Input**: Voice (audio) or text queries
- **🔍 Academic Search**: Semantic search over ArXiv papers
- **📝 Auto-Summarization**: Condense research papers with HuggingFace transformers
- **💬 Conversational Context**: Follow-up questions with session memory
- **📚 Notion Integration**: Persist conversations and summaries to Notion database
- **🔊 Text-to-Speech**: Multiple TTS backends (system, pyttsx3, CosyVoice)
- **🖥️ Hardware Agnostic**: Auto-detects CUDA/MPS/CPU and optimizes accordingly
- **🎯 Function Calling**: LLM intelligently routes to tools (search, calculate, etc.)
- **⚡ RESTful API**: FastAPI backend with OpenAPI documentation
- **🎨 Interactive UI**: Streamlit frontend with audio I/O

---

## 📋 Table of Contents

- [Demo](#-demo)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎥 Demo

### Voice Query Example

```
User (voice): "What is quantum entanglement?"
   ↓ [Whisper transcribes]
Assistant: Searching ArXiv...
   ↓ [Finds 3 relevant papers]
   ↓ [Summarizes findings]
Assistant (voice): "Quantum entanglement is a phenomenon where particles..."
   ↓ [Saves to Notion]
✅ Conversation synced to Notion
```

### Follow-Up Question

```
User: "Tell me more about the second paper"
   ↓ [Uses session context to understand "second paper"]
Assistant: "The second paper, 'Quantum Teleportation...', discusses..."
```

---

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design and workflow diagrams.

### High-Level Overview

```
User Interface (Streamlit)
        ↓
FastAPI Backend
        ↓
    ┌───┴───┐
    ↓       ↓
  LLM   Session Manager
    ↓
Function Router
    ↓
┌───┼───┬───┐
↓   ↓   ↓   ↓
Search  Summarize  Notion  Calculate
(ArXiv) (HF)       (API)   (SymPy)
```

### Key Components

- **ASR**: Whisper (base/large-v3) for speech-to-text
- **LLM**: Llama 3.2 via Ollama for query understanding and function calling
- **Search**: ArXiv API for academic paper retrieval
- **Summarization**: HuggingFace BART for text condensation
- **TTS**: System (macOS 'say'), pyttsx3, or CosyVoice for speech synthesis
- **Persistence**: Notion API for conversation storage
- **Frontend**: Streamlit with audio input/output
- **Backend**: FastAPI with async endpoints

---

## 📦 Installation

### Prerequisites

- **macOS M3/M4** (development) or **Linux with NVIDIA GPU** (production)
- Python 3.10
- Conda/Miniconda
- Ollama (for LLM)

### Quick Install (macOS)

```bash
# 1. Clone repository
git clone https://github.com/christinezhaogmail/ai-research-assistant.git
cd ai-research-assistant

# 2. Create conda environment
conda env create -f env_mac.yml
conda activate ai-research-assistant-mac

# 3. Install Ollama
brew install ollama
ollama serve &
ollama pull llama3.2

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run tests
python test/test_all.py

# 6. Start application
python backend.py &
streamlit run frontend.py
```

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).

---

## 🚀 Quick Start

### 1. Start the Backend API

```bash
python backend.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (interactive Swagger UI)
- **Health**: http://localhost:8000/health

### 2. Start the Frontend UI

```bash
streamlit run frontend.py
```

The UI will be available at: http://localhost:8501

### 3. Use the Application

#### Via Web UI (Streamlit)

1. Open http://localhost:8501
2. Click "Record your question" to use voice input
3. Or type your question in the text box
4. View response with audio playback
5. Click "Sync to Notion" to save conversation

#### Via API (cURL)

```bash
# Text query
curl -X POST http://localhost:8000/ask \
  -F "text=What is quantum entanglement?"

# With session ID
curl -X POST http://localhost:8000/ask \
  -F "text=Tell me more" \
  -F "session_id=abc-123-def"

# Sync to Notion
curl -X POST http://localhost:8000/notion-sync \
  -F "session_id=abc-123-def"

# Check status
curl http://localhost:8000/status
```

---

## 📖 Usage

### Voice Queries

1. **Enable voice mode** in the sidebar
2. **Select TTS backend**: system (fastest), pyttsx3, or cosyvoice
3. **Click "Record your question"**
4. **Speak your query**
5. **Wait for transcription** (Whisper)
6. **View response** with audio playback

### Text Queries

1. **Type your question** in the chat input
2. **Press Enter**
3. **View response** with details (function calls, timing)

### Follow-Up Questions

The assistant maintains conversation context:

```
Query 1: "What is quantum entanglement?"
   → Returns 3 papers

Query 2: "Tell me more about the second paper"
   → Uses context to understand "second paper"

Query 3: "What about applications?"
   → Continues the conversation thread
```

### Notion Sync

1. **Set up Notion integration** (see Configuration)
2. **Have a conversation**
3. **Click "Sync to Notion"** or call `/notion-sync` endpoint
4. **View in Notion** with summary and full transcript

---

## 📚 API Documentation

### Endpoints

#### `GET /health`
Returns system health and available services.

```json
{
  "status": "healthy",
  "services": {
    "llm": "ollama/llama3.2",
    "stt": "whisper",
    "tts": "system",
    "tools": ["search_arxiv", "calculate"],
    "notion_sync": true
  }
}
```

#### `GET /status?session_id={id}`
Returns session status and information.

```json
{
  "status": "healthy",
  "session": {
    "session_id": "abc-123-def",
    "query_count": 3,
    "message_count": 6,
    "created_at": "2024-01-17T10:00:00"
  }
}
```

#### `POST /ask`
Main research assistant endpoint.

**Request:**
```bash
curl -X POST http://localhost:8000/ask \
  -F "text=What is quantum entanglement?" \
  -F "session_id=abc-123" \
  -F "include_summary=true"
```

**Response:**
```json
{
  "success": true,
  "session_id": "abc-123-def",
  "query_text": "What is quantum entanglement?",
  "response_text": "Found 3 papers on quantum entanglement...",
  "summary": "Quantum entanglement is a phenomenon...",
  "is_function_call": true,
  "function_name": "search_arxiv",
  "function_args": {"query": "quantum entanglement", "limit": 3},
  "processing_time": 2.5,
  "query_count": 1
}
```

#### `POST /notion-sync`
Sync conversation to Notion.

**Request:**
```bash
curl -X POST http://localhost:8000/notion-sync \
  -F "session_id=abc-123-def" \
  -F "include_summary=true"
```

**Response:**
```json
{
  "success": true,
  "session_id": "abc-123-def",
  "notion_url": "https://notion.so/page-xyz",
  "message": "Session synced successfully"
}
```

For complete API documentation, visit http://localhost:8000/docs when the backend is running.

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
LLM_TEMPERATURE=0.7

# ASR Configuration
WHISPER_MODEL=base  # or large-v3 on GPU

# TTS Configuration
TTS_BACKEND=system  # or pyttsx3, cosyvoice
COSYVOICE_PATH=/home/jovyan/CosyVoice
COSYVOICE_MODEL_DIR=/home/jovyan/CosyVoice/pretrained_models/CosyVoice-300M-SFT

# Notion Integration (Optional)
NOTION_TOKEN=secret_xyz123...
NOTION_DATABASE_ID=abc123def456...

# ArXiv Search
ARXIV_MAX_RESULTS=3

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_PORT=8501

# Logging
LOG_LEVEL=INFO
```

### Notion Setup

1. **Create Integration**:
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Copy the "Internal Integration Token"

2. **Create Database**:
   - Create a new database in Notion
   - Add properties:
     - `Session ID` (Text)
     - `Date` (Date)
     - `Query Count` (Number)
   - Share database with your integration

3. **Get Database ID**:
   - Open database in browser
   - Copy ID from URL: `notion.so/workspace/DATABASE_ID?v=...`

4. **Set Environment Variables**:
   ```bash
   export NOTION_TOKEN="secret_xyz..."
   export NOTION_DATABASE_ID="abc123..."
   ```

---

## 🧪 Testing

### Run All Tests

```bash
python test/test_all.py
```

### Run Individual Tests

```bash
# Hardware detection
python test/test_hardware.py

# Session management
python test/test_session_manager.py

# Academic search
python test/test_search.py

# Summarization (downloads model first run)
python test/test_summarize.py

# Notion sync (requires credentials)
python test/test_notion.py

# API models
python test/test_api_models.py
```

See [test/README.md](test/README.md) for detailed testing documentation.

---

## 📁 Project Structure

```
ai-research-assistant/
├── backend.py              # FastAPI backend entry point
├── frontend.py             # Streamlit frontend
├── api.py                  # Pydantic data models
├── config.py               # Configuration management
├── llm_service.py          # LLM integration (Ollama)
├── function_router.py      # Function call routing
├── agent_tools.py          # LangChain tools (search_arxiv, calculate)
├── audio_service.py        # Legacy audio services
│
├── models/                 # AI Model layer
│   ├── __init__.py
│   ├── asr.py             # VoiceTranscriber (Whisper)
│   └── tts.py             # VoiceSynthesizer (CosyVoice/system)
│
├── tools/                  # Tool layer
│   ├── __init__.py
│   ├── search.py          # AcademicSearch (ArXiv)
│   ├── summarize.py       # ContentSummarizer (HuggingFace)
│   └── notion.py          # NotionSync (Notion API)
│
├── utils/                  # Utility layer
│   ├── __init__.py
│   ├── hardware.py        # Hardware detection (CUDA/MPS/CPU)
│   ├── logger.py          # Logging and tool call wrapping
│   └── session_manager.py # Session and conversation management
│
├── test/                   # Test suite
│   ├── README.md
│   ├── test_all.py
│   ├── test_hardware.py
│   ├── test_session_manager.py
│   ├── test_search.py
│   ├── test_summarize.py
│   ├── test_notion.py
│   └── test_api_models.py
│
├── logs/                   # Application logs
├── .env                    # Environment variables (not in git)
├── .env.example           # Example environment file
├── requirements.txt       # Python dependencies
├── env_mac.yml           # Conda environment (macOS)
├── env_server.yml        # Conda environment (GPU server)
├── ARCHITECTURE.md       # System architecture documentation
├── INSTALLATION.md       # Detailed installation guide
└── README.md             # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests before committing
python test/test_all.py

# Format code
black .
isort .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI Whisper** for speech recognition
- **Meta Llama** for language understanding
- **HuggingFace** for summarization models
- **ArXiv** for academic paper access
- **Notion** for knowledge management
- **FastAPI** for API framework
- **Streamlit** for web interface

---

## 📞 Support

For issues, questions, or suggestions:
- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/christinezhaogmail/ai-research-assistant/issues)
- 📖 Documentation: [Full docs](https://github.com/christinezhaogmail/ai-research-assistant/wiki)

---

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] PubMed and Semantic Scholar integration
- [ ] Vector database for semantic caching
- [ ] Voice cloning with reference audio
- [ ] Mobile app (React Native)
- [ ] Docker containerization
- [ ] Cloud deployment templates (AWS, GCP, Azure)
- [ ] Citation management integration (Zotero, Mendeley)

---

**Built with ❤️ for researchers and AI enthusiasts**
