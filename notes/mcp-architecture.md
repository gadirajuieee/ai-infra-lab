# MCP (Model Context Protocol) — Architecture Notes

## What is MCP?

MCP is an open protocol that standardizes how AI applications connect to
external data sources and tools. Think of it as a USB-C port for AI agents.

## Core Components

### 1. MCP Host
The AI application (e.g., Claude Desktop, IDE plugin) that initiates connections.

### 2. MCP Client
Maintains a 1:1 connection with an MCP server. Handles protocol communication.

### 3. MCP Server
Lightweight service that exposes:
- **Resources** — Data the AI can read (files, DB records, API responses)
- **Tools** — Functions the AI can call (create ticket, send email, query DB)
- **Prompts** — Reusable prompt templates

## Communication Flow

Host (Claude) → Client → Server → External Service (GitHub, Slack, DB)

## Why It Matters for AI Infra

1. **Standardization** — One protocol instead of custom integrations per tool
2. **Security** — Servers run locally, data doesn't need to leave your infra
3. **Composability** — Mix and match servers for different capabilities
4. **Scalability** — Deploy servers as microservices on Kubernetes

## Deployment Patterns on Kubernetes

- Sidecar pattern: MCP server as sidecar to the AI agent pod
- Service mesh: MCP servers as independent services
- Gateway: Central MCP gateway routing to multiple backends

## Resources

- [MCP Specification](https://modelcontextprotocol.io)
- [MCP GitHub](https://github.com/modelcontextprotocol)