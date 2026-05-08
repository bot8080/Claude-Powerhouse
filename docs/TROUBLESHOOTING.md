# Troubleshooting — MultiAgents-Powerhouse

Central troubleshooting guide for all components. Choose your error below.

## Quick Navigation

| Component | Most Common Error | Fix |
|-----------|------------------|-----|
| CLI (`npx powerhouse`) | `command not found` | Run `npm link` in repo root |
| `/pst` commands | `command not found` | Install Claude Code first |
| MCP: market-intelligence | Connection failed | Server not running |
| MCP: investment-brain | Analysis fails | Set `MARKET_INTELLIGENCE_CMD` |
| OpenCode Handoff | Auth failed | Run `opencode auth login` |
| Skills (Claude.ai) | Not triggering | Wrong trigger phrase |

---

## CLI (`npx powerhouse`)

```
npx powerhouse: command not found
```

**Cause:** The CLI is not linked globally.

**Fix:**
```bash
cd MultiAgents-Powerhouse
npm link
powerhouse --help    # Should work now
```

```
Error: Node.js 20+ required
```

**Fix:** Upgrade Node.js from [nodejs.org](https://nodejs.org).

---

## /pst Commands (Claude Code)

```
/pst: command not found
```

**Cause:** You're not in a Claude Code session.

**Fix:** These are Claude Code slash commands, not terminal commands. Run `claude` first, then type `/pst status` inside the Claude Code session.

```
/pst status: No BUILD_STATUS.md found
```

**Cause:** You ran `npx powerhouse init` or `npx powerhouse apply` successfully? The BUILD_STATUS.md should exist in the project root.

**Fix:** Run `npx powerhouse apply` from project root to create workflow files.

---

## MCP Servers

### market-intelligence

```
MCP tool call failed: connection refused
```

**Cause:** The market-intelligence server needs to be running in a separate terminal.

**Fix:**
```bash
cd MultiAgents-Powerhouse/mcps/market-intelligence
uv sync                  # First time only
uv run market-intelligence
```
Keep this terminal open. In Claude Desktop, restart the app.

```
resolve_tickers returned empty results
```

**Cause:** Yahoo Finance API may be temporarily unavailable, or ticker format is wrong.

**Fix:**
- Wait 2-3 minutes and retry
- Include the exchange suffix: `.NS` for NSE India, `.TO` for TSX Canada
- Check [Yahoo Finance status](https://status.yahoo.com/)

```
Rate limit errors on batch calls
```

**Fix:** Add 0.3s delay between calls. Already built into `get_batch_profiles` — just use it instead of individual calls.

### investment-brain

```
MARKET_INTELLIGENCE_CMD not found
```

**Cause:** The environment variable pointing to market-intelligence is not set.

**Fix:**
```bash
# Mac / Linux
export MARKET_INTELLIGENCE_CMD="uv run --directory /path/to/MultiAgents-Powerhouse/mcps/market-intelligence market-intelligence"

# Windows (PowerShell)
$env:MARKET_INTELLIGENCE_CMD = "uv run --directory C:\path\to\MultiAgents-Powerhouse\mcps\market-intelligence market-intelligence"
```

Add this to your shell profile (`.bashrc`, `.zshrc`, `$PROFILE`) to make it permanent.

```
yfinance rate limit exceeded
```

**Fix:** Without market-intelligence MCP, investment-brain falls back to yfinance which has rate limits. Wait 1 hour, or better: set `MARKET_INTELLIGENCE_CMD` to use the MCP data layer instead.

```
SQLite database is locked
```

**Fix:** Close other terminals that might have the database open. If persistent, delete `data/portfolio.db` (you'll lose portfolio data — export first with `python main.py export`).

---

## OpenCode Handoff

```
opencode: command not found
```

**Cause:** OpenCode CLI not installed.

**Fix:**
```bash
curl -fsSL https://opencode.ai/install | bash
opencode --version
```

```
OpenRouter auth failed / 401 Unauthorized
```

**Cause:** Your OpenRouter API key is missing or expired.

**Fix:**
```bash
opencode auth login
# Select: OpenRouter
# Paste your API key from https://openrouter.ai/keys
```

```
Worktree conflict: already exists
```

**Cause:** A previous dispatch left a stale worktree.

**Fix:**
```bash
git worktree prune
rm -rf .powerhouse/wt/*
```

```
Free tier exhausted (200 req/day limit)
```

**Options:**
- Wait for daily reset (next day UTC)
- Switch to paid `minimax-m2` model ($0.255/M input)
- Keep the task in Claude Code

---

## Skills (Claude.ai)

```
Skill not triggering
```

**Causes & fixes:**
| Cause | Fix |
|-------|-----|
| Wrong trigger phrase | Use exact phrases from the skill's README |
| Skill not installed | Claude.ai → Settings → Skills → Install Skill |
| CLI-only skill in web | Check `[CLI only]` vs `[CLI + Web]` badge in README |
| Description mismatch | Your request needs to match the skill's `description:` field |

```
Install Skill button shows error
```

**Fix:** Ensure you downloaded the `.skill` file (not `SKILL.md`). The `.skill` file has the correct YAML frontmatter format.

```
Skill content not loading or empty
```

**Fix:** Raw GitHub URLs work best. Try:
```
https://raw.githubusercontent.com/bot8080/MultiAgents-Powerhouse/main/skills/{skill-name}/{skill-name}.skill
```

---

## Getting Help

If your issue isn't listed here:

1. Search this file for error keywords
2. Check the component's `README.md` for component-specific docs
3. Open a [GitHub issue](https://github.com/bot8080/MultiAgents-Powerhouse/issues) with:
   - Component name and version
   - Full error message (screenshot helps)
   - OS and versions (Node, Python, Claude Code)
   - Steps to reproduce

---

*Related: [QUICKSTART.md](./QUICKSTART.md) | [CHEATSHEET.md](./CHEATSHEET.md)*
