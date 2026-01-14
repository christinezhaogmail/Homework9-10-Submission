# Quick Start Guide

Get the AI Voice Agent running in 5 minutes!

## Prerequisites

1. **Conda** installed
2. **Ollama** installed ([download here](https://ollama.ai/download))

**macOS M3 Users**: Having installation issues? See [MACOS_SETUP.md](MACOS_SETUP.md) for detailed instructions.

## Setup (One-Time)

```bash
# 1. Run the setup script
bash setup.sh

# Or manually:
conda create -n hw6_310 python=3.10 -y
conda activate hw6_310
pip install -r requirements.txt
ollama pull my-lama3-finetuned-Q4_K_M
```

## Running the Agent

### Terminal 1: Start Ollama
```bash
ollama serve
```

### Terminal 2: Run the Agent

**Option A: Quick Start CLI (Simplest)**
```bash
conda activate hw6_310
python quick_start.py
```

**Option B: Streamlit Web Interface (Best)**
```bash
conda activate hw6_310
streamlit run frontend.py
```

**Option C: Easy Launcher**
```bash
conda activate hw6_310
python run.py
# Then choose your option
```

## Test It

```bash
conda activate hw6_310
python test_agent.py
```

## Example Queries

Try these in the interface:

1. **Math**: "What is 25 multiplied by 4?"
2. **Research**: "What is quantum entanglement?"
3. **Chat**: "Hello, how are you?"

## Troubleshooting

**Error: "Cannot connect to Ollama"**
- Start Ollama: `ollama serve`

**Error: "Module not found"**
- Activate environment: `conda activate hw6_310`
- Install dependencies: `pip install -r requirements.txt`

**Error: "Model not found"**
- Pull model: `ollama pull my-lama3-finetuned-Q4_K_M`

## Next Steps

- Read [README.md](README.md) for full documentation
- Read [DEMO_GUIDE.md](DEMO_GUIDE.md) for video demo instructions
- Check logs in `logs/` directory

## Need Help?

1. Run the test suite: `python test_agent.py`
2. Check the logs: `ls logs/`
3. Read the full README.md

That's it! You're ready to use the AI Voice Agent! 🎉
