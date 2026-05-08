# MultiAgents-Powerhouse Cheat Sheet

One-page reference for the most common commands and concepts.

---

## CLI — Scaffolding

| Command | What It Does |
|---------|--------------|
| `npx powerhouse init [name]` | Create new project (interactive) |
| `npx powerhouse apply` | Add workflow to existing project |
| `npx powerhouse --help` | Show all CLI options |

During `init`, you pick: **Stack** (Expo) → **Backend** (None/Firebase/Supabase) → **Payments** (No/Stripe) → **AI Workflow** (None/OpenCode)

> Not on npm — requires `npm link` from the cloned repo.

---

## /pst Commands — Agent Pipeline

Type these inside a **Claude Code** session:

```
/pst status           Current layer + next task
/pst plan "feature"   PM writes a ticket
/pst build            Dev implements the ticket
/pst review           QA validates the result
/pst branch name      Create feature branch
/pst pr               Type-check → push → create PR
/pst next             First unchecked task in project
```

---

## Agent Pipeline Flow

```
/pst plan → [Research?] → /pst build → /pst review → Human Approve → Merge
```

| Agent | Trigger | Job |
|-------|---------|-----|
| @advisor | `@advisor` | Quick help, brainstorming |
| PM Tech Lead | `/pst plan` | Writes ticket, checks spec-gate |
| Research Engineer | `/pst plan` (auto) | Investigates unfamiliar APIs |
| Dev Engineer | `/pst build` | Implements the ticket |
| QA Engineer | `/pst review` | 7-point validation |

---

## 7-Layer Build Order

| # | Layer | Example |
|---|-------|---------|
| 1 | Types & Constants | Interfaces, enums, config |
| 2 | Services | CRUD, auth, API clients |
| 3 | Context & Hooks | State, business logic |
| 4 | Base Components | Buttons, inputs, cards |
| 5 | Screens / Pages | Full routes |
| 6 | Backend Functions | Cloud functions, webhooks |
| 7 | Integration & Polish | Wire up, performance |

---

## Skills — Claude.ai

| Skill | Install | Trigger |
|-------|---------|---------|
| Software Team | [Download](../skills/Powerhouse-software-team/Powerhouse-software-team.skill) | "Set up AI dev team" |
| Project Setup Kit | [Download](../skills/Powerhouse-Claud-Project-Setup-Kit/Powerhouse-Claud-Project-Setup-Kit.skill) | "Audit my project" |
| Prompt Optimizer | [Download](../skills/Powerhouse-Prompt-Optimizer/Powerhouse-Prompt-Optimizer.skill) | "Improve this prompt" |
| Resume Specialist | [Download](../skills/Powerhouse-Resume-Specialist/Powerhouse-Resume-Specialist.skill) | "Format my resume" |

---

## MCP Servers

### market-intelligence

```bash
cd mcps/market-intelligence
uv sync                              # First time
uv run market-intelligence           # Start server
```

Available tools: `resolve_tickers` `get_full_profile` `get_batch_profiles` `get_technicals` `get_institutional_activity` `get_fii_dii_flows` `get_nifty_valuation` `get_scoring_data`

### investment-brain

```bash
cd mcps/investment-brain
pip install -r requirements.txt
python main.py analyze NVDA
python main.py screen --pe-max 25 --roe-min 15
python main.py paper-buy TSM 10 175 --stop-loss 158
python main.py portfolio
```

---

## Multi-Model Routing (OpenCode Go Plan)

| Agent | Model |
|-------|-------|
| PM Tech Lead | kimi-k2-0711 |
| Dev Engineer | deepseek-v4-pro |
| Worker-Mechanical | deepseek-v4-flash |
| QA Engineer | qwen3.6-plus |
| Research Engineer | qwen3.5-plus |
| Advisor | kimi-k2-0711 |

**Activate:** `cp opencode.go.json opencode.json`

---

## Session Recovery

After session clear, restore full context in 4 commands:

```bash
git branch --show-current          # Where am I?
git diff main...HEAD --stat        # What changed?
git diff main...HEAD               # Full diff
git status                         # Uncommitted work?
```

Then read `BUILD_STATUS.md`.

---

## Common Fixes

| Error | Fix |
|-------|-----|
| `npx powerhouse` not found | `npm link` in repo root |
| `/pst` not found | Start Claude Code first |
| MCP connection failed | Run server in separate terminal |
| Skill not triggering | Use exact phrases from README |
| OpenCode auth failed | `opencode auth login` |

Full troubleshooting: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
