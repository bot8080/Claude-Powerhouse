# Quota & Fallback

OpenRouter free-tier limits, the dispatcher's quota guard, and the paid-fallback economics.

---

## OpenRouter free tier — `minimax-m2:free`

| Metric | Limit |
|---|---|
| Rate (per minute) | ~20 requests |
| Rate (per day) | ~200 requests |
| Context window | 204,800 tokens |
| Max output | up to 196,608 tokens (model-side) |
| Tool calling | Supported |
| Reasoning | Supported (`reasoning_details` between turns) |
| Cost | $0 |

**Important nuance.** The 200 RPD is shared across **all OpenRouter free models** on your account, not per-model. If you also use other free models (e.g. free Llama), they all draw from the same 200 RPD pool.

A single OpenCode dispatch typically issues **5–30 model requests** depending on:

- How many file reads OC does to ground itself
- How many edit/write operations
- Whether OC re-reads to verify acceptance criteria

So with ~200 RPD, expect **~10–30 dispatches per day** comfortably.

---

## Dispatcher's quota guard

The dispatcher inspects the **last 24h of `.powerhouse/dispatch-log.md`** before each new dispatch and estimates remaining requests.

```
Estimated requests used in last 24h = sum of "requests" column from log entries within 24h
Estimated remaining = 200 - used
```

| Estimated remaining | Action |
|---|---|
| > 30 RPD | Proceed silently |
| 10–30 RPD | **Warn**: print remaining quota, ask user to confirm |
| < 10 RPD | **Refuse** by default; offer fallback options |

The estimate is approximate — OpenRouter doesn't expose a per-account quota endpoint. Treat the log-based count as a lower bound.

---

## Paid fallback — `minimax-m2`

When the free tier is exhausted, the dispatcher offers the paid version of the same model on OpenRouter:

| Field | Value |
|---|---|
| Model | `openrouter/minimax/minimax-m2` |
| Input | $0.255 / M tokens |
| Output | $1.00 / M tokens |
| Context | 204k tokens |
| Quality | Same model, no rate-limit pool |

### Cost comparison per typical dispatch

A "typical" mechanical coding dispatch uses ~10k input tokens (ticket + read files) and ~5k output tokens (edits + completion JSON):

| Model | Input cost | Output cost | Total |
|---|---|---|---|
| Claude Opus 4.7 (CC) | ~$0.150 | ~$0.375 | **~$0.525** |
| Claude Sonnet 4.6 (CC) | ~$0.030 | ~$0.075 | **~$0.105** |
| MiniMax M2 paid | ~$0.0026 | ~$0.0050 | **~$0.0076** |
| MiniMax M2 free | $0 | $0 | **$0** |

So:
- Free → paid M2: still **~14× cheaper** than Sonnet, **~70× cheaper** than Opus.
- Paid M2 is a very acceptable fallback. The dispatcher should default to offering it.

### Fallback UX (the dispatcher must implement)

When free-tier remaining is < 10 RPD, the dispatcher prints:

```
Free-tier quota low (estimated 7 RPD remaining of ~200).
Options:
  1. Switch to paid minimax-m2 (~$0.008 per dispatch). Cheap and same model.
  2. Wait for daily reset (~14h from now).
  3. Run this ticket in Claude Code instead (uses your CC tokens).
What would you like to do?
```

The user must explicitly pick option 1, 2, or 3 — never default-switch.

---

## Other fallback providers (manual, not auto)

If you want to wire a different MiniMax provider, valid alternatives:

| Provider | Endpoint | Notes |
|---|---|---|
| MiniMax direct | `https://api.minimax.io/anthropic/v1` | Anthropic-compatible. Needs `MINIMAX_API_KEY`. May offer separate free credits via the [Token Plan](https://platform.minimax.io/docs/token-plan/opencode). |
| Novita | OpenRouter routing tag | Sometimes faster than the default OpenRouter pool |
| Local vLLM | self-hosted | For air-gapped use; needs ~256GB VRAM at FP8 |

To switch, edit the `model:` field in the ticket's frontmatter before dispatch — the dispatcher passes it to `opencode run --model` verbatim.

---

## Rough monthly economics

If you do **10 dispatches/day for 30 days**:

| Strategy | Monthly cost |
|---|---|
| All on Claude Opus (no handoff) | ~$157 |
| All on Sonnet (no handoff) | ~$31 |
| Plan + review on Sonnet, dispatch to free M2 | ~$5–10 (CC plan + review only) |
| Plan + review on Sonnet, dispatch to paid M2 (after quota) | ~$7–15 |

Token savings compound. The skill is a pure win on cost as long as the QA Engineer catches OC's mistakes — which is exactly what the existing `qa-engineer.md` checklist does.
