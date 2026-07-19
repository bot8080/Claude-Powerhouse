# Claude-Powerhouse

**Stock analysis inside Claude, and an AI dev-team workflow for your projects.** Real Python MCP servers, installable Claude skills, and a spec-first agent pipeline — all source-only: clone and use, nothing to buy or publish.

| What | For | Go to |
|------|-----|-------|
| 📈 **2 MCP servers** — live stock data, technical analysis, and auto-scoring across US, India, and Canada | Claude Desktop + Claude Code | [`mcps/`](./mcps/) |
| 🧰 **4 skills** — PM→Dev→QA software team, project setup, prompt optimization, resume formatting | Claude.ai web + Claude Code | [`skills/`](./skills/) |

---

## Find your path

### 📈 "I want stock analysis inside Claude"

```bash
git clone https://github.com/bot8080/Claude-Powerhouse.git
cd Claude-Powerhouse/mcps/market-intelligence
uv sync && uv run market-intelligence
```

Then register the server in Claude Desktop and ask Claude things like *"Score NVDA and TSM and tell me which is the better buy."* Claude answers with live data: prices, fundamentals, RSI/MACD, insider activity, and a 100-point BUY/HOLD/SELL score.

Want auto-scoring, a screener, and paper trading on top? Add **investment-brain** — a local Python engine that does the heavy lifting and cuts Claude token usage by ~90%.

**→ [mcps/README.md](./mcps/README.md)** — which server you need, full install, Claude Desktop config.

### 🧰 "I want an AI dev team (or the other skills) in my Claude"

1. Pick a skill in [`skills/`](./skills/) and download its `.skill` file
2. Claude.ai → **Settings → Skills → Install Skill** → upload
3. Just ask — skills trigger automatically from what you say

| Skill | One-liner |
|-------|-----------|
| [Software Team](./skills/Powerhouse-software-team/) | PM plans → Dev builds → QA reviews, with specs and build-order gates *(Claude Code)* |
| [Project Setup Kit](./skills/Powerhouse-Claude-Project-Setup-Kit/) | Sets up or audits your Claude project instructions and knowledge base |
| [Prompt Optimizer](./skills/Powerhouse-Prompt-Optimizer/) | Turns vague prompts into professional-grade specifications |
| [Resume Specialist](./skills/Powerhouse-Resume-Specialist/) | ATS-safe, pixel-consistent DOCX resumes |

**→ [skills/README.md](./skills/README.md)** — install details per platform, troubleshooting.

### 💼 "I'm evaluating the engineering" (recruiters, reviewers)

The three things worth your time, in order:

1. **[market-intelligence](./mcps/market-intelligence/)** — a shipped FastMCP server: 8 tools, dynamic ticker resolution across 3 exchanges (no static symbol maps), batched profile fetching that collapses ~112 API calls into 1 MCP call, defensive error handling throughout. Start at [`src/market_intelligence/server.py`](./mcps/market-intelligence/src/market_intelligence/server.py).
2. **[investment-brain](./mcps/investment-brain/)** — a token-economics play: a local engine that pre-computes scoring/screening/portfolio state and hands Claude a 20–50-token prompt instead of ~3,500 tokens of raw data (~90% cheaper per analysis). SQLite persistence, rule-enforced paper trading, CLI + FastAPI UI.
3. **The process itself** — this repo was built with its own spec-first agent pipeline: every sub-project has a `TECH_SPEC.md` and layer-gated `BUILD_STATUS.md`; agent role definitions and the `/pst` command tooling live in [`.internal/`](./.internal/). The [Software Team skill](./skills/Powerhouse-software-team/) is that workflow, packaged for any project.

---

## Repo map

```
Claude-Powerhouse/
├── mcps/                  # MCP financial servers (Python)
│   ├── market-intelligence/   # Live data: 8 tools, 3 markets — shipped
│   └── investment-brain/      # Local scoring/screening/paper-trading engine — shipped
├── skills/                # 4 installable Claude skills (.skill + docs each)
├── docs/                  # Troubleshooting guide
└── .internal/             # Maintainer tooling: agent definitions, /pst commands, templates
```

## Documentation

| Read this | For |
|-----------|-----|
| [mcps/README.md](./mcps/README.md) | Which MCP server you need + full setup |
| [skills/README.md](./skills/README.md) | Skill install + usage per platform |
| [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) | Common errors across all components |
| [.internal/AGENTS.md](./.internal/AGENTS.md) | Agent pipeline + session protocol (maintainers) |
| [.internal/BUILD_STATUS.md](./.internal/BUILD_STATUS.md) | Development progress tracker (maintainers) |

## Contributing

PRs welcome — one change at a time merges fastest. Bug fixes, new MCP tools/markets, and skill improvements can go straight to PR; open a discussion first for structural changes.

## License

MIT — see [LICENSE](./LICENSE).

> Financial data is for informational purposes only. Always verify before making investment decisions.
