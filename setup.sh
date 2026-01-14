#!/bin/bash

echo "=========================================="
echo "AI Voice Agent - Setup Script"
echo "=========================================="
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install conda first."
    echo "   Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ Conda found"

# Check if environment exists
ENV_NAME="hw9_311"
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "⚠️  Environment ${ENV_NAME} already exists"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing environment..."
        conda env remove -n ${ENV_NAME} -y
    else
        echo "Using existing environment"
        conda activate ${ENV_NAME}
    fi
else
    echo "Creating conda environment: ${ENV_NAME}"
    conda create -n ${ENV_NAME} python=3.11 -y
fi

echo ""
echo "Activating environment..."
eval "$(conda shell.bash hook)"
conda activate ${ENV_NAME}

echo ""
echo "Installing Python dependencies..."

# Check if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS - checking for Homebrew dependencies..."

    # Check if brew is installed
    if command -v brew &> /dev/null; then
        echo "Installing portaudio for audio processing..."
        brew install portaudio 2>/dev/null || echo "portaudio may already be installed"
    else
        echo "⚠️  Homebrew not found. Some features may not work."
        echo "   Install Homebrew from: https://brew.sh"
    fi
fi

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Some packages failed to install."
    echo "   This is usually okay - the core functionality should still work."
    echo "   See MACOS_SETUP.md for troubleshooting."
    echo ""
fi

echo ""
echo "Downloading Whisper model..."
python -c "import whisper; whisper.load_model('base')"

echo ""
echo "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed"
    echo "   Please install Ollama from: https://ollama.ai/download"
    echo "   Then run: ollama pull llama3.2"
else
    echo "✅ Ollama found"
    echo ""
    echo "Checking for llama3.2 model..."
    if ollama list | grep -q "llama3.2"; then
        echo "✅ llama3.2 model found"
    else
        echo "⚠️  llama3.2 model not found"
        echo "Downloading llama3.2 model..."
        ollama pull llama3.2
    fi
fi

echo ""
echo "Creating necessary directories..."
mkdir -p logs

echo ""
echo "Creating .env file from template..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "⚠️  .env file already exists, skipping"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the environment: conda activate ${ENV_NAME}"
echo "2. Start Ollama (in a separate terminal): ollama serve"
echo "3. Run the test suite: python test_agent.py"
echo "4. Start the quick CLI: python quick_start.py"
echo "5. Or start the web interface: streamlit run frontend.py"
echo ""
echo "For more information, see README.md"
echo ""
