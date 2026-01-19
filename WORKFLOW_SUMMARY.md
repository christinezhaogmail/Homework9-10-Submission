# Auto-Save Workflow Summary

## Overview
The system automatically summarizes and saves research sessions to Notion after each arXiv query.
- **Each query returns 3 papers** (configurable via ARXIV_MAX_RESULTS)
- **Summary includes all paper titles and arXiv URLs**
- **Saves to Notion immediately after each query**

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

**Single Query Workflow (1 query → 3 papers → Auto-save):**

1. **User makes 1 arXiv query** (e.g., "What is quantum computing?")
2. **System searches and returns 3 papers** with:
   - Paper titles
   - Authors
   - Publication dates
   - Summaries
   - arXiv URLs
3. **System automatically summarizes and saves to Notion**:
   - Extracts all 3 paper titles
   - Extracts all 3 arXiv URLs
   - Creates summary with titles and clickable links
   - Saves to Notion database
   - Returns Notion page URL

**Example:**
- Query: "machine learning in healthcare"
- Results: 3 papers with titles and URLs
- Auto-save: Notion page with summary listing all 3 papers and their arXiv links

**Configurable:** Set `AUTO_SAVE_THRESHOLD` environment variable to change behavior (default: 1)

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

# Query 1: Search for quantum computing papers
result = router.route_llm_output('{"function": "search_arxiv", "arguments": {"query": "quantum computing", "limit": 3}}')
# Returns 3 papers
# result['auto_save_triggered'] == True
# result['auto_save_result'] contains:
#   - Summary with 3 paper titles
#   - All 3 arXiv URLs
#   - Notion page URL

# Query 2: Search for machine learning papers (creates new Notion page)
result2 = router.route_llm_output('{"function": "search_arxiv", "arguments": {"query": "machine learning", "limit": 3}}')
# Returns 3 different papers
# result2['auto_save_triggered'] == True
# Creates a separate Notion page with these 3 papers

# Example Notion Summary Format:
# Research Session Summary (1 arXiv queries)
#
# Queries:
#   • Query 1: quantum computing
#
# Papers Found (3 papers):
#
# 1. Quantum Computing: A Gentle Introduction
#    Link: https://arxiv.org/abs/1234.5678
#
# 2. Advances in Quantum Algorithms
#    Link: https://arxiv.org/abs/2345.6789
#
# 3. Quantum Error Correction Methods
#    Link: https://arxiv.org/abs/3456.7890
```

## Future Enhancements

Possible improvements:
- Add manual save command for users
- Allow customizing summary format
- Support multiple Notion databases
- Add session naming/tagging
- Include timestamps in summaries
- Export to other formats (PDF, Markdown)
