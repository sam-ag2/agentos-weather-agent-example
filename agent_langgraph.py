"""
Weather Agent - LangGraph

Demonstrates building a weather agent using LangChain's LangGraph framework.
https://github.com/langchain-ai/langgraph

Requirements:
    pip install langgraph langchain-openai httpx

Environment:
    OPENAI_API_KEY
"""

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from weather_utils import fetch_current_weather, fetch_weather_forecast


@tool
def get_current_weather(city: str, country: str = "") -> str:
    """
    Get the current weather conditions for a city.

    Args:
        city: The city name (e.g., 'London', 'New York', 'Tokyo')
        country: Optional country code to disambiguate (e.g., 'US', 'UK')
    """
    return fetch_current_weather(city, country)


@tool
def get_weather_forecast(city: str, country: str = "", days: int = 3) -> str:
    """
    Get a multi-day weather forecast for a city.

    Args:
        city: The city name (e.g., 'London', 'New York', 'Tokyo')
        country: Optional country code to disambiguate (e.g., 'US', 'UK')
        days: Number of days to forecast (1-7)
    """
    return fetch_weather_forecast(city, country, days)


# Create the LangGraph ReAct agent
model = ChatOpenAI(model="gpt-4o-mini")
tools = [get_current_weather, get_weather_forecast]

agent = create_react_agent(
    model,
    tools,
    prompt="You are a helpful weather assistant. When users ask about weather, "
    "use the available tools to fetch current conditions or forecasts. Be clear "
    "about which city you're reporting on, especially for ambiguous city names.",
)


def run_agent(query: str) -> str:
    """Run the agent with a query and return the response."""
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    # Extract the final AI message
    for message in reversed(result["messages"]):
        if hasattr(message, "content") and message.type == "ai":
            return message.content
    return "No response generated"


def main():
    """Run the agent interactively."""
    print("LangGraph Weather Agent")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        response = run_agent(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()
