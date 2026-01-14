# macOS Setup Guide (M3/Apple Silicon)

Special instructions for setting up the AI Voice Agent on macOS with Apple Silicon (M3, M2, M1).

## Quick Fix for Installation Issues

If you encounter errors during `pip install -r requirements.txt`, follow these steps:

### 1. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install System Dependencies

```bash
# Install portaudio (for audio processing)
brew install portaudio

# Install espeak (optional, for better TTS)
brew install espeak
```

### 3. Create and Activate Conda Environment

```bash
# Create environment with Python 3.11
conda create -n hw9_311 python=3.11 -y

# Activate environment
conda activate hw9_311
```

### 4. Install Python Packages

```bash
# Install requirements (pyaudio removed for compatibility)
pip install -r requirements.txt

# Optional: Install pyaudio if you need it later
# brew install portaudio
# pip install pyaudio
```

### 5. Install Ollama

```bash
# Download and install Ollama for macOS
# Visit: https://ollama.ai/download
# Or use brew:
brew install ollama

# Pull the hf.co/Christine-HiAiPerf/llama3-8b-qlora-finetuned-Q4_K_M-GGUF:Q4_K_M model
ollama pull hf.co/Christine-HiAiPerf/llama3-8b-qlora-finetuned-Q4_K_M-GGUF:Q4_K_M
```

## Common Issues and Fixes

### Issue 1: PyAudio Build Error

**Error**: `fatal error: 'portaudio.h' file not found`

**Solution**: PyAudio is not needed for our implementation. It's already removed from requirements.txt. We use `sounddevice` instead, which works better on macOS.

### Issue 2: Torch/TorchAudio Installation

**Error**: Large downloads or compatibility issues with torch

**Solution**: PyTorch is optional (only needed for advanced TTS). The basic app works without it.

If you need PyTorch:
```bash
# Install PyTorch for macOS Apple Silicon
pip install torch torchaudio
```

### Issue 3: pyttsx3 Not Working

**Error**: TTS not producing audio or "name 'objc' is not defined"

**Solution**: This was caused by a bug in pyttsx3 version 2.90. Upgrade to 2.99 or later:

```bash
pip install --upgrade pyttsx3
```

The requirements.txt has been updated to use `pyttsx3>=2.99`, which includes the fix.

**Note on pyttsx3 Audio Files on macOS**:
When you select pyttsx3 in the Streamlit UI, the app automatically uses the macOS `say` command to generate audio files for playback. This is because pyttsx3's `save_to_file()` method doesn't work properly on macOS. The `say` command provides high-quality audio output and works perfectly with the Streamlit audio player.

For the best experience on macOS, you can use either:
- **system**: Uses macOS `say` command (fastest, recommended)
- **pyttsx3**: Also uses `say` for file generation on macOS (same quality)

You can select the TTS backend in the Streamlit UI sidebar.

### Issue 4: CosyVoice Dependencies (pynini/WeTextProcessing)

**Error**: `Failed building wheel for pynini` or `No module named 'hyperpyyaml'`

**Solution**: CosyVoice dependencies are **not needed on macOS**. They're only for GPU deployment.

For macOS development:
```bash
# Use system TTS (faster and works great)
export TTS_BACKEND=system

# The warning is harmless - just ignore it
# CosyVoice will work on GPU deployment
```

The error occurs because `pynini` requires OpenFST C++ library, which is difficult to install on macOS M3.

**Recommended**: Use system TTS on macOS, CosyVoice on GPU.

### Issue 5: Whisper Model Download

**Error**: Slow download or timeout when loading Whisper

**Solution**: The first time you run Whisper, it downloads models. This is normal.

Pre-download models:
```bash
python -c "import whisper; whisper.load_model('base')"
```

### Issue 5: Ollama Connection Error

**Error**: "Cannot connect to Ollama"

**Solution**: Start Ollama server in a separate terminal:
```bash
ollama serve
```

Or check if it's already running:
```bash
ps aux | grep ollama
```

### Issue 6: Permission Errors with Microphone

