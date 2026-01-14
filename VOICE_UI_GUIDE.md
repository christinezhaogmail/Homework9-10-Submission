# Voice UI Guide - Streamlit Audio Integration

Complete guide for using the voice-enabled Streamlit interface with audio input and output.

## 🎙️ Features

The Streamlit frontend now includes full voice interaction capabilities:

### Audio Input (`st.audio_input`)
- **Record voice queries** directly in the browser
- **Automatic transcription** using Whisper
- **Real-time display** of transcribed text

### Audio Output (`st.audio`)
- **Generated audio responses** using TTS
- **Playback controls** for all responses
- **Persistent audio** in conversation history
- **Multiple TTS backends**: system, pyttsx3, CosyVoice

## 🚀 Quick Start

### 1. Start Ollama

```bash
# Terminal 1
ollama serve
```

### 2. Run Streamlit

```bash
# Terminal 2
conda activate hw9_311
streamlit run frontend.py
```

### 3. Enable Voice Mode

1. Open http://localhost:8501
2. In the sidebar, check **"Enable Voice Mode"**
3. Choose your TTS backend (system is fastest on macOS)

## 🎯 How to Use

### Voice Input

1. **Click the microphone button** "🎤 Record your question"
2. **Speak your question** (browser will record)
3. **Click Stop** when done
4. Wait for **automatic transcription**
5. See transcribed text appear
6. Response will be generated automatically

### Voice Output

When you receive a response:
- **Text appears** in the chat
- **Audio player appears** below the text
- **Click play** to hear the response
- **Audio is saved** - you can replay it anytime

### Text Input (Still Available)

You can still type questions in the chat input box at the bottom.

## ⚙️ Configuration

### Voice Settings (Sidebar)

**Enable Voice Mode**
- Toggle audio input/output on/off
- Unchecked: Text-only mode
- Checked: Full voice interaction

**TTS Backend** (when voice enabled)
- `system`: macOS 'say' command (fastest, good quality)
- `pyttsx3`: Cross-platform (medium speed, good quality)
- `cosyvoice`: Neural TTS (slower, highest quality, GPU recommended)

### Mode Selection

**Use API Mode**
- Unchecked: Direct local processing (required for voice)
- Checked: Use FastAPI backend (voice features disabled in API mode)

## 🎨 User Interface

### Main Screen

```
🤖 AI Voice Agent
──────────────────────────────────────
🎙️ Voice Mode: Enabled - Audio input and output active

Ask me anything! I can search scientific papers and perform calculations.

💬 Conversation
──────────────────────────────────────
[Previous messages with audio players]

🎤 Voice Input
──────────────────────────────────────
[🎤 Record your question button]
[Transcription appears here]

──────────────────────────────────────
💭 Type your message here...
```

### Sidebar

```
⚙️ Configuration
──────────────────
☐ Use API Mode
☑ Using local services

🎙️ Voice Settings
──────────────────
☑ Enable Voice Mode
TTS Backend: [system ▼]

📊 Statistics
──────────────────
Total Queries: 5
Conversation Length: 10
```

## 💡 Usage Examples

### Example 1: Math Query with Voice

1. Click "🎤 Record your question"
2. Say: "What is 25 multiplied by 4?"
3. Wait for transcription: "What is 25 multiplied by 4?"
4. See response: "The result is: 100"
5. Audio player appears - click play to hear: "The result is: 100"

### Example 2: arXiv Search with Voice

1. Click "🎤 Record your question"
2. Say: "What is quantum entanglement?"
3. Wait for transcription
4. See response with paper summaries
5. Audio player reads the summary

### Example 3: Mixed Input

1. Use voice for first question
2. Type follow-up question in chat
3. Both work seamlessly
4. All responses have audio if voice mode is on

## 🔊 Audio Playback Features

### In Conversation History

Each assistant message shows:
- **Text response**
- **🔊 Audio player** (if voice mode was enabled)
- **📋 Details** expander (function calls, processing time)
- **🔍 Raw LLM Output** expander (JSON)

### Audio Controls

Standard HTML5 audio controls:
- ▶️ Play/Pause
- 🔈 Volume control
- ⏩ Seek bar
- ⬇️ Download option

## 🛠️ Technical Details

### Audio Input Pipeline

```
Browser Microphone
    ↓ (st.audio_input)
Audio Bytes
    ↓ (save to temp file)
Whisper STT
    ↓ (transcription)
Text Query
    ↓
LLM Processing
```

