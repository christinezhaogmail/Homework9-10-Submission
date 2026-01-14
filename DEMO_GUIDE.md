# Demo Video Guide

This guide will help you create a compelling 1-2 minute demo video for the AI Voice Agent assignment.

## Demo Requirements

According to the assignment, your demo should show:

1. **A math query** - Invoking the `calculate` function
2. **An arXiv search query** - Invoking the `search_arxiv` function
3. **A normal query** - No function call, just regular conversation

## Recommended Demo Flow

### Introduction (10 seconds)
- Show the application interface (Streamlit or CLI)
- Brief introduction: "This is my AI Voice Agent with function calling"

### Demo 1: Math Query (20-30 seconds)
**Query**: "What is 25 multiplied by 4?"

**What to show**:
1. Enter the query
2. Show the LLM detecting it needs to call a function
3. Show the function call JSON: `{"function": "calculate", "arguments": {"expression": "25*4"}}`
4. Show the result: "The result is: 100"
5. Point out the function was called automatically

**Narration**: "First, let me ask a math question. The agent recognizes this as a calculation task and automatically calls the calculate function, returning the correct result."

### Demo 2: arXiv Search (30-40 seconds)
**Query**: "What is quantum entanglement?"

**What to show**:
1. Enter the query
2. Show the LLM generating a function call
3. Show the function call JSON: `{"function": "search_arxiv", "arguments": {"query": "quantum entanglement", "limit": 10}}`
4. Show some of the paper results returned
5. Point out the titles and summaries of papers found

**Narration**: "Next, I'll ask a scientific question. The agent identifies this as a research query and calls the search_arxiv function, returning relevant papers from the arXiv repository."

### Demo 3: Normal Conversation (15-20 seconds)
**Query**: "Hello, how are you?"

**What to show**:
1. Enter the query
2. Show the LLM responding with regular text (no function call)
3. Show the conversational response
4. Point out that no function was called

**Narration**: "Finally, for a general greeting, the agent responds normally without calling any functions, showing it can distinguish between different types of queries."

### Closing (5-10 seconds)
- Quick summary: "The agent successfully handles calculations, research queries, and conversations"
- Show the logs or details panel demonstrating the full pipeline

## Tips for a Great Demo

### Visual Tips
1. **Use Streamlit interface** - More visually appealing than CLI
2. **Enable the Details expander** - Show function calls and processing
3. **Keep the UI clean** - Close unnecessary windows/tabs
4. **Use zoom/screen recording** - Make text readable
5. **Show the logs** - Demonstrates comprehensive logging requirement

### Recording Tips
1. **Screen recorder**: Use OBS Studio, QuickTime, or Loom
2. **Resolution**: 1920x1080 recommended
3. **Audio**: Clear narration explaining what's happening
4. **Length**: Aim for 90-120 seconds
5. **Practice**: Do a test run to ensure smooth flow

### What to Emphasize
1. **Function calling detection** - Show the JSON output
2. **Automatic routing** - Highlight that it's automatic
3. **Error handling** - Optionally show "What is 1 divided by 0?" to demonstrate graceful error handling
4. **Logging** - Show comprehensive logging of all steps
5. **Tool integration** - Explain how LangChain tools work

## Example Scripts

### Script 1: Detailed (for longer demo)
```
"Hi, I'm demonstrating my AI Voice Agent with function calling capabilities.

The agent uses Llama 3.2 to analyze queries and automatically call functions when needed.

Let me start with a math question: 'What is 25 multiplied by 4?'
As you can see, the LLM recognized this as a calculation and generated a function call to the calculate tool.
The expression '25*4' is evaluated, and we get the result: 100.

Next, let me ask a research question: 'What is quantum entanglement?'
The agent identifies this as a scientific query and calls the search_arxiv function.
Here you can see several relevant papers from arXiv with titles, authors, and summaries.

Finally, let me try a normal conversation: 'Hello, how are you?'
For this greeting, the agent responds naturally without calling any functions.

The system includes comprehensive logging, showing the query, LLM output, function calls, and final response for each interaction.

This demonstrates a fully functional voice agent with intelligent function calling."
```

### Script 2: Concise (for shorter demo)
```
"This is my AI Voice Agent with function calling.

First, a math query [show calculation]
The agent calls the calculate function automatically.

Second, a research query [show arXiv search]
It calls search_arxiv and returns relevant papers.

Third, a normal conversation [show greeting]
No function call needed - just a regular response.

All interactions are logged, and the agent handles errors gracefully."
```

## Additional Demo Ideas

### Bonus Demos (if time permits):

**Error Handling**:
- Query: "What is 1 divided by 0?"
- Show graceful error message

**Complex Calculation**:
- Query: "What is the square root of 144?"
- Show SymPy handling advanced math

**Multiple Papers**:
- Query: "Find papers on neural networks"
- Show multiple relevant results

## Technical Setup for Recording

### Before Recording:
1. Start Ollama server: `ollama serve`
2. Ensure conda environment is activated: `conda activate hw6_310`
3. Start Streamlit: `streamlit run frontend.py`
4. Test all three queries to ensure they work
5. Clear conversation history for a clean demo
6. Close unnecessary applications
7. Disable notifications

### During Recording:
1. Start with a clear view of the interface
2. Type queries slowly and clearly
3. Wait for responses to complete before moving on
4. Narrate what's happening
5. Point to important elements (cursor or annotations)

### After Recording:
1. Review the video for clarity
2. Add captions if needed
3. Trim any dead time
4. Add title/intro slide if desired
5. Export in a standard format (MP4)

## Submission Checklist

- [ ] Video is 1-2 minutes long
- [ ] Shows math calculation with function call
- [ ] Shows arXiv search with function call
- [ ] Shows normal conversation without function call
- [ ] Clear audio narration
- [ ] Readable text on screen
- [ ] Demonstrates logging (optional but impressive)
- [ ] Shows error handling (optional but impressive)
- [ ] Smooth flow between demos
- [ ] Professional presentation

## Example Test Logs Format

Include in your submission alongside the video:

```
Query 1: What is 25 multiplied by 4?
----------------------------------------
User Query: What is 25 multiplied by 4?
Raw LLM Output: {"function": "calculate", "arguments": {"expression": "25*4"}}
Function Called: calculate
Function Arguments: {'expression': '25*4'}
Function Output: The result is: 100
Final Response: The result is: 100

Query 2: What is quantum entanglement?
----------------------------------------
User Query: What is quantum entanglement?
Raw LLM Output: {"function": "search_arxiv", "arguments": {"query": "quantum entanglement", "limit": 10}}
Function Called: search_arxiv
Function Arguments: {'query': 'quantum entanglement', 'limit': 10}
Function Output: Found 10 papers on arXiv:
[Paper details...]
Final Response: [Paper summaries...]

Query 3: Hello, how are you?
----------------------------------------
User Query: Hello, how are you?
Raw LLM Output: Hello! I'm doing well, thank you for asking. How can I help you today?
Function Called: None
Function Arguments: None
Function Output: N/A
Final Response: Hello! I'm doing well, thank you for asking. How can I help you today?
```

## Resources

- **OBS Studio**: https://obsproject.com/ (Free screen recording)
- **Loom**: https://www.loom.com/ (Easy browser-based recording)
- **QuickTime**: Built-in on macOS for screen recording

Good luck with your demo! 🎬
