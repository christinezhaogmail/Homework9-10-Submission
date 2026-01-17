## 🏗️ System Architecture & Logic Flow

The assistant operates through a **Central Orchestrator** that manages state and hardware resources.

1. **Ingestion:** streamlit captures audio via the browser.
2. **Platform Detection:** The system detects if it’s on a Mac (M3/M4) or a Linux Server (NVIDIA) and loads the appropriate model weights (MPS vs. CUDA).
3. **ASR:** `Faster-Whisper` (Large-v3) transcribes audio, handling accents and noise.
4. **The Brain (LLM):** Processes the text query using a **Conversation Buffer** to understand context (e.g., "Tell me more about the *second* paper").
5. **Tools:** The Brain triggers ArXiv search, summarization, or Notion syncing via function-calling.
6. **Synthesis:** `CosyVoice` performs zero-shot cloning to read the summary back.
7. **UI:** streamlit updates the chat history and provides the Notion deep link.

---

## 🛠️ Phase 1: Environment & Platform Setup

We will use a hardware-agnostic utility to ensure the code runs seamlessly on your M3 Mac during dev and the GPU server during prod.

### 1.1 Hardware Detection Utility

```python
# utils/hardware.py
import torch

def get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"

```

### 1.2 Environment Files

**`env_mac.yml` (Development)**

* Python 3.11
* `faster-whisper` + `ctranslate2` (optimized for ARM)
* `faiss-cpu`

**`env_server.yml` (Production)**

* Python 3.11
* `faster-whisper` + `cuda12`
* `faiss-gpu`
* `cosyvoice` (Full requirements)

---

## 📂 Phase 2: Modular Repository Structure

This Object-Oriented structure ensures that each component can be tested in isolation.

```text
ai-research-assistant/
├── main.py                 # streamlit + FastAPI Entry Point
├── config.py               # API Keys, Model Paths, Platform detection
├── models/
│   ├── asr.py              # Class VoiceTranscriber (Faster-Whisper)
│   ├── tts.py              # Class VoiceSynthesizer (CosyVoice)
│   └── brain.py            # Class ResearchOrchestrator (LLM + Memory)
├── tools/
│   ├── search.py           # Class AcademicSearch (ArXiv + Multi-source)
│   ├── summarize.py        # Class ContentSummarizer (HF Pipeline)
│   └── notion.py           # Class NotionSync (Notion API)
├── utils/
│   ├── logger.py           # Tool-call wrapping & logging
│   └── hardware.py         # Device detection
├── README.md
└── requirements/           # conda yml files

```

---

## 🚀 Phase 3: Implementation Detail

### Step 1: The Multi-Source Search (OOP)

This module allows for future expansion (e.g., adding PubMed or Semantic Scholar).

```python
class AcademicSearch:
    def __init__(self, device):
        self.device = device
        # Initialize Vector Store (FAISS)
        
    def search_arxiv(self, query: str, top_k=3):
        """Semantic search over ArXiv abstracts."""
        # Logic: ArXiv API -> Embedding -> Vector Search
        return excerpts

    def multi_search(self, query: str):
        """Orchestrate search across multiple academic sources."""
        results = self.search_arxiv(query)
        # Add future sources here
        return results

```

### Step 2: Long-Conversation Memory

We use a `HistoryBuffer` to store the last  turns of conversation, which is passed to the LLM during function-calling to resolve pronouns (like "it" or "that paper").

### Step 3: streamlit Interface

The streamlit UI will include:

* **Audio Input:** A "Record from Mic" component.
* **Chatbot:** Displaying the "Research Thread."
* **Notion Link:** A markdown component displaying the link to the synced Notion page.

---

## 🧪 Phase 4: Testing & Integration

1. **Unit Testing:** Each class in `models/` and `tools/` will have a `if __name__ == "__main__":` block to allow testing the component without launching the whole API.
2. **Noise/Accent Test:** Using `Faster-Whisper`'s `beam_size=5` and `initial_prompt` to improve transcription of technical jargon.
3. **FastAPI Endpoints:**
* `POST /ask`: Wraps the orchestrator.
* `POST /notion-sync`: Calls the `NotionSync` singleton.



---

## 📝 Phase 5: Documentation (README.md)

Your README will include:

1. **Installation:** Step-by-step Conda setup for both Mac and Server.
2. **Configuration:** How to add the Notion `secret_token` and `database_id`.
3. **Voice Cloning:** Where to place the `reference.wav` for CosyVoice zero-shot cloning.
4. **Usage:** How to launch the streamlit UI vs. the FastAPI backend.

---
