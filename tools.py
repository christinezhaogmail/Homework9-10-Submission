# 1. Imports (Should work after upgrading all packages)
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain import hub


# Step 1: Define Your Function using the @tool decorator
@tool
def get_weather(city: str) -> str:
    """
    Fetches the current weather information for a specific city. 
    Use this tool when the user asks for weather conditions in a location.
    The input must be the city name as a string.
    """
    return f"The weather in {city} is sunny with a high of 25°C."

# Step 2: Initialize the LLM and Tools
llm = ChatOpenAI(temperature=0)
tools = [get_weather]

# Step 3: Get the Agent Prompt
prompt = hub.pull("hwchase17/react")

# Step 4: Create the Agent and Executor
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

# Step 5: Test the Agent
response = agent_executor.invoke({"input": "What is the weather in New York?"})

print("-" * 30)
print("Final Response:", response["output"])