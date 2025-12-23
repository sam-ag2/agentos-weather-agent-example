"""
A2A Protocol Wrapper Utilities

Provides A2A (Agent-to-Agent) protocol support for non-AG2 agent frameworks.
Implements JSON-RPC 2.0 message handling and response formatting.
"""

import uuid
from datetime import datetime
from typing import Any


def generate_agent_card(
    name: str,
    description: str,
    url: str,
    framework: str,
    organization: str = "AG2 AI",
    version: str = "1.0.0",
) -> dict:
    """Generate an A2A-compatible agent card."""
    return {
        "name": name,
        "description": description,
        "url": url,
        "provider": {
            "organization": organization,
        },
        "version": version,
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
            "stateTransitionHistory": False,
        },
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain", "application/json"],
        "skills": [
            {
                "id": "current_weather",
                "name": "Current Weather",
                "description": f"Get real-time weather conditions for any city worldwide using {framework}.",
                "tags": ["weather", "current", "temperature", "conditions", framework.lower()],
                "examples": [
                    "What's the weather in Tokyo?",
                    "Current weather in London, UK",
                    "How hot is it in Dubai?",
                ],
            },
            {
                "id": "weather_forecast",
                "name": "Weather Forecast",
                "description": f"Get multi-day weather forecasts for any city using {framework}.",
                "tags": ["weather", "forecast", "prediction", "planning", framework.lower()],
                "examples": [
                    "What's the 5-day forecast for Paris?",
                    "Will it rain in Seattle this week?",
                    "7-day forecast for Sydney",
                ],
            },
        ],
    }


def parse_a2a_request(body: dict) -> tuple[str, str, str, str]:
    """
    Parse an A2A JSON-RPC 2.0 request.

    Returns:
        tuple: (request_id, method, user_message, context_id)
    """
    request_id = body.get("id", str(uuid.uuid4()))
    method = body.get("method", "")

    params = body.get("params", {})
    message = params.get("message", {})
    context_id = message.get("contextId", str(uuid.uuid4()))

    # Extract the user message from parts
    parts = message.get("parts", [])
    user_message = ""

    # Handle multi-turn conversations - get the last user message
    for part in reversed(parts):
        if part.get("kind") == "text":
            # Check metadata for role, default to user
            metadata = part.get("metadata", {})
            role = metadata.get("role", "user")
            if role == "user":
                user_message = part.get("text", "")
                break

    # Fallback: just get the first text part
    if not user_message and parts:
        for part in parts:
            if part.get("kind") == "text":
                user_message = part.get("text", "")
                break

    return request_id, method, user_message, context_id


def format_a2a_response(
    request_id: str,
    context_id: str,
    user_message: str,
    agent_response: str,
    status: str = "completed",
) -> dict:
    """
    Format a response in A2A protocol format.

    Args:
        request_id: The JSON-RPC request ID
        context_id: The conversation context ID
        user_message: The original user message
        agent_response: The agent's response text
        status: Task status (completed, failed, etc.)

    Returns:
        A2A-formatted JSON-RPC response
    """
    task_id = str(uuid.uuid4())
    user_msg_id = str(uuid.uuid4())
    agent_msg_id = str(uuid.uuid4())
    artifact_id = str(uuid.uuid4())

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "id": task_id,
            "contextId": context_id,
            "status": {
                "state": status,
            },
            "history": [
                {
                    "messageId": user_msg_id,
                    "role": "user",
                    "parts": [{"kind": "text", "text": user_message}],
                },
                {
                    "messageId": agent_msg_id,
                    "role": "agent",
                    "parts": [{"kind": "text", "text": agent_response}],
                },
            ],
            "artifacts": [
                {
                    "artifactId": artifact_id,
                    "parts": [{"kind": "text", "text": agent_response}],
                }
            ],
        },
    }


def format_a2a_error(
    request_id: str,
    error_code: int,
    error_message: str,
) -> dict:
    """Format an error response in A2A/JSON-RPC format."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": error_code,
            "message": error_message,
        },
    }
