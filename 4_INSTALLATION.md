# Installation Guide

This guide covers installation for both **macOS M3/M4 (Development)** and **Linux GPU Server (Production)**.

---

## 🍎 macOS M3/M4 Installation (Development)

### Prerequisites
- macOS with Apple Silicon (M3 or M4)
- Homebrew installed
- Conda/Miniconda installed

### Step 1: Clone Repository

```bash
git clone https://github.com/christinezhaogmail/ai-research-assistant.git
cd ai-research-assistant
```

### Step 2: Create Conda Environment

```bash
# Create environment from yml file
conda env create -f requirements/env_mac.yml

# Activate environment
conda activate ai-research-assistant-mac
```

### Step 3: Install Ollama (for LLM)

```bash
# Install Ollama
brew install ollama

# Start Ollama service
ollama serve &

# Pull Llama 3.2 model
ollama pull llama3.2
```

### Step 4: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env
```

Set the following variables:
```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2

# ASR/TTS Configuration
WHISPER_MODEL=base
TTS_BACKEND=system  # Use macOS 'say' command

# Notion Integration (optional)
# NOTION_TOKEN=your_token_here
# NOTION_DATABASE_ID=your_database_id_here

# ArXiv
ARXIV_MAX_RESULTS=3
```

### Step 5: Verify Installation

```bash
# Test hardware detection
python test/test_hardware.py

# Run all tests
python test/test_all.py
```

### Step 6: Start the Application

```bash
# Terminal 1: Start FastAPI backend
python backend.py

# Terminal 2: Start Streamlit frontend
streamlit run frontend.py
```

The application will be available at:
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:8501
- API Docs: http://localhost:8000/docs

---

## 🖥️ Linux GPU Server Installation (Production)

### Prerequisites
- Linux server with NVIDIA GPU
- CUDA 12.1+ installed
- Conda/Miniconda installed

### Step 1: Clone Repository

```bash
git clone https://github.com/christinezhaogmail/ai-research-assistant.git
cd ai-research-assistant
```

### Step 2: Create Conda Environment

```bash
# Create environment from yml file
conda env create -f requirements/env_server.yml

# Activate environment
conda activate ai-research-assistant-gpu
```

### Step 3: Verify CUDA Installation

```bash
# Check CUDA version
nvcc --version

# Verify PyTorch can see GPU
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0)}')"
```

### Step 4: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Pull Llama 3.2 model
ollama pull llama3.2
```

### Step 5: Install CosyVoice (Optional, for advanced TTS)

```bash
# Clone CosyVoice repository
cd /opt  # or your preferred location
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice

# Install CosyVoice dependencies
pip install -r requirements.txt

# Download pretrained models (follow CosyVoice README)
```

### Step 6: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env
```

Set the following variables:
```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2

# ASR/TTS Configuration
WHISPER_MODEL=large-v3  # Use larger model on GPU
TTS_BACKEND=cosyvoice  # or "system" or "pyttsx3"
COSYVOICE_PATH=/opt/CosyVoice
COSYVOICE_MODEL_DIR=/opt/CosyVoice/pretrained_models/CosyVoice-300M-SFT

# Notion Integration (optional)
# NOTION_TOKEN=your_token_here
# NOTION_DATABASE_ID=your_database_id_here

# ArXiv
ARXIV_MAX_RESULTS=3
```

### Step 7: Verify Installation

```bash
# Test hardware detection (should show CUDA)
python test/test_hardware.py

# Run all tests
python test/test_all.py
```

### Step 8: Start the Application

#### Option A: Development Mode

```bash
# Terminal 1: Start FastAPI backend
python backend.py

# Terminal 2: Start Streamlit frontend
streamlit run frontend.py
```

#### Option B: Production Mode with systemd

Create service file `/etc/systemd/system/ai-research-assistant.service`:

```ini
[Unit]
Description=AI Research Assistant API
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/jovyan/ai-research-assistant
Environment="PATH=/home/your_username/miniconda3/envs/ai-research-assistant-gpu/bin"
ExecStart=/home/your_username/miniconda3/envs/ai-research-assistant-gpu/bin/python backend.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-research-assistant
sudo systemctl start ai-research-assistant
sudo systemctl status ai-research-assistant
```

---

## 🔧 Troubleshooting

### macOS Issues

#### Issue: "ImportError: cannot import name 'CosyVoice'"
**Solution**: This is expected on macOS. Use `TTS_BACKEND=system` in .env

#### Issue: Whisper model download fails
**Solution**:
```bash
# Set cache directory
export HF_HOME=~/.cache/huggingface
python -c "import whisper; whisper.load_model('base')"
```

#### Issue: "Module 'streamlit' has no attribute 'audio_input'"
**Solution**: Upgrade Streamlit
```bash
pip install --upgrade streamlit
# Ensure version >= 1.31.0
```

### Linux GPU Server Issues

#### Issue: PyTorch not detecting GPU
**Solution**:
```bash
# Reinstall PyTorch with CUDA support
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

#### Issue: CosyVoice installation fails
**Solution**:
```bash
# Use system TTS as fallback
echo "TTS_BACKEND=system" >> .env
```

#### Issue: Out of memory errors
**Solution**: Use smaller models
```bash
# In .env
WHISPER_MODEL=base  # instead of large-v3
```

### General Issues

#### Issue: Notion sync not working
**Solution**: Verify credentials
```bash
# Test Notion connection
python test/test_notion.py
```

#### Issue: ArXiv search fails
**Solution**: Check internet connection
```bash
# Test ArXiv API
python test/test_search.py
```

---

## 📦 Alternative Installation (pip only)

If you prefer not to use conda:

```bash
# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔄 Updating

To update the application:

```bash
# Pull latest code
git pull origin main

# Update conda environment
conda env update -f requirements/env_mac.yml  # or requirements/env_server.yml

# Restart services
```

---

## 🗑️ Uninstallation

```bash
# Remove conda environment
conda deactivate
conda env remove -n ai-research-assistant-mac

# Remove cloned repository
rm -rf /home/jovyan/ai-research-assistant

# (Optional) Remove Ollama
brew uninstall ollama  # macOS
# or
sudo rm /usr/local/bin/ollama  # Linux
```

---

## 📚 Next Steps

After installation:
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
2. Review [test/README.md](test/README.md) for testing guidelines
3. Check [README.md](README.md) for usage instructions
4. Set up Notion integration (optional)

---

## 🆘 Getting Help

If you encounter issues:
1. Check this troubleshooting guide
2. Review logs in `logs/` directory
3. Run diagnostic tests: `python test/test_all.py`
4. Open an issue on GitHub with:
   - Error message
   - System info (OS, Python version, GPU)
   - Steps to reproduce
