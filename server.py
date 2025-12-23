"""
Unified Weather Agent Server

A FastAPI server hosting weather agents built with multiple frameworks,
all exposed via A2A-compatible endpoints.

Endpoints:
    /ag2/              - AG2 (AutoGen) weather agent
    /google-adk/       - Google ADK weather agent
    /openai-sdk/       - OpenAI Agents SDK weather agent
    /langgraph/        - LangGraph weather agent
    /crewai/           - CrewAI weather agent

Each agent exposes:
    GET  /.well-known/agent.json  - Agent card for discovery
    POST /                         - JSON-RPC 2.0 message handler

Usage:
    uvicorn server:app --host 0.0.0.0 --port 8000 --reload
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from a2a_wrapper import (
    generate_agent_card,
    parse_a2a_request,
    format_a2a_response,
    format_a2a_error,
)
from weather_utils import fetch_current_weather, fetch_weather_forecast

# Get host URL from environment (Railway sets this)
HOST_URL = os.getenv("HOST_URL", "http://localhost:8000")

# Agent configurations
AGENTS = {
    "ag2": {
        "name": "WeatherAgent-AG2",
        "description": "Weather agent built with AG2 (AutoGen) framework. Provides current weather and forecasts using the A2A protocol.",
        "framework": "AG2",
    },
    "google-adk": {
        "name": "WeatherAgent-GoogleADK",
        "description": "Weather agent built with Google's Agent Development Kit (ADK). Powered by Gemini models.",
        "framework": "Google ADK",
    },
    "openai-sdk": {
        "name": "WeatherAgent-OpenAI",
        "description": "Weather agent built with OpenAI's Agents SDK. Uses GPT models for natural language understanding.",
        "framework": "OpenAI Agents SDK",
    },
    "langgraph": {
        "name": "WeatherAgent-LangGraph",
        "description": "Weather agent built with LangChain's LangGraph framework. Implements a ReAct agent pattern.",
        "framework": "LangGraph",
    },
    "crewai": {
        "name": "WeatherAgent-CrewAI",
        "description": "Weather agent built with CrewAI framework. Designed for multi-agent task orchestration.",
        "framework": "CrewAI",
    },
}


# Agent handlers - each framework processes messages differently
async def handle_ag2_message(user_message: str) -> str:
    """Handle message using AG2 ConversableAgent."""
    try:
        from autogen import ConversableAgent, LLMConfig

        llm_config = LLMConfig({"model": "gpt-4o-mini"})

        agent = ConversableAgent(
            name="WeatherAgent",
            system_message="""You are a helpful weather assistant. Use the available tools
to fetch weather information. Always be clear about which city you're reporting on.""",
            llm_config=llm_config,
        )

        # Register tools
        agent.register_function(
            function_map={
                "get_current_weather": lambda city, country="": fetch_current_weather(city, country),
                "get_weather_forecast": lambda city, country="", days=3: fetch_weather_forecast(city, country, days),
            }
        )

        # Simple direct call - AG2 handles tool execution internally
        response = await asyncio.to_thread(
            agent.generate_reply,
            messages=[{"role": "user", "content": user_message}],
        )
        return response if isinstance(response, str) else str(response)
    except Exception as e:
        return f"Error with AG2 agent: {str(e)}"


async def handle_google_adk_message(user_message: str) -> str:
    """Handle message using Google ADK Agent."""
    try:
        # Google ADK requires Gemini API key
        if not os.getenv("GOOGLE_API_KEY"):
            return "Google ADK agent requires GOOGLE_API_KEY environment variable."

        from google.adk.agents import Agent
        from google.adk.runners import Runner

        def get_current_weather(city: str, country: str = "") -> dict:
            result = fetch_current_weather(city, country)
            if "Error" in result or "not found" in result:
                return {"status": "error", "error_message": result}
            return {"status": "success", "report": result}

        def get_weather_forecast(city: str, country: str = "", days: int = 3) -> dict:
            result = fetch_weather_forecast(city, country, days)
            if "Error" in result or "not found" in result:
                return {"status": "error", "error_message": result}
            return {"status": "success", "report": result}

        agent = Agent(
            name="weather_agent",
            model="gemini-2.0-flash",
            instruction="You are a helpful weather assistant.",
            tools=[get_current_weather, get_weather_forecast],
        )

        runner = Runner(agent=agent)
        response = await asyncio.to_thread(runner.run, user_message)
        return str(response)
    except ImportError:
        return "Google ADK not installed. Install with: pip install google-adk"
    except Exception as e:
        return f"Error with Google ADK agent: {str(e)}"


async def handle_openai_sdk_message(user_message: str) -> str:
    """Handle message using OpenAI Agents SDK."""
    try:
        from agents import Agent, Runner, function_tool

        @function_tool
        def get_current_weather(city: str, country: str = "") -> str:
            """Get current weather for a city."""
            return fetch_current_weather(city, country)

        @function_tool
        def get_weather_forecast(city: str, country: str = "", days: int = 3) -> str:
            """Get weather forecast for a city."""
            return fetch_weather_forecast(city, country, days)

        agent = Agent(
            name="WeatherAgent",
            instructions="You are a helpful weather assistant.",
            tools=[get_current_weather, get_weather_forecast],
            model="gpt-4o-mini",
        )

        result = await Runner.run(agent, user_message)
        return result.final_output
    except ImportError:
        return "OpenAI Agents SDK not installed. Install with: pip install openai-agents"
    except Exception as e:
        return f"Error with OpenAI SDK agent: {str(e)}"


