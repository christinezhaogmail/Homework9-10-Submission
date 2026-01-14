# AI Voice Agent with Function Calling

An intelligent voice-enabled AI agent that can listen to user queries, process them using LLM (my-lama3-finetuned-Q4_K_M), execute tools (arXiv search and mathematical calculations), and respond with synthesized speech.

## Features

- **Voice Interaction**: Speech-to-Text using OpenAI Whisper
- **Intelligent LLM**: my-lama3-finetuned-Q4_K_M via Ollama with function calling capabilities
- **Tool Execution**:
  - `search_arxiv`: Search scientific papers on arXiv
  - `calculate`: Perform mathematical calculations using SymPy
- **Text-to-Speech**: Multiple TTS backends
  - System TTS (macOS `say` command)
  - pyttsx3 (cross-platform)
  - **CosyVoice** (high-quality neural TTS, GPU-accelerated)
- **FastAPI Backend**: RESTful API for all agent operations
- **Streamlit Frontend**: Interactive web interface with **full voice I/O**
  - **Audio Input**: `st.audio_input()` for voice queries
  - **Audio Output**: `st.audio()` for spoken responses
  - **Seamless text/voice mixing**
- **GPU Support**: Full CUDA support with PyTorch for deployment on NVIDIA GPUs
- **Comprehensive Logging**: Detailed logs for debugging and analysis
- **Error Handling**: Graceful handling of edge cases (e.g., division by zero)

## Architecture

```
User Voice Input → Whisper (STT) → my-lama3-finetuned-Q4_K_M (LLM) → Function Router → Tools
                                                                           ↓
User Voice Output ← TTS ← Response Text ← Function Result ← [calculate/search_arxiv]
```

## Prerequisites

- Python 3.11+
- Conda (recommended for environment management)
- Ollama with my-lama3-finetuned-Q4_K_M model installed
- macOS (for system TTS) or pyttsx3 for other platforms

**macOS M3 Users**: See [MACOS_SETUP.md](MACOS_SETUP.md) for optimized setup instructions.

**GPU Deployment**: For NVIDIA GPU deployment with CosyVoice, see [GPU_DEPLOYMENT.md](GPU_DEPLOYMENT.md).

## Installation

### 1. Create Conda Environment

```bash
# Create and activate conda environment
conda create -n hw9_311 python=3.11 -y
conda activate hw9_311
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Whisper model (first time only)
python -c "import whisper; whisper.load_model('base')"
```

### 3. Install and Setup Ollama

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull my-lama3-finetuned-Q4_K_M model
ollama pull my-lama3-finetuned-Q4_K_M

# Start Ollama server (in a separate terminal)
ollama serve
```

### 4. Create Logs Directory

```bash
mkdir -p logs
```

## Project Structure

```
Homework6-Submission/
├── agent_tools.py          # LangChain tools (search_arxiv, calculate)
├── llm_service.py          # LLM integration with Ollama
├── function_router.py      # Function call detection and routing
├── audio_service.py        # Speech-to-Text and Text-to-Speech
├── backend.py              # FastAPI REST API server
├── frontend.py             # Streamlit web interface
├── config.py               # Configuration settings
├── test_agent.py           # Comprehensive test suite
├── requirements.txt        # Python dependencies
├── logs/                   # Log files directory
└── README.md              # This file
```

## Usage

### Option 1: Run Complete Test Suite

Test all components before running the full application:

```bash
python test_agent.py
```

This will test:
- Individual tools (calculate, search_arxiv)
- LLM service
- Function router
- End-to-end integration

### Option 2: Run with Streamlit Frontend (Recommended)

```bash
# Start Streamlit app (includes all services)
streamlit run frontend.py
```

Access the web interface at: `http://localhost:8501`

The Streamlit app can run in two modes:
1. **Local Mode**: Direct processing without API (default) - **Supports voice I/O**
2. **API Mode**: Uses FastAPI backend (requires backend.py to be running)

#### 🎙️ Using Voice Features in Streamlit

Enable voice interaction in the Streamlit interface:

