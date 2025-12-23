"""
Weather Agent - OpenAI Agents SDK

Demonstrates building a weather agent using OpenAI's Agents SDK.
https://github.com/openai/openai-agents-python

Requirements:
    pip install openai-agents httpx

Environment:
    OPENAI_API_KEY
"""

import asyncio
from agents import Agent, Runner, function_tool
from weather_utils import fetch_current_weather, fetch_weather_forecast


@function_tool
def get_current_weather(city: str, country: str = "") -> str:
    """
    Get the current weather conditions for a city.

    Args:
        city: The city name (e.g., 'London', 'New York', 'Tokyo')
        country: Optional country code to disambiguate (e.g., 'US', 'UK')
    """
    return fetch_current_weather(city, country)


@function_tool
def get_weather_forecast(city: str, country: str = "", days: int = 3) -> str:
    """
    Get a multi-day weather forecast for a city.

    Args:
        city: The city name (e.g., 'London', 'New York', 'Tokyo')
        country: Optional country code to disambiguate (e.g., 'US', 'UK')
        days: Number of days to forecast (1-7)
    """
    return fetch_weather_forecast(city, country, days)


# Create the OpenAI agent
agent = Agent(
    name="WeatherAgent",
    instructions="""You are a helpful weather assistant. When users ask about weather,
use the available tools to fetch current conditions or forecasts. Be clear about
which city you're reporting on, especially for ambiguous city names.""",
    tools=[get_current_weather, get_weather_forecast],
    model="gpt-4o-mini",
)


async def main():
    """Run the agent interactively."""
    print("OpenAI Agents SDK Weather Agent")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        result = await Runner.run(agent, user_input)
        print(f"Agent: {result.final_output}\n")


if __name__ == "__main__":
    asyncio.run(main())
