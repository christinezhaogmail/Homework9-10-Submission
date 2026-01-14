# 1. Update the 'Tool' import location
from langchain_core.tools import Tool 
from langchain.agents import initialize_agent
from langchain_community.chat_models import ChatOpenAI

# Step 1: Define Your Functions
def get_weather(city):
    # Replace with a real API call if needed
    return f"The weather in {city} is sunny with a high of 25°C."

# Step 2: Wrap Functions as Tools
weather_tool = Tool(
    name="get_weather",
    func=get_weather,
    description="Fetches weather information for a given city."
)

# Step 3: Initialize the Agent
# Initialize the language model
# Using langchain_community for ChatOpenAI is best practice now
llm = ChatOpenAI(temperature=0)

# Add tools to the agent
tools = [weather_tool]

# Note: The 'initialize_agent' and 'zero-shot-react-description' are deprecated,
# but we keep them here to match your original agent pattern.
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

# Step 4: Test the Agent
response = agent.run("What is the weather in New York?")
print(response)