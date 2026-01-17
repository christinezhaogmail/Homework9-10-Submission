## AI Research Assistant


Function:
1. Input: accept live audio query from any computer, for example, mac, linux, or windows.
2. Search academic content
3. Summarize findings
4. Save the results
5. Support follow-up questions and context


# Tech stack:

1. Integrating Whisper with CosyVoice creates a powerful "Zero-Shot" voice cloning pipeline.
2. Leverage Vector (e.g., a semantic search over ArXiv papers) to fetch relevant passages. Function search_arxiv(query) returns top-3 relevant documents or excerpts.
3. Use function-calling to orchestrate tools. E.g., LLM’s output can go to search_arxiv, summarize, sync_to_notion.
4. Wrap each tool call with logging.
5. Use HiggingFace summarization pipeline to condense retrieved content.
6. Save conversation and summary to Notion’s database. Function sync_to_notion(session_id, content)

# Sample functions:
```python
def search_arxiv(query: str) -> List[str]:
      """Return relevant document passages for the query."""
      ...

def summarize(texts: List[str]) -> str:
      """Return a concise summary of the given passages."""
      ...

def sync_to_notion(session_id: str, content: str):
      """Append the session content and summary to Notion."""
      ...
```

1. LLM Invocation and Logging: wrap LLM calls so that you can see inputs/outputs.
2. HTTP API endpoints (FastAPI)
3. POST /ask: accept a voice alive or text. Run pipeline and return the answer (audio or text). Process request, call whisper, LLM, summarizer, TTS in order, and return final response. Log activities.
4. POST /notion-sync: manually triggers syncing the current conversation to Notion (or done at session end). Log activities.
5. GET /status: returns the current session ID or a health check status. Log activities.


# Libraries:

Fastapi, uvicorn, whisper, transformers, cosyvoice.

# Need to install ASR/TTS engines

1. Run on server: GPU.
2. Develop on MacOs M3 or M4.
3. Create two separate environment or requirement files.
4. Python version is 3.10
5. Use conda to handle  
