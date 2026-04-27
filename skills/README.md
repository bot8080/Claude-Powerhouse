# claude-skills

A personal collection of Claude AI skills — reusable, installable, and open source.

> Not affiliated with or endorsed by Anthropic.

---

## What are Claude Skills?

Claude Skills are instruction files (`.skill`) that extend Claude's behavior for specific tasks. Once installed in Claude.ai, they trigger automatically based on what you ask — no manual setup needed per conversation.

Think of them as plugins for Claude: each skill teaches Claude how to handle a specific domain or workflow better than it would by default.

---

## 🏮 The Challenges These Skills Solve

A detailed comparison of why these skills were built and the results they deliver.

### 🏠 1. Powerhouse-Claud-Project-Setup-Kit

| The Issue (Before) ❌ | The Powerhouse Solution ✅ | The Result 🚀 |
| :--- | :--- | :--- |
| • Bloated instructions wasting tokens<br>• Inconsistent agent behavior<br>• Claude ignoring uploaded knowledge base files<br>• Repetitive manual setup for every conversation | • Principles-based architecture (not rigid rules)<br>• Automatic RAG-optimized file structure<br>• Professional Audit & Improve workflows<br>• Intelligent context-aware triggering | • **Higher Logic Accuracy**: Instructions that actually stick.<br>• **Lower Token Cost**: Leaner prompts = more context window.<br>• **Consistent Performance**: Stable results across 50+ chats. |

### 🧠 2. Powerhouse-Prompt-Optimizer

| The Issue (Before) ❌ | The Powerhouse Solution ✅ | The Result 🚀 |
| :--- | :--- | :--- |
| • Vague or lazy "one-sentence" prompts<br>• Robotic, generic AI outputs<br>• Claude hallucinating or ignoring constraints<br>• No clear structure or XML tagging | • Expert Role & Context framing<br>• XML tagging for structural clarity<br>• Chain-of-Thought (CoT) reasoning injection<br>• Few-shot example implementation | • **Expert-Level Outputs**: AI that sounds like a specialist.<br>• **Zero Hallucination**: Precise adherence to hard constraints.<br>• **Ready-to-Use**: Prompts you can copy-paste into ANY model. |

### 📄 3. Powerhouse-Resume-Specialist

| The Issue (Before) ❌ | The Powerhouse Solution ✅ | The Result 🚀 |
| :--- | :--- | :--- |
| • AI messily formatting DOCX files<br>• Dates jumping or overflowing margins<br>• Unprofessional colors and inconsistent fonts<br>• Resumes being "rejected" by ATS scanners | • Exact US Letter margin/page constraints<br>• Strict professional navy/steel blue color palette<br>• Tab-stop alignment for perfect date positioning<br>• Clean typography (Calibri-only) for ATS parsing | • **Market-Ready Resumes**: 100% professional look.<br>• **Perfect Alignment**: Dates and text never skip. <br>• **ATS-Optimized**: Guaranteed readability for recruiters. |

### 🤖 4. software-team

| The Issue (Before) ❌ | The Powerhouse Solution ✅ | The Result 🚀 |
| :--- | :--- | :--- |
| • Claude starts coding before requirements are clear<br>• No enforced order — Layer 5 built before Layer 2<br>• Token budget blown on re-explaining context each session<br>• No QA step — bugs slip into every PR | • Three anchor documents (TECH_SPEC, SCREEN_SPEC, BUILD_STATUS) written before any code<br>• Strict 7-layer gate: Layer N cannot start until N-1 is merged<br>• Four specialized agents (PM, Research, Dev, QA) with clear scope<br>• Git state + BUILD_STATUS used for context recovery | • **No Scope Creep**: Tickets are bounded — no more, no less.<br>• **Stable Builds**: Each layer is solid before the next begins.<br>• **Resilient Sessions**: Clear context with four git commands, no re-explaining. |

---

## Skills in this repo

> **Target labels:** `[CLI]` = Claude Code terminal only. `[Both]` = Claude Code + Claude.ai web.

| Skill | Target | Description | Install |
|---|---|---|---|
| [software-team](./software-team/) | **CLI** | Complete AI dev team — spec-first, 7-layer build order, PM → Dev → QA pipeline. Use in Claude Code when building any product. | [Download](./software-team/software-team.skill) |
| [opencode-handoff](./opencode-handoff/) | **CLI** | Hand off mechanical coding to OpenCode + MiniMax M2 (free). Claude Code plans + reviews; OpenCode executes in an isolated git worktree. Auto-suggests when the task profile is mechanical. | [Download](./opencode-handoff/opencode-handoff.skill) |
| [Powerhouse-Claud-Project-Setup-Kit](./Powerhouse-Claud-Project-Setup-Kit/) | **Both** | Professional AI Workspace Architect — principles-based setup and project auditing v2 | [Download](./Powerhouse-Claud-Project-Setup-Kit/Powerhouse-Claud-Project-Setup-Kit.skill) |
| [Powerhouse-Prompt-Optimizer](./Powerhouse-Prompt-Optimizer/) | **Both** | Advanced Prompt Engineering Specialist v2 — strictly based on Anthropic 2025 heuristics | [Download](./Powerhouse-Prompt-Optimizer/Powerhouse-Prompt-Optimizer.skill) |
| [Powerhouse-Resume-Specialist](./Powerhouse-Resume-Specialist/) | **Both** | Premium Resume/CV specialist — handles professional structure and document formatting | [Download](./Powerhouse-Resume-Specialist/Powerhouse-Resume-Specialist.skill) |

---

## How to install a skill

1. Download the `.skill` file from the skill's folder
2. Open [Claude.ai](https://claude.ai)
3. Go to **Settings → Skills**
4. Click **Install Skill** and upload the `.skill` file
5. The skill is now active in all your Claude chats

---

## How skills work

Each skill has:
- A **trigger description** — Claude reads this to decide when to use the skill
- **Instructions** — what Claude should do when the skill activates
- Optionally: **knowledge files, scripts, or reference docs** bundled inside

Skills activate automatically when your request matches the trigger — you don't need to mention the skill by name.

---

## Requirements

- Claude.ai account (Free, Pro, or Team)
- Skills feature enabled in your account

---

## Contributing

Found a bug or want to improve a skill? PRs and issues are welcome.

If you want to submit your own skill:
- Follow the folder structure: `skill-name/SKILL.md` + `skill-name/skill-name.skill`
- Include a `README.md` inside the skill folder explaining what it does
- Open a PR with a short description of what the skill does and when it triggers

---

## License

MIT — see [LICENSE](./LICENSE)
