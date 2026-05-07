# OpenCode AI Setup Guide

## What This Addon Provides

This addon configures OpenCode AI multi-agent workflow for your project:
- **AGENTS.md** — System prompt with model routing and agent pipeline
- **Skills** — `dg` (command center), component/screen/service scaffolds
- **Hooks** — Branch name and commit message validation

## Prerequisites

1. OpenCode desktop app or CLI (https://opencode.ai)
2. An OpenCode API key

## AI Workflow Costs

| Mode | Tool | Cost | When to Use |
|------|------|------|-------------|
| Manual | None | $0 | Review your own code. Template still works. |
| Claude Desktop | Anthropic Pro | ~$20/mo | Single-agent assistance, no orchestration. |
| OpenCode Free | OpenCode API | $0 (158K Flash req/mo) | Full multi-agent pipeline for solo devs. |
| OpenCode Pro | OpenCode API | Paid tier | Teams needing higher quotas or Pro models. |

## Setup

1. Install OpenCode: `npm install -g @opencode-ai/cli`
2. Run: `opencode init` in your project
3. Or configure your OpenCode desktop app to point to this project

## How It Works

The template does not require an OpenCode API key to function. If you enable the AI agent addon, DeepSeek V4 Flash (158K req/mo free tier) is sufficient for a solo developer building full-time.

## Sample Quota Calculation

- 1 developer, 50 agent calls/day = ~1,500 req/mo
- Well under the 158K Flash limit
- Use Pro models selectively for architecture/debugging
