"""
Weather Agent - CrewAI

Demonstrates building a weather agent using the CrewAI framework.
https://github.com/crewAIInc/crewAI

Requirements:
    pip install crewai httpx

Environment:
    OPENAI_API_KEY
"""

from crewai import Agent, Task, Crew
from crewai.tools import tool
from weather_utils import fetch_current_weather, fetch_weather_forecast


@tool("get_current_weather")
def get_current_weather(city: str, country: str = "") -> str:
    """
    Get the current weather conditions for a city.
    Use this tool when users ask about current weather, temperature, or conditions.

    Args:
        city: The city name (e.g., 'London', 'New York', 'Tokyo')
        country: Optional country code to disambiguate (e.g., 'US', 'UK')
    """
    return fetch_current_weather(city, country)


@tool("get_weather_forecast")
def get_weather_forecast(city: str, country: str = "", days: int = 3) -> str:
    """
    Get a multi-day weather forecast for a city.
    Use this tool when users ask about future weather or forecasts.

    Args:
        city: The city name (e.g., 'London', 'New York', 'Tokyo')
        country: Optional country code to disambiguate (e.g., 'US', 'UK')
        days: Number of days to forecast (1-7)
    """
    return fetch_weather_forecast(city, country, days)


# Create the CrewAI agent
weather_agent = Agent(
    role="Weather Assistant",
    goal="Provide accurate weather information for cities worldwide",
    backstory="""You are a helpful weather assistant with access to real-time
weather data. You help users by fetching current conditions and forecasts
for any city they ask about. You're clear about which city you're reporting
on, especially when city names are ambiguous.""",
    tools=[get_current_weather, get_weather_forecast],
    verbose=True,
)


def run_weather_query(query: str) -> str:
    """Run a weather query through the CrewAI agent."""
    task = Task(
        description=f"Answer the following weather question: {query}",
        expected_output="A clear and helpful response about the weather",
        agent=weather_agent,
    )

    crew = Crew(
        agents=[weather_agent],
        tasks=[task],
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)


def main():
    """Run the agent interactively."""
    print("CrewAI Weather Agent")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        response = run_weather_query(user_input)
        print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()
