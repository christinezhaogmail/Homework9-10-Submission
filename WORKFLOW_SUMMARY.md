# Auto-Save Workflow Summary

## Overview
The system has been improved to automatically summarize and save research sessions to Notion after every arXiv query.

## Key Changes

### 1. agent_tools.py
- **Removed:** `calculate` function (no longer needed)
- **Added:** `summarize_and_save` function that:
  - Accepts session content, arXiv papers, and query count
  - Generates a summary of the research session
  - Saves everything to Notion database automatically
  - Returns the Notion page URL for easy access

### 2. llm_service.py
- **Updated system prompt** to focus on arXiv research assistance
- **Removed** all references to the `calculate` function
- **Added** guidance about automatic Notion saving after 3 queries
- **Improved** examples to focus on research-oriented queries

### 3. function_router.py
- **Added session tracking:**
  - `arxiv_query_count`: Tracks number of arXiv searches
  - `arxiv_results`: Stores all arXiv search results
  - `session_content`: Stores query metadata

- **New workflow methods:**
  - `should_trigger_auto_save()`: Checks if threshold is reached
  - `trigger_auto_save()`: Automatically calls summarize_and_save
  - `reset_session()`: Resets tracking after save

- **Enhanced routing:**
  - Automatically triggers summarization after 3 arXiv queries
  - Appends auto-save result to the response
  - Returns auto-save status in the result dictionary

### 4. config.py
- **Added Notion configuration:**
  - `NOTION_TOKEN`: Environment variable for Notion API token
  - `NOTION_DATABASE_ID`: Environment variable for target database
  - `AUTO_SAVE_THRESHOLD`: Configurable threshold (default: 3)

- **Updated config dict** to include:
  - `arxiv_max_results`
  - `auto_save_threshold`
  - `notion_configured`: Boolean indicating if Notion is set up

## Workflow Behavior

**Every arXiv query automatically triggers:**
1. System searches arXiv and returns results
2. System automatically:
   - Summarizes the query and results
   - Saves to Notion database
   - Returns Notion page URL
   - Resets counter

**Configurable threshold:** Set `AUTO_SAVE_THRESHOLD` environment variable to save after N queries instead (default: 1)

## Configuration

Set these environment variables:

```bash
export NOTION_TOKEN="your_notion_integration_token"
export NOTION_DATABASE_ID="your_database_id"
export AUTO_SAVE_THRESHOLD=1  # Optional, defaults to 1 (save after every query)
export ARXIV_MAX_RESULTS=3     # Optional, defaults to 3
```

## Testing

Run the test suites to verify functionality:

```bash
# Test agent tools (including summarize_and_save)
python agent_tools.py

# Test function router (demonstrates auto-save workflow)
python function_router.py

# Test LLM service (updated prompts)
python llm_service.py

# Test Notion integration
python tools/notion.py
```

## Architecture Benefits

1. **Automatic Documentation:** Research sessions are saved without manual intervention
2. **Configurable:** Threshold and settings can be adjusted via environment variables
3. **Modular:** Clean separation between routing, tools, and LLM service
4. **Trackable:** Full session history preserved in Notion
5. **User-Friendly:** Provides confirmation and Notion URL after saving

## Example Usage

```python
from function_router import FunctionRouter

router = FunctionRouter()

# Every query automatically triggers auto-save!
result = router.route_llm_output('{"function": "search_arxiv", "arguments": {"query": "quantum computing", "limit": 3}}')
# result['auto_save_triggered'] == True
# result['auto_save_result'] contains Notion URL
# Session counter resets to 0

# Next query
result2 = router.route_llm_output('{"function": "search_arxiv", "arguments": {"query": "machine learning", "limit": 3}}')
# result2['auto_save_triggered'] == True
# Each query creates a new Notion page

# To save after N queries instead, set AUTO_SAVE_THRESHOLD=3 in environment
# Then it will save after every 3 queries
```

## Future Enhancements

Possible improvements:
- Add manual save command for users
- Allow customizing summary format
- Support multiple Notion databases
- Add session naming/tagging
- Include timestamps in summaries
- Export to other formats (PDF, Markdown)
