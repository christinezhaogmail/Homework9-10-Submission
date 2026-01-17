# Test Suite for AI Research Assistant

This directory contains comprehensive test scripts for all components of the AI Research Assistant.

## Test Files

| Test File | Component | Description |
|-----------|-----------|-------------|
| `test_hardware.py` | Hardware Detection | Tests device detection (CUDA/MPS/CPU) |
| `test_session_manager.py` | Session Management | Tests session creation, history, and context |
| `test_search.py` | Academic Search | Tests ArXiv search functionality |
| `test_summarize.py` | Summarization | Tests HuggingFace summarization |
| `test_notion.py` | Notion Sync | Tests Notion API integration |
| `test_api_models.py` | API Models | Tests Pydantic data models |
| `test_all.py` | Master Runner | Runs all tests in sequence |

## Running Tests

### Run All Tests

```bash
# From project root
python test/test_all.py
```

### Run Individual Tests

```bash
# Test hardware detection
python test/test_hardware.py

# Test session management
python test/test_session_manager.py

# Test academic search
python test/test_search.py

# Test summarization (downloads model on first run)
python test/test_summarize.py

# Test Notion sync (requires credentials)
python test/test_notion.py

# Test API models
python test/test_api_models.py
```

## Test Requirements

### Basic Tests
Most tests run without additional configuration:
- `test_hardware.py` - No configuration needed
- `test_session_manager.py` - No configuration needed
- `test_api_models.py` - No configuration needed

### Tests Requiring External Services

#### ArXiv Search (`test_search.py`)
- Requires internet connection
- No API key needed (public ArXiv API)

#### Summarization (`test_summarize.py`)
- Requires internet connection (first run only)
- Downloads BART model (~1.6GB) on first run
- Subsequent runs use cached model

#### Notion Sync (`test_notion.py`)
- Requires Notion integration setup
- Environment variables needed:
  ```bash
  export NOTION_TOKEN="your_token_here"
  export NOTION_DATABASE_ID="your_database_id_here"
  ```

## Setting Up Notion Tests

1. **Create Notion Integration:**
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Give it a name and select your workspace
   - Copy the "Internal Integration Token"

2. **Create Notion Database:**
   - Create a new database in Notion
   - Add the following properties:
     - `Session ID` (Text)
     - `Date` (Date)
     - `Query Count` (Number)
   - Share the database with your integration

3. **Get Database ID:**
   - Open the database in Notion
   - Copy the URL: `https://notion.so/workspace/DATABASE_ID?v=...`
   - Extract the `DATABASE_ID` part

4. **Set Environment Variables:**
   ```bash
   export NOTION_TOKEN="ntn_xyz..."
   export NOTION_DATABASE_ID="abc123..."
   ```

## Expected Output

Each test prints:
- ✅ for passed tests
- ❌ for failed tests
- ⚠️  for skipped tests (missing configuration)

Example output:
```
======================================================================
HARDWARE DETECTION - TEST SUITE
======================================================================

======================================================================
TEST 1: Device Detection
======================================================================

[Test 1.1] Get device
Detected device: mps
✅ Device detected: mps

...

======================================================================
🎉 ALL HARDWARE TESTS PASSED!
======================================================================
```

## Continuous Integration

To run tests in CI/CD:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (skip Notion tests if no credentials)
python test/test_all.py
```

## Troubleshooting

### Import Errors
Make sure you're running tests from the project root:
```bash
cd /home/jovyan/Homework9-10-Submission
python test/test_hardware.py
```

### Model Download Failures
If summarization model download fails:
```bash
# Set HuggingFace cache directory
export HF_HOME=/home/jovyan/cache
python test/test_summarize.py
```

### Notion Tests Fail
- Verify NOTION_TOKEN is valid
- Verify NOTION_DATABASE_ID is correct
- Ensure database is shared with integration
- Check database has correct properties

## Test Coverage

The test suite covers:
- ✅ Hardware detection and device selection
- ✅ Session management and conversation history
- ✅ ArXiv search with various queries
- ✅ Text summarization with different lengths
- ✅ Notion API integration (if configured)
- ✅ Pydantic model validation
- ✅ Error handling and edge cases

## Adding New Tests

To add a new test file:

1. Create `test/test_yourcomponent.py`
2. Follow the existing test structure:
   ```python
   import sys
   from loguru import logger

   logger.remove()
   logger.add(sys.stdout, level="INFO")

   def test_feature():
       print("\n" + "=" * 70)
       print("TEST 1: Feature Name")
       print("=" * 70)
       # Your tests here

   def main():
       try:
           test_feature()
           print("🎉 ALL TESTS PASSED!")
       except Exception as e:
           print(f"❌ TEST FAILED: {e}")
           sys.exit(1)

   if __name__ == "__main__":
       main()
   ```
3. Add to `test_all.py` test_files list
4. Update this README

## Performance Notes

- `test_hardware.py`: < 1 second
- `test_session_manager.py`: < 1 second
- `test_api_models.py`: < 1 second
- `test_search.py`: ~5-10 seconds (network I/O)
- `test_summarize.py`: ~30-60 seconds first run (model download), ~10 seconds subsequent runs
- `test_notion.py`: ~5 seconds (if configured)

Total test time: ~1-2 minutes (after initial model download)
