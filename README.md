# Weather Agent - AgentOS Hello World

A simple example agent for [AgentOS](https://github.com/ag2ai/ag2) that provides weather information using the free Open-Meteo API.

## What This Example Demonstrates

- Creating an AG2 `ConversableAgent` with custom tools
- Exposing the agent via the A2A (Agent-to-Agent) protocol
- Defining an agent card with skills for discovery by AgentOS

## Prerequisites

- Python 3.10+
- An OpenAI API key (for the LLM)

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/ag2ai/agentos-weather-agent-example.git
cd agentos-weather-agent-example

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Your API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Run the Agent

```bash
python weather_agent.py
```

The agent will start on `http://localhost:8000`.

### 4. Test the Agent

The agent exposes an A2A-compatible endpoint. You can view the agent card at:

```
http://localhost:8000/weather/.well-known/agent.json
```

## How It Works

### Tools

The agent has two tools:

1. **get_current_weather** - Returns current temperature, humidity, wind, and conditions for any city
2. **get_weather_forecast** - Returns a multi-day forecast (up to 7 days)

Both tools use the [Open-Meteo API](https://open-meteo.com/) which is free and requires no API key.

### Agent Card

The agent publishes an A2A-compatible agent card that describes its capabilities:

```json
{
  "name": "WeatherAgent",
  "description": "A weather information agent...",
  "skills": [
    {
      "id": "current_weather",
      "name": "Current Weather",
      "examples": ["What's the weather in Tokyo?"]
    },
    {
      "id": "weather_forecast",
      "name": "Weather Forecast",
      "examples": ["What's the 5-day forecast for Paris?"]
    }
  ]
}
```

## Registering with AgentOS

To make this agent discoverable by AgentOS, you can register it with an AgentOS registry:

```bash
# Set your AgentOS registry URL
export AGENTOS_REGISTRY_URL="https://your-agentos-instance.com"

# Register the agent (requires the agent to be running)
curl -X POST "$AGENTOS_REGISTRY_URL/api/agents/register" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://your-agent-host:8000/weather/"}'
```

## Customization

### Changing the LLM

Edit the `llm_config` in `weather_agent.py`:

```python
# Use a different model
llm_config = LLMConfig({"model": "gpt-4o"})

# Or use a different provider (requires appropriate API key)
llm_config = LLMConfig({
    "model": "claude-3-5-sonnet-20241022",
    "api_type": "anthropic"
})
```

### Adding More Tools

Add new tools using the `@tool` decorator:

```python
@tool(
    name="get_air_quality",
    description="Get air quality index for a city.",
)
def get_air_quality(city: str) -> str:
    # Your implementation here
    pass

# Add to the agent
agent = ConversableAgent(
    ...
    functions=[get_current_weather, get_weather_forecast, get_air_quality],
)
```

## Project Structure

```
agentos-weather-agent-example/
    weather_agent.py    # Main agent code
    requirements.txt    # Python dependencies
    README.md          # This file
```

## Learn More

- [AG2 Documentation](https://docs.ag2.ai/)
- [A2A Protocol Specification](https://github.com/google/A2A)
- [Open-Meteo API](https://open-meteo.com/en/docs)

## License

MIT License
