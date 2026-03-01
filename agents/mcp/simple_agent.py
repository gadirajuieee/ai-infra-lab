"""
Simple AI Agent with Tool Use
Demonstrates the pattern of an LLM agent that can call external tools
via MCP (Model Context Protocol).
"""

import json
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Tool:
    """A tool the agent can use. In MCP, these come from MCP servers."""
    name: str
    description: str
    parameters: dict
    function: Callable

    def to_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


@dataclass
class AgentMessage:
    """A message in the conversation."""
    role: str
    content: str
    tool_name: str = None
    tool_result: str = None


class SimpleAgent:
    """
    AI agent that decides which tool to call based on user message.
    In production, replace keyword matching with actual LLM call.
    """

    def __init__(self, name: str = "AI Assistant"):
        self.name = name
        self.tools: dict[str, Tool] = {}
        self.history: list[AgentMessage] = []
        self.max_iterations = 5

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool
        print(f"[{self.name}] Registered tool: {tool.name}")

    def get_available_tools(self) -> list[dict]:
        return [tool.to_schema() for tool in self.tools.values()]

    def execute_tool(self, tool_name: str, arguments: dict) -> str:
        if tool_name not in self.tools:
            return json.dumps({"error": f"Tool '{tool_name}' not found"})
        tool = self.tools[tool_name]
        try:
            result = tool.function(**arguments)
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def process_message(self, user_message: str) -> str:
        self.history.append(AgentMessage(role="user", content=user_message))

        for tool_name, tool in self.tools.items():
            if tool_name.lower() in user_message.lower():
                print(f"[{self.name}] Calling tool: {tool_name}")
                result = self.execute_tool(tool_name, {"query": user_message})
                self.history.append(AgentMessage(
                    role="tool", content=result,
                    tool_name=tool_name, tool_result=result
                ))
                response = f"I used the {tool_name} tool. Result: {result}"
                self.history.append(AgentMessage(role="assistant", content=response))
                return response

        response = f"I received your message: '{user_message}'. No tools were needed."
        self.history.append(AgentMessage(role="assistant", content=response))
        return response


def search_kubernetes(query: str) -> dict:
    """Simulate searching Kubernetes cluster."""
    return {
        "pods": ["vllm-server-abc123", "redis-cache-def456"],
        "status": "all healthy",
        "namespace": "ai-serving"
    }


def check_gpu_status(query: str) -> dict:
    """Simulate checking GPU status."""
    return {
        "gpu_count": 2,
        "gpu_type": "NVIDIA A100",
        "memory_used": "14.2 GB / 80 GB",
        "utilization": "67%"
    }


def query_metrics(query: str) -> dict:
    """Simulate querying application metrics."""
    return {
        "requests_per_second": 45,
        "avg_latency_ms": 230,
        "error_rate": "0.1%",
        "uptime": "99.97%"
    }


if __name__ == "__main__":
    agent = SimpleAgent(name="InfraBot")

    agent.register_tool(Tool(
        name="kubernetes",
        description="Search and manage Kubernetes resources",
        parameters={"query": {"type": "string"}},
        function=search_kubernetes
    ))

    agent.register_tool(Tool(
        name="gpu",
        description="Check GPU status and utilization",
        parameters={"query": {"type": "string"}},
        function=check_gpu_status
    ))

    agent.register_tool(Tool(
        name="metrics",
        description="Query application metrics and performance",
        parameters={"query": {"type": "string"}},
        function=query_metrics
    ))

    print("\n--- Agent Demo ---\n")
    print(agent.process_message("Check kubernetes pod status"))
    print()
    print(agent.process_message("What is the gpu utilization?"))
    print()
    print(agent.process_message("Show me the metrics dashboard"))
    print()
    print(agent.process_message("Hello, how are you?"))