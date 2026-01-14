# Configuration Guide

## Overview

The AI Voice Agent is now fully configurable through environment variables. You can customize the model, temperatures, and other settings without modifying code.

## Quick Start

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` to customize your settings**:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Set your model name**:
   ```bash
   LLM_MODEL=your-model-name-here
   ```

## Configuration Options

### LLM Model Settings

#### `LLM_MODEL`
- **Description**: The Ollama model to use for the agent
- **Default**: `hf.co/Christine-HiAiPerf/llama3-8b-qlora-finetuned-Q4_K_M-GGUF:Q4_K_M`
- **Examples**:
  ```bash
  # Use the default finetuned model
  LLM_MODEL=hf.co/Christine-HiAiPerf/llama3-8b-qlora-finetuned-Q4_K_M-GGUF:Q4_K_M

  # Use Llama 3.2
  LLM_MODEL=llama3.2:latest

  # Use a different custom model
  LLM_MODEL=my-custom-model:latest
  ```

#### `OLLAMA_BASE_URL`
- **Description**: The URL where Ollama is running
- **Default**: `http://localhost:11434`
- **Examples**:
  ```bash
  # Local Ollama
  OLLAMA_BASE_URL=http://localhost:11434

  # Remote Ollama server
  OLLAMA_BASE_URL=http://192.168.1.100:11434
  ```

#### `LLM_TEMPERATURE`
- **Description**: Temperature for general LLM responses (0.0 to 1.0)
- **Default**: `0.7`
- **Notes**: Higher = more creative, Lower = more focused

#### `SUMMARIZATION_TEMPERATURE`
- **Description**: Temperature specifically for summarization (0.0 to 1.0)
- **Default**: `0.3`
- **Notes**: Lower temperature for more consistent, focused summaries

### Whisper ASR Settings

#### `WHISPER_MODEL`
- **Description**: Which Whisper model size to use for speech recognition
- **Default**: `base`
- **Options**: `tiny`, `base`, `small`, `medium`, `large`
- **Notes**: Larger models are more accurate but slower

### TTS Settings

#### `TTS_BACKEND`
- **Description**: Which text-to-speech engine to use
- **Default**: `system`
- **Options**: `system`, `pyttsx3`, `cosyvoice`

### Tool Settings

#### `ARXIV_MAX_RESULTS`
- **Description**: Maximum number of papers to return from arXiv searches
- **Default**: `3`
- **Notes**: More results = better coverage but longer processing time

## How to Change Models

### Option 1: Using Environment Variables (Recommended)

1. Create or edit `.env`:
   ```bash
   LLM_MODEL=llama3.2:latest
   ```

2. Restart the backend:
   ```bash
   python backend.py
   ```

### Option 2: Using Shell Environment

```bash
export LLM_MODEL=llama3.2:latest
python backend.py
```

### Option 3: Direct Configuration (Not Recommended)

Edit `config.py` and change the default value:
```python
LLM_MODEL = os.getenv("LLM_MODEL", "your-model-here")
```

**Note**: Using environment variables is preferred as it keeps your configuration separate from code.

## Verifying Configuration

### Check Current Configuration

1. **Via Health Endpoint**:
   ```bash
   curl http://localhost:8000/health
   ```

   Response will show:
   ```json
   {
     "status": "healthy",
     "services": {
       "llm": "ollama/your-model-name",
       "stt": "whisper/base",
       "tts": "system",
       "tools": ["search_arxiv", "calculate", "summarize", "sync_to_notion"]
     },
     "config": {
       "ollama_url": "http://localhost:11434",
       "temperature": 0.7,
       "summarization_temperature": 0.3
     }
   }
   ```

2. **Via Config Script**:
   ```bash
   python config.py
   ```

   Output:
   ```
   Current Configuration:
   --------------------------------------------------
   ollama_base_url: http://localhost:11434
   llm_model: hf.co/Christine-HiAiPerf/...
   whisper_model: base
   tts_backend: system
   api_host: 0.0.0.0
   api_port: 8000
   ```

## Model Requirements

Your Ollama model should:
1. Support chat/instruction format
2. Be capable of generating JSON function calls
3. Handle multi-turn conversations
4. Be available in Ollama: `ollama list` should show it

## Troubleshooting

### Issue: "Model not found"

**Check if model is loaded in Ollama**:
```bash
ollama list
```

If not listed, pull it:
```bash
ollama pull your-model-name
```

### Issue: "Cannot connect to Ollama"

**Verify Ollama is running**:
```bash
# Start Ollama
ollama serve

# In another terminal, test connection
curl http://localhost:11434/api/tags
```

### Issue: Configuration not taking effect

**Make sure**:
1. `.env` file is in the project root directory
2. You restarted the backend after changing `.env`
3. No typos in environment variable names
4. `python-dotenv` is installed: `pip install python-dotenv`

## Advanced Configuration

### Multiple Environments

Create different environment files:
- `.env.development`
- `.env.production`
- `.env.testing`

Load specific environment:
```bash
# Using custom env file
cp .env.production .env
python backend.py
```

### Docker Configuration

If using Docker, pass environment variables:
```bash
docker run -e LLM_MODEL=llama3.2:latest your-image
```

## Best Practices

1. **Never commit `.env` to git**: Already in `.gitignore`
2. **Use `.env.example` as template**: Keep it updated with all options
3. **Document custom settings**: Add comments in your `.env`
4. **Test after changes**: Always verify with `/health` endpoint

## Configuration Priority

Settings are loaded in this order (later overrides earlier):
1. Default values in `config.py`
2. Environment variables from `.env` file
3. System environment variables

Example:
```python
# In config.py
LLM_MODEL = os.getenv("LLM_MODEL", "default-model")  # Default is "default-model"

# In .env
LLM_MODEL=env-file-model  # Overrides to "env-file-model"

# In shell
export LLM_MODEL=shell-model  # Overrides to "shell-model"
```

Final value: `shell-model`
