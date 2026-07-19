# MCP Servers

Financial intelligence servers for Claude Desktop and Claude Code.

> **You are here:** Home → MCP Servers

---

## What Are MCP Servers?

Model Context Protocol (MCP) servers connect Claude to external data sources. Once configured, Claude can call these tools directly in your conversation — no copy-pasting required.

---

## Available Servers

| Server | Data Source | Markets | Best For |
|--------|------------|---------|----------|
| [market-intelligence](./market-intelligence/) | Yahoo Finance + yfinance | US, India, Canada | Real-time stock data, technicals, scoring |
| [investment-brain](./investment-brain/) | market-intelligence MCP + yfinance | US, India, Canada | Auto-scoring, paper trading, portfolio tracking |

---

## Which Server Do I Need?

```
What do you want to do?
│
├── "Get stock data in Claude"
│   → market-intelligence (standalone, 9 tools)
│
├── "Analyze stocks with auto-scoring"
│   → investment-brain (uses market-intelligence as data layer)
│
└── "Full analysis + trading simulator"
    → Run BOTH together (see below)
```

**Just need stock data?** → market-intelligence alone is sufficient.

**Want scoring + portfolio tracking?** → investment-brain requires market-intelligence running alongside it.

---

## Quick Start

### market-intelligence (standalone)

```bash
cd mcps/market-intelligence
uv sync
uv run market-intelligence
```

### investment-brain (requires market-intelligence)

```bash
# Terminal 1 — Start data server
cd mcps/market-intelligence && uv run market-intelligence

# Terminal 2 — Set env var and run
export MARKET_INTELLIGENCE_CMD="uv run --directory /path/to/mcps/market-intelligence market-intelligence"
cd mcps/investment-brain
pip install -r requirements.txt
python main.py analyze NVDA
```

### Both in Claude Desktop

Config file location:
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "market-intelligence": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcps/market-intelligence", "market-intelligence"]
    },
    "investment-brain": {
      "command": "python",
      "args": ["/path/to/mcps/investment-brain/mcp_wrapper.py"],
      "env": {
        "MARKET_INTELLIGENCE_CMD": "uv run --directory /path/to/mcps/market-intelligence market-intelligence"
      }
    }
  }
}
```

On Windows, use backslash paths (`C:\\path\\to\\...`) and `set MARKET_INTELLIGENCE_CMD=...` in Command Prompt, or `$env:MARKET_INTELLIGENCE_CMD=...` in PowerShell.

---

## Documentation

| Server | Full Docs | Install | Troubleshooting |
|--------|-----------|---------|----------------|
| [market-intelligence](./market-intelligence/) | Tools, workflow, config | `uv sync && uv run` | [FAQ](./market-intelligence/README.md#troubleshooting) |
| [investment-brain](./investment-brain/) | Commands, architecture, deploy | `pip install -r requirements.txt` | [FAQ](./investment-brain/README.md#troubleshooting) |

---

← [Root README](../README.md) | [Skills](../skills/README.md) | [Troubleshooting](../docs/TROUBLESHOOTING.md)