1. **Open the app**: `streamlit run frontend.py`
2. **Enable Voice Mode**: Check "Enable Voice Mode" in the sidebar
3. **Record audio**: Click the 🎤 microphone button to record your question
4. **Get audio response**: Hear the response with automatic audio playback
5. **Choose TTS backend**: Select system (fastest), pyttsx3, or cosyvoice

See [VOICE_UI_GUIDE.md](VOICE_UI_GUIDE.md) for detailed voice UI documentation.

### Option 3: Run with FastAPI Backend + Streamlit

Terminal 1 - Start FastAPI backend:
```bash
python backend.py
```

Terminal 2 - Start Streamlit frontend:
```bash
streamlit run frontend.py
```

Then enable "Use API Mode" in the Streamlit sidebar.

API Documentation: `http://localhost:8000/docs`

### Option 4: Use API Directly

Start the backend:
```bash
python backend.py
```

Test with curl:
```bash
# Text query
curl -X POST "http://localhost:8000/api/voice-query/" \
  -H "Content-Type: application/json" \
  -d '{"text": "What is 25 multiplied by 4?"}'

# Health check
curl http://localhost:8000/health
```

## Example Queries

### Mathematical Calculations
- "What is 25 multiplied by 4?"
- "Calculate the square root of 144"
- "What is 100 divided by 5?"
- "What is 1 divided by 0?" (tests error handling)

### arXiv Paper Search
- "What is quantum entanglement?"
- "Search for papers on neural networks"
- "Find research about climate change"
- "Show me papers on large language models"

### General Conversation
- "Hello, how are you?"
- "Tell me about yourself"
- "What can you do?"

## API Endpoints

### Main Endpoints

- **POST** `/api/voice-query/` - Main query endpoint
  ```json
  {
    "text": "What is 2+2?"
  }
  ```

- **POST** `/api/text-query/` - Text-only query
- **POST** `/api/transcribe/` - Transcribe audio file
- **POST** `/api/synthesize/` - Convert text to speech
- **POST** `/api/full-voice-query/` - Complete voice pipeline
- **GET** `/health` - Health check

### Response Format

```json
{
  "success": true,
  "query_text": "What is 2+2?",
  "raw_llm_output": "{\"function\": \"calculate\", \"arguments\": {\"expression\": \"2+2\"}}",
  "is_function_call": true,
  "function_name": "calculate",
  "function_args": {"expression": "2+2"},
  "response_text": "The result is: 4",
  "processing_time": 1.23
}
```

## Logging

All operations are logged to:
- Console output (INFO level)
- `logs/voice_agent_*.log` (rotating daily, kept for 7 days)

Logs include:
1. User's query text
2. Raw LLM response
3. Function call detection
4. Function name and arguments
5. Function execution result
6. Final response to user
7. Processing time

Example log entry:
```
2024-12-14 10:30:45 | INFO | === NEW QUERY ===
2024-12-14 10:30:45 | INFO | User Query: What is 25 multiplied by 4?
2024-12-14 10:30:46 | INFO | Raw LLM Output: {"function": "calculate", "arguments": {"expression": "25*4"}}
2024-12-14 10:30:46 | INFO | Is Function Call: True
2024-12-14 10:30:46 | INFO | Function Name: calculate
2024-12-14 10:30:46 | INFO | Function Args: {'expression': '25*4'}
2024-12-14 10:30:46 | INFO | Final Response: The result is: 100
```

## Error Handling

The agent handles various error scenarios gracefully:

1. **Division by Zero**: Returns a friendly error message
2. **Invalid Math Expression**: Catches SymPy errors
3. **No arXiv Results**: Returns "No papers found" message
4. **LLM Connection Error**: Returns connection error message
5. **Malformed Function Call**: Falls back to text response
6. **Unknown Function**: Returns list of available functions

## Configuration

Configure the agent using environment variables or `config.py`:

