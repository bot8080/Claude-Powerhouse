#!/usr/bin/env python3
"""Investment Brain MCP Server (wraps the local engine for Claude).

This is the SERVER side: exposes investment-brain itself as an MCP server so
Claude can call `analyze_stock`, `screen_stocks`, etc. as tools directly.

Not to be confused with `mcp_bridge.py`, which is the CLIENT side that
investment-brain uses to fetch raw data from the market-intelligence MCP.

  mcp_wrapper.py : Claude → investment-brain (this file, server)
  mcp_bridge.py  : investment-brain → market-intelligence (client)
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Resolved relative to this file — works on any machine, any OS.
BRAIN_DIR = Path(__file__).resolve().parent
MAIN_PY = BRAIN_DIR / "main.py"


def run_brain(*args) -> dict:
    """Run main.py with --json and parse stdout as JSON.

    --json suppresses the human-readable preamble and emits one JSON blob
    per command. Falls back to {"raw": out} if JSON parse fails (e.g. an
    unexpected error message on stderr-only paths).
    """
    cmd = [sys.executable, str(MAIN_PY), "--json"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BRAIN_DIR, timeout=30)

    if result.returncode != 0:
        return {"error": result.stderr.strip() or result.stdout.strip()}

    out = result.stdout.strip()
    if not out:
        return {"error": "No output from main.py"}

    try:
        return json.loads(out)
    except json.JSONDecodeError:
        # main.py may have crashed mid-stream — return whatever we got.
        return {"error": "Non-JSON output", "raw": out}


server = Server("investment-brain")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="analyze_stock",
            description="Analyze a single stock. Returns scored data + raw fundamentals + technicals + news headlines.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "market": {"type": "string", "enum": ["US", "CA", "IN"], "default": "US"}
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="screen_stocks",
            description="Screen a universe of stocks by criteria. Returns ranked results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tickers": {"type": "array", "items": {"type": "string"}},
                    "pe_max": {"type": "number", "default": 25},
                    "roe_min": {"type": "number", "default": 15},
                    "sector": {"type": "string"}
                },
                "required": ["tickers"]
            }
        ),
        Tool(
            name="portfolio_review",
            description="Review current portfolio from SQLite DB.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="paper_trade",
            description="Execute a paper trade (BUY or SELL).",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["BUY", "SELL"]},
                    "ticker": {"type": "string"},
                    "shares": {"type": "number"},
                    "price": {"type": "number"}
                },
                "required": ["action", "ticker", "shares", "price"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "analyze_stock":
        result = run_brain("analyze", arguments["ticker"], "--market", arguments.get("market", "US"))
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "screen_stocks":
        args = ["screen", "--pe-max", str(arguments.get("pe_max", 25)), "--roe-min", str(arguments.get("roe_min", 15))]
        if arguments.get("sector"):
            args.extend(["--sector", arguments["sector"]])
        args.extend(arguments.get("tickers", []))
        result = run_brain(*args)
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "portfolio_review":
        result = run_brain("portfolio")
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "paper_trade":
        action = arguments["action"].lower()
        result = run_brain(f"paper-{action}", arguments["ticker"], str(arguments["shares"]), str(arguments["price"]))
        return [TextContent(type="text", text=json.dumps(result))]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# Updated Execution Block
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())