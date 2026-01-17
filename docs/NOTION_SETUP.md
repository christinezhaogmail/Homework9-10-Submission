# Notion Integration Setup Guide

This guide walks you through setting up Notion integration for the AI Research Assistant.

---

## 📋 Overview

The Notion integration allows you to:
- Persist conversation sessions to your Notion workspace
- Store research summaries for later reference
- Track query counts and metadata
- Access conversations from any device via Notion

---

## 🚀 Quick Setup

### Step 1: Create Notion Integration

1. **Go to Notion Integrations**
   - Visit: https://www.notion.so/my-integrations
   - Click **"+ New integration"**

2. **Configure Integration**
   - **Name**: AI Research Assistant (or your preferred name)
   - **Associated workspace**: Select your workspace
   - **Type**: Internal integration
   - Click **"Submit"**

3. **Copy Integration Token**
   - After creation, you'll see the "Internal Integration Token"
   - Click **"Show"** and **"Copy"**
   - Save this token - you'll need it later
   - Format: `ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Create Notion Database

1. **Create a New Database**
   - Open Notion
   - Create a new page
   - Type `/database` and select "Database - Full page"
   - Name it: "AI Research Sessions" (or your preferred name)

2. **Add Properties** (Optional but recommended)

   The integration works with ANY database, but for best results, add these properties:

   | Property Name | Type | Required | Description |
   |---------------|------|----------|-------------|
   | Name | Title | ✅ Yes | Automatically created - session title |
   | Session ID | Text | ⚠️ Recommended | Unique session identifier |
   | Date | Date | ⚠️ Recommended | When session was created |
   | Query Count | Number | ⚪ Optional | Number of queries in session |

   **How to add properties:**
   - Click the **"+"** button in the database header
   - Select property type
   - Name it exactly as shown above (case-sensitive)

3. **Share Database with Integration**
   - Click the **"..."** menu (top right of database)
   - Click **"Add connections"**
   - Search for your integration name
   - Click to connect
   - ✅ Integration should now appear in connections list

4. **Get Database ID**
   - Open the database as a full page
   - Copy the URL from your browser
   - Format: `https://www.notion.so/workspace-name/DATABASE_ID?v=view_id`
   - Extract the `DATABASE_ID` part (32 characters, no dashes)
   - Example: `abc123def456ghi789jkl012mno345pq`

### Step 3: Configure Environment Variables

#### Option A: Using .env file (Recommended)

```bash
# Edit your .env file
nano .env

# Add these lines:
NOTION_TOKEN=ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=abc123def456ghi789jkl012mno345pq
```

#### Option B: Export in terminal

```bash
export NOTION_TOKEN="ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export NOTION_DATABASE_ID="abc123def456ghi789jkl012mno345pq"
```

#### Option C: Add to shell profile (Permanent)

```bash
# For bash
echo 'export NOTION_TOKEN="ntn_xxxx..."' >> ~/.bash_profile
echo 'export NOTION_DATABASE_ID="abc123..."' >> ~/.bash_profile
source ~/.bash_profile

# For zsh (macOS default)
echo 'export NOTION_TOKEN="ntn_xxxx..."' >> ~/.zshrc
echo 'export NOTION_DATABASE_ID="abc123..."' >> ~/.zshrc
source ~/.zshrc
```

### Step 4: Test the Integration

```bash
# Run Notion test
python test/test_notion.py
```

Expected output:
```
======================================================================
NOTION SYNC - TEST SUITE
======================================================================

======================================================================
TEST 1: Notion Initialization
======================================================================

[Test 1.1] Initialize Notion client
✓ Notion client initialized successfully
   Database ID: abc123def4...

======================================================================
TEST 2: Session Sync
======================================================================

[Test 2.1] Sync session to Notion
Available Notion properties: {'Name', 'Session ID', 'Date', 'Query Count'}
✓ Session synced successfully
   Notion URL: https://www.notion.so/...

======================================================================
🎉 ALL NOTION TESTS PASSED!
======================================================================
```

---

## 🛠️ Troubleshooting

### Error: "Notion sync not enabled"

**Problem**: Missing environment variables

**Solution**:
```bash
# Check if variables are set
echo $NOTION_TOKEN
echo $NOTION_DATABASE_ID

# If empty, set them
export NOTION_TOKEN="your_token"
export NOTION_DATABASE_ID="your_database_id"
```

### Error: "Unauthorized" or "Invalid token"

**Problem**: Incorrect integration token

