# Software Team

A **complete AI software development team** skill — spec-first, layer-gated, and fully agent-driven. PM plans, Dev builds, QA reviews, all in one structured workflow.

> [!NOTE]
> AI-assisted projects often collapse into chaos: no specs, no build order, agents doing whatever they want. This skill enforces a **spec-first discipline** with hard gates between build layers and a four-agent pipeline that keeps every feature accountable.

---

## The Challenges This Solves

| The Issue (Before) ❌ | The Powerhouse Solution ✅ | The Result 🚀 |
| :--- | :--- | :--- |
| • Claude starts coding before requirements are clear<br>• No enforced order — Layer 5 built before Layer 2<br>• Token budget blown on re-explaining context each session<br>• No QA step — bugs slip into every PR | • Three anchor documents (TECH_SPEC, SCREEN_SPEC, BUILD_STATUS) written before any code<br>• Strict 7-layer gate: Layer N cannot start until N-1 is merged<br>• Four specialized agents (PM, Research, Dev, QA) with clear scope<br>• Git state + BUILD_STATUS used for context recovery | • **No Scope Creep**: Tickets are bounded — no more, no less.<br>• **Stable Builds**: Each layer is solid before the next begins.<br>• **Resilient Sessions**: Clear context with four git commands, no re-explaining. |

---

## Installation

1. Download [software-team.skill](./software-team.skill)
2. Open [Claude.ai](https://claude.ai) → **Settings** → **Skills**
3. Click **Install Skill** and upload the file

---

## How to Use

Say any of these to trigger the skill:

- *"Help me set up an AI software team for my project."*
- *"I want to structure my next app build with PM, Dev, and QA agents."*
- *"Let's start a complex project — set up the spec documents and build layers."*
- *"Create the anchor documents and agent pipeline for my new app."*

---

## What You Get

After the skill runs, your project has:

| Artifact | Purpose |
|----------|---------|
| `TECH_SPEC.md` | Data contract — schemas, service signatures |
| `SCREEN_SPEC.md` | UX contract — every screen before any UI |
| `BUILD_STATUS.md` | Checked-off progress tracker per layer |
| `.claude/agents/` | Four agent files: PM, Research, Dev, QA |
| `.claude/skills/[project]/SKILL.md` | Unified `/myapp` command skill |

---

## Contents

- `SKILL.md`: The full skill instructions — agent pipeline, build layers, session hygiene, context recovery.
- `software-team.skill`: The installable distributable.

---

*Part of the [Claude-Powerhouse](../../README.md) suite.*