### Audio Output Pipeline

```
LLM Response Text
    ↓
TTS Service
    ↓ (generate_audio_response)
WAV File
    ↓ (st.audio)
Browser Audio Player
```

### File Management

- **Temporary files**: Audio stored in `/tmp/` (automatically managed)
- **Conversation history**: Audio paths stored in session state
- **Cleanup**: Temporary files persist during session

## ⚡ Performance

### Audio Input
- **Recording**: Instant (browser-based)
- **Transcription**: 1-2 seconds (Whisper base model)
- **Total**: ~2 seconds from recording to text

### Audio Output
- **System TTS**: < 1 second (fastest)
- **pyttsx3**: 1-2 seconds
- **CosyVoice**: 3-5 seconds CPU, 1-2 seconds GPU

### Recommendations

**For Development (macOS)**:
- Use `system` TTS backend
- Whisper `base` model
- Fast iteration, good quality

**For Production (GPU)**:
- Use `cosyvoice` TTS backend
- Whisper `base` or `small` model
- Best quality, reasonable speed

## 🐛 Troubleshooting

### Issue: Microphone not working

**Solution**:
1. Check browser permissions (camera/microphone)
2. Chrome: chrome://settings/content/microphone
3. Allow access for localhost:8501
4. Restart browser if needed

### Issue: Audio not playing

**Solution**:
1. Check browser audio permissions
2. Verify TTS backend is initialized
3. Check logs for errors
4. Try different TTS backend

### Issue: Transcription fails

**Solution**:
1. Check Whisper is installed: `pip install openai-whisper`
2. Verify audio format (should be WAV)
3. Check logs: `logs/voice_agent_*.log`
4. Try speaking more clearly

### Issue: "Voice Mode disabled in API mode"

**Solution**:
- Voice features only work with local services
- Uncheck "Use API Mode" in sidebar
- Use direct local processing

### Issue: CosyVoice not available

**Solution**:
1. Check CosyVoice installation
2. Set correct paths in `.env`:
   ```bash
   COSYVOICE_PATH=/path/to/CosyVoice
   COSYVOICE_MODEL_DIR=/path/to/model
   ```
3. Install dependencies: `pip install hyperpyyaml WeTextProcessing`
4. Fall back to `system` or `pyttsx3`

## 📊 Comparison: Voice vs Text Mode

| Feature | Text Mode | Voice Mode |
|---------|-----------|------------|
| Input Method | Keyboard | Microphone + Keyboard |
| Output Format | Text only | Text + Audio |
| Speed | Fast | Moderate (+ transcription/TTS time) |
| Accessibility | Standard | Enhanced |
| Bandwidth | Low | Higher |
| Use Case | Quick queries | Immersive interaction |

## 🎯 Best Practices

### For Users

1. **Speak clearly** when recording
2. **Use quiet environment** for better transcription
3. **Verify transcription** before submitting
4. **Adjust volume** on audio players as needed
5. **Switch to text** for complex/technical input

### For Developers

1. **Handle audio errors gracefully**
2. **Provide fallback to text input**
3. **Clean up temporary files**
4. **Monitor audio file sizes**
5. **Test on different browsers**

## 🔮 Future Enhancements

Potential improvements:

- [ ] Real-time audio streaming
- [ ] Voice activity detection
- [ ] Multiple language support
- [ ] Custom voice selection
- [ ] Audio quality settings
- [ ] Batch audio export
- [ ] Audio effects/filters
- [ ] Speaker diarization

## 📖 Related Documentation

- [README.md](README.md) - Main documentation
- [COSYVOICE_INTEGRATION.md](COSYVOICE_INTEGRATION.md) - CosyVoice setup
- [MACOS_SETUP.md](MACOS_SETUP.md) - macOS-specific setup
- [GPU_DEPLOYMENT.md](GPU_DEPLOYMENT.md) - GPU deployment

## 🎉 Summary

The Streamlit frontend now provides:

✅ **Full voice input** via `st.audio_input()`
✅ **Automatic transcription** with Whisper
✅ **Audio output playback** via `st.audio()`
✅ **Multiple TTS backends** (system/pyttsx3/CosyVoice)
✅ **Seamless text/voice mixing**
✅ **Persistent audio history**
✅ **Real-time feedback**
✅ **Easy configuration**

Enjoy your voice-enabled AI agent! 🎙️🤖