async def handle_langgraph_message(user_message: str) -> str:
    """Handle message using LangGraph ReAct agent."""
    try:
        from langchain_core.tools import tool
        from langchain_openai import ChatOpenAI
        from langgraph.prebuilt import create_react_agent

        @tool
        def get_current_weather(city: str, country: str = "") -> str:
            """Get current weather for a city."""
            return fetch_current_weather(city, country)

        @tool
        def get_weather_forecast(city: str, country: str = "", days: int = 3) -> str:
            """Get weather forecast for a city."""
            return fetch_weather_forecast(city, country, days)

        model = ChatOpenAI(model="gpt-4o-mini")
        agent = create_react_agent(
            model,
            [get_current_weather, get_weather_forecast],
            prompt="You are a helpful weather assistant.",
        )

        result = await asyncio.to_thread(
            agent.invoke,
            {"messages": [{"role": "user", "content": user_message}]},
        )

        # Extract the last AI message
        for message in reversed(result.get("messages", [])):
            if hasattr(message, "content") and getattr(message, "type", None) == "ai":
                return message.content

        return "No response generated"
    except ImportError:
        return "LangGraph not installed. Install with: pip install langgraph langchain-openai"
    except Exception as e:
        return f"Error with LangGraph agent: {str(e)}"


async def handle_crewai_message(user_message: str) -> str:
    """Handle message using CrewAI agent."""
    try:
        from crewai import Agent, Task, Crew
        from crewai.tools import tool

        @tool("get_current_weather")
        def get_current_weather(city: str, country: str = "") -> str:
            """Get current weather for a city."""
            return fetch_current_weather(city, country)

        @tool("get_weather_forecast")
        def get_weather_forecast(city: str, country: str = "", days: int = 3) -> str:
            """Get weather forecast for a city."""
            return fetch_weather_forecast(city, country, days)

        weather_agent = Agent(
            role="Weather Assistant",
            goal="Provide accurate weather information for cities worldwide",
            backstory="You are a helpful weather assistant with access to real-time weather data.",
            tools=[get_current_weather, get_weather_forecast],
            verbose=False,
        )

        task = Task(
            description=f"Answer the following weather question: {user_message}",
            expected_output="A clear and helpful response about the weather",
            agent=weather_agent,
        )

        crew = Crew(
            agents=[weather_agent],
            tasks=[task],
            verbose=False,
        )

        result = await asyncio.to_thread(crew.kickoff)
        return str(result)
    except ImportError:
        return "CrewAI not installed. Install with: pip install crewai"
    except Exception as e:
        return f"Error with CrewAI agent: {str(e)}"


# Map agent names to handlers
AGENT_HANDLERS: dict[str, Callable] = {
    "ag2": handle_ag2_message,
    "google-adk": handle_google_adk_message,
    "openai-sdk": handle_openai_sdk_message,
    "langgraph": handle_langgraph_message,
    "crewai": handle_crewai_message,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print(f"Starting Weather Agent Server at {HOST_URL}")
    print(f"Available agents: {', '.join(AGENTS.keys())}")
    yield
    print("Shutting down Weather Agent Server")


app = FastAPI(
    title="Weather Agent Server",
    description="Unified server hosting weather agents built with multiple frameworks",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint listing all available agents."""
    return {
        "service": "Weather Agent Server",
        "agents": {
            name: {
                "card": f"{HOST_URL}/{name}/.well-known/agent.json",
                "endpoint": f"{HOST_URL}/{name}/",
                "framework": config["framework"],
            }
            for name, config in AGENTS.items()
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/{agent_name}/.well-known/agent.json")
async def get_agent_card(agent_name: str):
    """Return the A2A agent card for the specified agent."""
    if agent_name not in AGENTS:
        return JSONResponse(
            status_code=404,
            content={"error": f"Agent '{agent_name}' not found"},
        )

    config = AGENTS[agent_name]
    card = generate_agent_card(
        name=config["name"],
        description=config["description"],
        url=f"{HOST_URL}/{agent_name}/",
        framework=config["framework"],
    )
    return card


@app.post("/{agent_name}/")
async def handle_message(agent_name: str, request: Request):
    """Handle A2A JSON-RPC 2.0 message/send requests."""
    if agent_name not in AGENTS:
        return JSONResponse(
            status_code=404,
            content={"error": f"Agent '{agent_name}' not found"},
        )

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content=format_a2a_error("", -32700, "Parse error"),
        )

    # Parse the A2A request
    request_id, method, user_message, context_id = parse_a2a_request(body)

    # Validate method
    if method != "message/send":
        return JSONResponse(
            content=format_a2a_error(request_id, -32601, f"Method not found: {method}"),
        )

    # Validate message
    if not user_message:
        return JSONResponse(
            content=format_a2a_error(request_id, -32602, "Invalid params: no message text"),
        )

    # Get the handler for this agent
    handler = AGENT_HANDLERS.get(agent_name)
    if not handler:
        return JSONResponse(
            content=format_a2a_error(request_id, -32603, f"No handler for agent: {agent_name}"),
        )

    # Process the message
    try:
        agent_response = await handler(user_message)
        return format_a2a_response(
            request_id=request_id,
            context_id=context_id,
            user_message=user_message,
            agent_response=agent_response,
            status="completed",
        )
    except Exception as e:
        return format_a2a_response(
            request_id=request_id,
            context_id=context_id,
            user_message=user_message,
            agent_response=f"Error processing request: {str(e)}",
            status="failed",
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