**Error**: "Microphone access denied"

**Solution**: Grant microphone permissions:
1. System Settings → Privacy & Security → Microphone
2. Enable access for Terminal (or your IDE)

## Optimized Installation for macOS M3

Here's a streamlined installation process for macOS M3:

```bash
# Step 1: Install Homebrew dependencies
brew install portaudio espeak ollama

# Step 2: Create conda environment
conda create -n hw9_311 python=3.11 -y
conda activate hw9_311

# Step 3: Install Python packages
pip install -r requirements.txt

# Step 4: Download Whisper model
python -c "import whisper; whisper.load_model('base')"

# Step 5: Pull Llama model
ollama pull hf.co/Christine-HiAiPerf/llama3-8b-qlora-finetuned-Q4_K_M-GGUF:Q4_K_M

# Step 6: Create logs directory
mkdir -p logs

# Step 7: Test the installation
python test_agent.py
```

## Running on macOS M3

### Terminal 1: Start Ollama
```bash
ollama serve
```

### Terminal 2: Run the Agent
```bash
conda activate hw9_311

# Option 1: Quick Start CLI
python quick_start.py

# Option 2: Streamlit Interface (Recommended)
streamlit run frontend.py

# Option 3: Just run the menu
python run.py
```

## Performance Tips for M3

1. **Use the base Whisper model** - Good balance of speed and accuracy on M3
2. **System TTS is fast** - The macOS `say` command is optimized for Apple Silicon
3. **Ollama runs great on M3** - Apple's Neural Engine accelerates inference
4. **Keep Ollama running** - Start it once and leave it running for faster responses

## Verify Installation

Test each component:

```bash
# Test Python environment
python --version  # Should show 3.11.x

# Test Ollama
ollama list  # Should show hf.co/Christine-HiAiPerf/llama3-8b-qlora-finetuned-Q4_K_M-GGUF:Q4_K_M

# Test system TTS
say "Hello from macOS"  # Should speak

# Test Whisper (creates a test)
python -c "import whisper; print('Whisper OK')"

# Run full test suite
python test_agent.py
```

## macOS-Specific Features

The app takes advantage of macOS features:

1. **System TTS**: Uses the built-in `say` command (fast and high-quality)
2. **Neural Engine**: Ollama leverages M3's Neural Engine for faster inference
3. **Native Audio**: sounddevice works well with Core Audio

## Recommended Configuration

For best performance on macOS M3, use these settings in `.env`:

```bash
# Use system TTS (fastest on macOS)
TTS_BACKEND=system

# Whisper base model (good balance)
WHISPER_MODEL=base

# Standard Ollama config
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=hf.co/Christine-HiAiPerf/llama3-8b-qlora-finetuned-Q4_K_M-GGUF:Q4_K_M
```

## Troubleshooting Commands

```bash
# Check conda environment
conda env list

# Check installed packages
pip list | grep -E "whisper|ollama|streamlit|fastapi"

# Check Ollama status
curl http://localhost:11434/api/tags

# Check Python path
which python

# Check if in correct environment
echo $CONDA_DEFAULT_ENV  # Should show hw9_311
```

## Alternative: Using Without Ollama

If you have issues with Ollama, you can use OpenAI's API instead:

1. Get an OpenAI API key
2. Set environment variable: `export OPENAI_API_KEY=your-key`
3. Modify `llm_service.py` to use `AlternativeLLMService`

## Need More Help?

1. Check the main [README.md](README.md)
2. Run the test suite: `python test_agent.py`
3. Check logs: `cat logs/voice_agent_*.log`
4. Verify Ollama: `ollama list`

## Summary

For macOS M3, the key points are:

- ✅ No pyaudio needed (removed from requirements.txt)
- ✅ Use system TTS (built-in, fast)
- ✅ Ollama works great on Apple Silicon
- ✅ Whisper 'base' model is perfect for M3
- ✅ All features fully supported on macOS

Enjoy using the AI Voice Agent on your M3 Mac! 🚀
