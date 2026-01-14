# GPU Deployment Guide (NVIDIA)

Guide for deploying the AI Voice Agent on NVIDIA GPU servers with CosyVoice support.

## Overview

This guide covers deploying the voice agent from macOS development environment to an NVIDIA GPU server for production use with high-quality CosyVoice TTS.

## Prerequisites

- NVIDIA GPU with CUDA support (Tesla, RTX, or A series)
- CUDA Toolkit 11.8 or 12.1
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.11
- Docker (optional but recommended)

## GPU Server Setup

### 1. Install NVIDIA Drivers and CUDA

```bash
# Check GPU
nvidia-smi

# Install CUDA Toolkit (if not installed)
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run

# Verify CUDA
nvcc --version
```

### 2. Install Python and Dependencies

```bash
# Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install PyTorch with CUDA Support

```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify PyTorch GPU support
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

### 4. Install CosyVoice

```bash
# Clone CosyVoice repository
cd ~/
sudo git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice

# Install CosyVoice dependencies
pip install -r requirements.txt

# Download pretrained models
# Follow CosyVoice documentation to download models
# Place models in: ~/CosyVoice/pretrained_models/CosyVoice-300M-SFT
```

### 5. Install Voice Agent

```bash
# Clone your project
cd ~/
sudo git clone <your-repo-url> ai-voice-agent
cd ai-voice-agent

# Install dependencies
pip install -r requirements.txt

# Install Ollama for Linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama model
ollama pull my-lama3-finetuned-Q4_K_M
```

## Configuration for GPU

### 1. Update Environment Variables

Create `~/ai-voice-agent/.env`:

```bash
# LLM Settings
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=my-lama3-finetuned-Q4_K_M
LLM_TEMPERATURE=0.7

# Whisper Settings
WHISPER_MODEL=base

# TTS Settings - Use CosyVoice on GPU
TTS_BACKEND=cosyvoice

# CosyVoice Settings
COSYVOICE_PATH=~/CosyVoice
COSYVOICE_MODEL_DIR=~/CosyVoice/pretrained_models/CosyVoice-300M-SFT

# FastAPI Settings
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_ROTATION=1 day
LOG_RETENTION=7 days
```

### 2. Test GPU Setup

```bash
# Test PyTorch GPU
python -c "import torch; print(torch.cuda.is_available())"

# Test CosyVoice
cd ~/CosyVoice
python test_cosyvoice.py  # If available

# Test Voice Agent
cd ~/ai-voice-agent
python test_agent.py
```

## Running on GPU

### Option 1: Direct Python

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start FastAPI backend
cd ~/ai-voice-agent
source venv/bin/activate
python backend.py
```

### Option 2: Using Systemd Services

Create `/etc/systemd/system/ollama.service`:

```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/voice-agent.service`:

```ini
[Unit]
Description=AI Voice Agent API
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=~/ai-voice-agent
Environment="PATH=~/ai-voice-agent/venv/bin"
Environment="COSYVOICE_PATH=~/CosyVoice"
ExecStart=~/ai-voice-agent/venv/bin/python backend.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ollama voice-agent
sudo systemctl start ollama voice-agent

# Check status
sudo systemctl status ollama
sudo systemctl status voice-agent
```

### Option 3: Using Docker

Create `Dockerfile`:

```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Install CosyVoice
RUN git clone https://github.com/FunAudioLLM/CosyVoice.git ~/CosyVoice
WORKDIR ~/CosyVoice
RUN pip install -r requirements.txt

# Install Voice Agent
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start services
CMD ["bash", "-c", "ollama serve & sleep 5 && ollama pull my-lama3-finetuned-Q4_K_M && python backend.py"]
```

Build and run:

```bash
# Build Docker image
docker build -t voice-agent-gpu .

# Run with GPU support
docker run --gpus all -p 8000:8000 \
  -v ~/CosyVoice/pretrained_models:~/CosyVoice/pretrained_models \
  -e TTS_BACKEND=cosyvoice \
  voice-agent-gpu
