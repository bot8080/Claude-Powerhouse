# prompt-improver

A skill for Claude AI that rewrites and strengthens prompts using Anthropic's official prompt engineering methodologies.

> Not affiliated with or endorsed by Anthropic.

---

## What it does

Paste any prompt and ask Claude to improve it — the skill rewrites it and returns the improved version immediately, with no commentary or explanation. Just a better prompt, ready to use.

It applies Anthropic's methodology in order of impact:

1. Role assignment (for system prompts)
2. Explicit task statement
3. Context and motivation
4. XML structure (for multi-section prompts)
5. Chain-of-thought (for reasoning tasks)
6. Output format specification
7. Constraints and guardrails

Not all techniques apply to every prompt — the skill uses judgment based on what the prompt actually needs.

---

## Prompt types supported

- **System prompts** — AI persona/instruction setup
- **User-facing chat prompts** — one-off task requests
- **API / developer prompts** — structured output for programmatic use

---

## Installation

1. Download `prompt-improver.skill` from this folder
2. Open [Claude.ai](https://claude.ai)
3. Go to **Settings → Skills**
4. Click **Install Skill** and upload the `.skill` file

**Optional**: Upload `references/prompt-types.md` as a knowledge file in a Claude Project for richer type-specific guidance.

---

## Usage

Just paste your prompt and ask Claude to improve it. Triggers on phrases like:

- "improve this prompt"
- "rewrite this system prompt"
- "this prompt isn't working, can you fix it?"
- "make this more effective"
- "clean up my instructions"

---

## Files in this folder

| File | Purpose |
|---|---|
| `prompt-improver.skill` | The installable skill file |
| `references/prompt-types.md` | Reference guide on how improvement differs by prompt type (system / chat / API) |

---

## License

MIT — see [LICENSE](../LICENSE)
