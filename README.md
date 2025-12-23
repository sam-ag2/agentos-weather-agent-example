# Weather Agent Examples

A collection of weather agent implementations demonstrating how to build AI agents across multiple frameworks. All examples use the free [Open-Meteo API](https://open-meteo.com/) for weather data (no API key required).

## Overview

This repository showcases how the same weather agent can be implemented using different AI agent frameworks:

| Framework | File | Provider |
|-----------|------|----------|
| [AG2](https://github.com/ag2ai/ag2) | `weather_agent.py` | OpenAI |
| [Google ADK](https://github.com/google/adk-python) | `agent_google_adk.py` | Google (Gemini) |
| [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | `agent_openai_sdk.py` | OpenAI |
| [LangGraph](https://github.com/langchain-ai/langgraph) | `agent_langgraph.py` | OpenAI |
| [CrewAI](https://github.com/crewAIInc/crewAI) | `agent_crewai.py` | OpenAI |

All implementations provide the same two tools:
- **get_current_weather** - Current conditions for any city
- **get_weather_forecast** - Multi-day forecast (1-7 days)

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/sam-ag2/agentos-weather-agent-example.git
cd agentos-weather-agent-example

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies for your chosen framework
pip install -r requirements.txt
```

### 2. Set API Keys

```bash
# For OpenAI-based agents (AG2, OpenAI SDK, LangGraph, CrewAI)
export OPENAI_API_KEY="your-api-key"

# For Google ADK
export GOOGLE_API_KEY="your-api-key"
```

### 3. Run an Agent

```bash
# AG2 (with A2A server)
python weather_agent.py

# Google ADK
adk run agent_google_adk.py
# or
adk web agent_google_adk.py

# OpenAI Agents SDK
python agent_openai_sdk.py

# LangGraph
python agent_langgraph.py

# CrewAI
python agent_crewai.py
```

---

## Framework Examples

### AG2 (AutoGen)

The AG2 implementation exposes an A2A (Agent-to-Agent) protocol endpoint, making it discoverable and interoperable with other agents.

```python
from autogen import ConversableAgent, LLMConfig
from autogen.tools import tool
from autogen.interop.a2a import A2aAgentServer, CardSettings

@tool(name="get_current_weather", description="Get current weather for a city")
def get_current_weather(city: str, country: str = "") -> str:
    # Implementation
    pass

agent = ConversableAgent(
    name="WeatherAgent",
    llm_config=LLMConfig({"model": "gpt-4o-mini"}),
    functions=[get_current_weather, get_weather_forecast],
)

server = A2aAgentServer(agents=[agent], card_settings=card_settings)
server.run()
```

**Run**: `python weather_agent.py`
**Endpoint**: `http://localhost:8000/weather/.well-known/agent.json`

---

### Google ADK

Google's Agent Development Kit uses plain Python functions as tools with dict returns for structured responses.

```python
from google.adk.agents import Agent

def get_current_weather(city: str, country: str = "") -> dict:
    result = fetch_current_weather(city, country)
    return {"status": "success", "report": result}

agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="Weather information agent",
    instruction="You are a helpful weather assistant...",
    tools=[get_current_weather, get_weather_forecast],
)
```

**Run**: `adk run agent_google_adk.py` or `adk web agent_google_adk.py`

---

### OpenAI Agents SDK

OpenAI's native agent framework using the `@function_tool` decorator.

```python
from agents import Agent, Runner, function_tool

@function_tool
def get_current_weather(city: str, country: str = "") -> str:
    return fetch_current_weather(city, country)

agent = Agent(
    name="WeatherAgent",
    instructions="You are a helpful weather assistant...",
    tools=[get_current_weather, get_weather_forecast],
    model="gpt-4o-mini",
)

# Usage
result = await Runner.run(agent, "What's the weather in Tokyo?")
```

**Run**: `python agent_openai_sdk.py`

---

### LangGraph

LangChain's graph-based agent framework with a prebuilt ReAct agent.

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

@tool
def get_current_weather(city: str, country: str = "") -> str:
    """Get current weather for a city."""
    return fetch_current_weather(city, country)

model = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(model, [get_current_weather, get_weather_forecast])
```

**Run**: `python agent_langgraph.py`

---

### CrewAI

Multi-agent orchestration framework using Tasks and Crews.

```python
from crewai import Agent, Task, Crew
from crewai.tools import tool

@tool("get_current_weather")
def get_current_weather(city: str, country: str = "") -> str:
    """Get current weather for a city."""
    return fetch_current_weather(city, country)

weather_agent = Agent(
    role="Weather Assistant",
    goal="Provide accurate weather information",
    tools=[get_current_weather, get_weather_forecast],
)

task = Task(description="What's the weather in Paris?", agent=weather_agent)
crew = Crew(agents=[weather_agent], tasks=[task])
result = crew.kickoff()
```

**Run**: `python agent_crewai.py`

---

## Project Structure

```
agentos-weather-agent-example/
    weather_agent.py       # AG2 implementation with A2A server
    agent_google_adk.py    # Google ADK implementation
    agent_openai_sdk.py    # OpenAI Agents SDK implementation
    agent_langgraph.py     # LangGraph implementation
    agent_crewai.py        # CrewAI implementation
    weather_utils.py       # Shared weather API functions
    requirements.txt       # All framework dependencies
    README.md              # This file
```

## Shared Utilities

All framework examples use `weather_utils.py` which provides:

- `geocode_city(city, country)` - Convert city name to coordinates
- `fetch_current_weather(city, country)` - Get current conditions
- `fetch_weather_forecast(city, country, days)` - Get multi-day forecast

The utilities use the [Open-Meteo API](https://open-meteo.com/) which is free and requires no API key.

## Learn More

- [AG2 Documentation](https://docs.ag2.ai/)
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Open-Meteo API](https://open-meteo.com/en/docs)

## License

MIT License