```

## Performance Optimization

### 1. GPU Memory Management

For CosyVoice on GPU, you can optimize memory usage:

```python
# In audio_service.py, you can add:
# Set PyTorch memory allocator
import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
```

### 2. Batch Processing

For multiple requests, consider batching:

```python
# In your application code
# Process multiple TTS requests in batches for efficiency
```

### 3. Model Quantization

For faster inference:

```python
# Use torch.quantization for INT8 inference
# This can speed up inference on GPU
```

## Monitoring

### 1. GPU Monitoring

```bash
# Monitor GPU usage
watch -n 1 nvidia-smi

# Log GPU metrics
nvidia-smi --query-gpu=timestamp,name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.free --format=csv -l 1 > gpu_metrics.log
```

### 2. Application Monitoring

```bash
# Check logs
tail -f logs/voice_agent_*.log

# Check API health
curl http://localhost:8000/health

# Monitor with htop
htop
```

## Benchmarking

Test performance on GPU:

```bash
# Test script
python << EOF
import time
import requests

# Warm up
for i in range(3):
    requests.post("http://localhost:8000/api/voice-query/", json={"text": "test"})

# Benchmark
start = time.time()
for i in range(100):
    requests.post("http://localhost:8000/api/voice-query/", json={"text": "What is quantum entanglement?"})
end = time.time()

print(f"Average time per request: {(end-start)/100:.2f}s")
EOF
```

Expected performance with GPU:
- **Whisper (base)**: ~0.2-0.5s per audio
- **LLM (my-lama3-finetuned-Q4_K_M)**: ~0.5-1.5s per query
- **CosyVoice**: ~1-3s per response (much better quality than system TTS)
- **Total**: ~2-5s end-to-end

## Troubleshooting

### Issue: CUDA Out of Memory

```bash
# Reduce batch size or use smaller Whisper model
export WHISPER_MODEL=tiny

# Or use CPU for Whisper, GPU for CosyVoice
```

### Issue: CosyVoice Not Loading

```bash
# Check model path
ls -la $COSYVOICE_MODEL_DIR

# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Check logs
tail -f logs/voice_agent_*.log
```

### Issue: Ollama Connection Error

```bash
# Check Ollama status
systemctl status ollama

# Restart Ollama
sudo systemctl restart ollama

# Check Ollama logs
journalctl -u ollama -f
```

## Security Considerations

1. **Firewall**: Only expose necessary ports
2. **HTTPS**: Use nginx reverse proxy with SSL
3. **Authentication**: Add API authentication
4. **Rate Limiting**: Prevent abuse

Example nginx config:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Cost Optimization

For cloud GPU instances:

1. **Auto-scaling**: Scale down during low usage
2. **Spot Instances**: Use for non-critical workloads
3. **Model Caching**: Cache frequently used model outputs
4. **Multi-tenancy**: Share GPU across multiple services

## Deployment Checklist

- [ ] NVIDIA drivers installed and working
- [ ] CUDA toolkit installed
- [ ] PyTorch with GPU support verified
- [ ] CosyVoice installed and tested
- [ ] Ollama running with my-lama3-finetuned-Q4_K_M
- [ ] Voice Agent dependencies installed
- [ ] Environment variables configured
- [ ] Services configured (systemd or docker)
- [ ] Firewall configured
- [ ] SSL certificates (if production)
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Load testing completed

## Scaling

For production scale:

1. **Load Balancer**: Use nginx or HAProxy
2. **Multiple Workers**: Run multiple FastAPI workers
3. **Queue System**: Use Celery + Redis for async processing
4. **Multi-GPU**: Distribute across multiple GPUs

## Support

- GPU issues: Check NVIDIA documentation
- CosyVoice: https://github.com/FunAudioLLM/CosyVoice
- Ollama: https://ollama.ai/docs
- Voice Agent: See main [README.md](README.md)

## Summary

With GPU deployment:
- ✅ 5-10x faster inference
- ✅ High-quality CosyVoice TTS
- ✅ Handle more concurrent users
- ✅ Better audio quality
- ✅ Production-ready scalability

Enjoy your GPU-powered AI Voice Agent! 🚀
