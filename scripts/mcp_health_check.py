"""
MCP Server Health Checker
Checks if MCP servers are running and responsive.
Useful for Kubernetes readiness/liveness probes.
"""

import json
import sys
import subprocess
import argparse
from datetime import datetime


def check_mcp_server(server_name: str, server_command: str) -> dict:
    result = {
        "server": server_name,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "unknown",
        "details": {}
    }

    try:
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "health-checker",
                    "version": "1.0.0"
                }
            }
        }

        proc = subprocess.run(
            server_command.split(),
            input=json.dumps(init_request),
            capture_output=True,
            text=True,
            timeout=10
        )

        if proc.returncode == 0:
            result["status"] = "healthy"
            try:
                response = json.loads(proc.stdout)
                result["details"]["protocol_version"] = response.get(
                    "result", {}
                ).get("protocolVersion", "unknown")
            except json.JSONDecodeError:
                result["details"]["raw_output"] = proc.stdout[:200]
        else:
            result["status"] = "unhealthy"
            result["details"]["error"] = proc.stderr[:200]

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["details"]["error"] = "Server did not respond within 10s"
    except FileNotFoundError:
        result["status"] = "not_found"
        result["details"]["error"] = f"Command not found: {server_command}"
    except Exception as e:
        result["status"] = "error"
        result["details"]["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(description="MCP Server Health Checker")
    parser.add_argument("--name", type=str, help="Server name")
    parser.add_argument("--command", type=str, help="Server command")
    args = parser.parse_args()

    if args.name and args.command:
        result = check_mcp_server(args.name, args.command)
        print(json.dumps(result, indent=2))
        if result["status"] != "healthy":
            sys.exit(1)
    else:
        print("Usage: python mcp_health_check.py --name <name> --command <cmd>")
        sys.exit(1)


if __name__ == "__main__":
    main()