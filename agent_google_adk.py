"""
Weather Agent - Google ADK (Agent Development Kit)

Demonstrates building a weather agent using Google's ADK framework.
https://github.com/google/adk-python

Requirements:
    pip install google-adk httpx

Environment:
    GOOGLE_API_KEY or GOOGLE_GENAI_USE_VERTEXAI=true
"""

from google.adk.agents import Agent
from weather_utils import fetch_current_weather, fetch_weather_forecast


def get_current_weather(city: str, country: str = "") -> dict:
    """
    Get the current weather conditions for a city.

    Args:
        city: The city name (e.g., 'London', 'New York', 'Tokyo')
        country: Optional country code to disambiguate (e.g., 'US', 'UK')

    Returns:
        A dict with status and weather report or error message
    """
    result = fetch_current_weather(city, country)
    if "Error" in result or "not found" in result:
        return {"status": "error", "error_message": result}
    return {"status": "success", "report": result}


def get_weather_forecast(city: str, country: str = "", days: int = 3) -> dict:
    """
    Get a multi-day weather forecast for a city.

    Args:
        city: The city name (e.g., 'London', 'New York', 'Tokyo')
        country: Optional country code to disambiguate (e.g., 'US', 'UK')
        days: Number of days to forecast (1-7)

    Returns:
        A dict with status and forecast report or error message
    """
    result = fetch_weather_forecast(city, country, days)
    if "Error" in result or "not found" in result:
        return {"status": "error", "error_message": result}
    return {"status": "success", "report": result}


# Create the Google ADK agent
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="A weather information agent that provides current conditions and forecasts for cities worldwide.",
    instruction="""You are a helpful weather assistant. When users ask about weather,
use the available tools to fetch current conditions or forecasts. Be clear about
which city you're reporting on, especially for ambiguous city names.""",
    tools=[get_current_weather, get_weather_forecast],
)


if __name__ == "__main__":
    # Run with ADK's built-in dev server
    # adk web agent_google_adk.py
    print("Google ADK Weather Agent")
    print("Run with: adk web agent_google_adk.py")
    print("Or use: adk run agent_google_adk.py")