**Solutions**:
1. Verify token starts with `ntn_` (note: older integrations may start with `secret_`, see https://github.com/ramnes/notion-sdk-py/issues/245)
2. Copy token again from https://www.notion.so/my-integrations
3. Ensure no extra spaces when setting environment variable
4. Try regenerating the integration token

### Error: "Database not found"

**Problem**: Incorrect database ID or integration not connected

**Solutions**:
1. **Verify Database ID**:
   - Open database in browser
   - Check URL format: `notion.so/workspace/DATABASE_ID?v=...`
   - DATABASE_ID should be 32 characters (no dashes in the middle part)

2. **Check Integration Connection**:
   - Open database in Notion
   - Click "..." menu → "Connections"
   - Your integration should be listed
   - If not, click "Add connections" and add it

### Error: "Property does not exist"

**Problem**: Database missing expected properties

**Solution**:
The integration now works with ANY database! However, for full features:

```bash
# Minimum (works with any database):
- Name (Title) - automatically exists

# Recommended (add these properties):
- Session ID (Text)
- Date (Date)
- Query Count (Number)
```

To add properties:
1. Open database in Notion
2. Click "+" in header
3. Select property type
4. Name exactly as shown above

### Integration works but no data appears

**Problem**: Page created but content missing

**Solution**:
1. Check if page was created (might be at bottom of database)
2. Open the page - content is in page body, not properties
3. Verify integration has "Insert content" permission
4. Try recreating integration with all permissions

---

## 📊 Database Schema Examples

### Minimal Setup (Works out of the box)
```
Database: AI Research Sessions
├── Name (Title) ✅ Required
```

### Recommended Setup
```
Database: AI Research Sessions
├── Name (Title) ✅ Required
├── Session ID (Text)
├── Date (Date)
└── Query Count (Number)
```

### Advanced Setup
```
Database: AI Research Sessions
├── Name (Title) ✅ Required
├── Session ID (Text)
├── Date (Date)
├── Query Count (Number)
├── Tags (Multi-select) - e.g., "Physics", "AI", "Biology"
├── Status (Select) - e.g., "New", "Reviewed", "Archived"
└── Papers Found (Number)
```

---

## 🔐 Security Best Practices

1. **Never commit tokens to Git**
   ```bash
   # .env should be in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Rotate tokens periodically**
   - Go to https://www.notion.so/my-integrations
   - Click your integration
   - Click "Regenerate token"
   - Update environment variable

3. **Use workspace-specific integrations**
   - Create separate integrations for dev/prod
   - Use different databases for testing

4. **Limit integration permissions**
   - Only grant necessary permissions
   - Review integration access regularly

---

## 📖 Usage Examples

### Via API

```bash
# Sync a session
curl -X POST http://localhost:8000/notion-sync \
  -F "session_id=abc-123-def" \
  -F "include_summary=true"
```

### Via Python

```python
from tools.notion import NotionSync

# Initialize
notion = NotionSync()

# Sync session
url = notion.sync_session(
    session_id="test-session-123",
    content="User: What is quantum entanglement?\nAssistant: ...",
    summary="Discussion about quantum physics",
    metadata={"query_count": 2}
)

print(f"Synced to: {url}")
```

### Via Streamlit UI

1. Have a conversation with the assistant
2. Click **"Sync to Notion"** button in sidebar
3. View the generated Notion page link

---

## 🎯 What Gets Synced

Each synced session creates a Notion page with:

### Properties (if available in database)
- **Name**: "Research Session: {session_id}"
- **Session ID**: Unique identifier
- **Date**: Creation timestamp
- **Query Count**: Number of queries

### Page Content
- **Summary Section**: AI-generated summary of conversation
- **Full Conversation**: Complete transcript with timestamps

### Example Notion Page

```
Title: Research Session: 20240117_143022

Properties:
  Session ID: abc-123-def-456
  Date: January 17, 2024
  Query Count: 3

Content:
  ## Summary
  User asked about quantum entanglement, searched 3 papers,
  and discussed applications in quantum computing.

  ## Full Conversation
  [2024-01-17 14:30:22] User: What is quantum entanglement?
  [2024-01-17 14:30:25] Assistant: Quantum entanglement is...
  ...
```

---

## 🆘 Still Having Issues?

1. **Check logs**:
   ```bash
   tail -f logs/voice_agent_*.log | grep -i notion
   ```

2. **Run diagnostic**:
   ```bash
   python -c "from tools.notion import NotionSync; n = NotionSync(); print(f'Enabled: {n.is_enabled()}')"
   ```

3. **Verify database access**:
   ```bash
   python test/test_notion.py
   ```

4. **Contact support**:
   - Check [GitHub Issues](https://github.com/yourusername/ai-research-assistant/issues)
   - Include error message and steps to reproduce

---

## 📚 Additional Resources

- [Notion API Documentation](https://developers.notion.com/)
- [Notion Python SDK](https://github.com/ramnes/notion-sdk-py)
- [Creating Integrations Guide](https://developers.notion.com/docs/create-a-notion-integration)
- [Database Properties Reference](https://developers.notion.com/reference/property-object)