```python
# LLM settings
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "my-lama3-finetuned-Q4_K_M"

# Whisper settings
WHISPER_MODEL = "base"  # tiny, base, small, medium, large

# TTS settings
TTS_BACKEND = "system"  # system, pyttsx3, cosyvoice

# CosyVoice settings (for high-quality neural TTS)
COSYVOICE_PATH = "/Users/huiruzhao/github/inference/CosyVoice"
COSYVOICE_MODEL_DIR = "/Users/huiruzhao/github/inference/CosyVoice/pretrained_models/CosyVoice-300M-SFT"

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
```

### Using CosyVoice (Advanced TTS)

If you have CosyVoice installed:

1. **Set environment variables**:
   ```bash
   export COSYVOICE_PATH=/path/to/CosyVoice
   export COSYVOICE_MODEL_DIR=/path/to/CosyVoice/pretrained_models/CosyVoice-300M-SFT
   export TTS_BACKEND=cosyvoice
   ```

2. **Test CosyVoice integration**:
   ```bash
   python test_cosyvoice.py
   ```

3. **Run the agent**:
   ```bash
   python quick_start.py
   # or
   streamlit run frontend.py
   ```

For GPU deployment with CosyVoice, see [GPU_DEPLOYMENT.md](GPU_DEPLOYMENT.md).

## Testing Workflow

1. **Component Tests**: Run `python test_agent.py` to verify all components
2. **API Tests**: Start backend and use curl or Postman
3. **Frontend Tests**: Open Streamlit app and try example queries
4. **Voice Tests**: Use microphone input (if hardware available)

## Troubleshooting

### Issue: "Cannot connect to Ollama"
**Solution**: Start Ollama server with `ollama serve`

### Issue: "Whisper model not loaded"
**Solution**: Install Whisper: `pip install openai-whisper`

### Issue: "TTS not working"
**Solution**:
- macOS: Should work with system TTS
- Other OS: Install pyttsx3: `pip install pyttsx3`

### Issue: "Module not found"
**Solution**: Ensure conda environment is activated: `conda activate hw9_311`

### Issue: "API connection refused"
**Solution**: Start the backend server: `python backend.py`

## Advanced Features

### Adding New Tools

1. Create a new tool in `agent_tools.py`:
```python
@tool
def my_new_tool(param: str) -> str:
    """Tool description"""
    # Implementation
    return result
```

2. Add to tool registry:
```python
TOOL_REGISTRY["my_new_tool"] = my_new_tool
ALL_TOOLS.append(my_new_tool)
```

3. Update system prompt in `llm_service.py` to include the new tool

### Using Different LLMs

Modify `llm_service.py` to use `AlternativeLLMService` with OpenAI:

```python
llm = AlternativeLLMService(api_key="your-api-key", model="gpt-4")
```

## Performance

- **Average response time**: 1-3 seconds (local processing)
- **Whisper transcription**: < 1 second for short audio
- **LLM inference**: 1-2 seconds (depends on query complexity)
- **Function execution**: < 0.5 seconds

## Future Enhancements

- [ ] Add more tools (weather, web search, etc.)
- [ ] Implement CosyVoice for better TTS
- [ ] Add conversation memory/context
- [ ] Support for chained tool calls
- [ ] Real-time audio streaming
- [ ] Multi-language support
- [ ] User authentication

## Credits

- **LLM**: my-lama3-finetuned-Q4_K_M via Ollama
- **STT**: OpenAI Whisper
- **Tools**: LangChain, arXiv API, SymPy
- **Web Framework**: FastAPI, Streamlit
- **Logging**: Loguru

## License

MIT License - See LICENSE file for details

## Assignment Submission

This project fulfills the Week 6 Assignment requirements:

✅ Function calling with Llama 3 (via Ollama)
✅ Two tools implemented (search_arxiv, calculate)
✅ Intent parsing and function routing
✅ Voice agent pipeline (STT → LLM → Tool → TTS)
✅ Prompt engineering for structured outputs
✅ Error handling for edge cases
✅ Comprehensive logging
✅ FastAPI endpoint implementation
✅ Tool registry for extensibility

## Contact

For questions or issues, please refer to the course materials or create an issue in the repository.
