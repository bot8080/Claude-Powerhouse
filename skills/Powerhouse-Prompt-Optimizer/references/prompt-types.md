# Prompt Type Reference

## System Prompts (AI instruction / persona setup)

**Goal**: Define Claude's role, behavior, tone, constraints, and scope for an entire session.

**Key improvements to apply:**
- Always open with a role: "You are a [role] specializing in [domain]."
- Define the audience explicitly
- Set tone and communication style
- List what Claude should and should not do
- Use XML sections for long system prompts: <role>, <context>, <instructions>, <constraints>, <output_format>
- Add CoT instructions only if the use case involves complex reasoning by default

**Example structure:**
```
You are a [role] helping [audience] with [task domain].

<context>
[Background on the product/service/situation]
</context>

<instructions>
[Core behaviors and responsibilities]
</instructions>

<constraints>
[What to avoid, scope limits, tone rules]
</constraints>

<output_format>
[How responses should be structured]
</output_format>
```

---

## User-Facing Chat Prompts (one-off requests)

**Goal**: Get a specific, high-quality response to a single task.

**Key improvements to apply:**
- State the task in the first sentence
- Add context about who the output is for and what it will be used for
- Specify format, length, tone
- Add CoT if the task involves reasoning or decisions
- Keep XML tags minimal unless the prompt includes background data

**Common patterns:**
- "Draft a [format] for [audience] that [achieves X]. Keep it under [length]. Tone: [adjective]."
- "Analyze [topic]. Think step by step. Focus on [specific angle]. Present as [format]."

---

## API / Developer Prompts

**Goal**: Produce reliable, consistent, parseable output for programmatic use.

**Key improvements to apply:**
- Be extremely explicit about output format (JSON schema, field names, exact structure)
- Add prefill if tight format control is needed (e.g., start the assistant turn with `{`)
- Use XML tags heavily — they improve parsing reliability
- Specify what to do on edge cases or missing data
- Add a role that matches the technical context
- Chain prompts if the task has distinct steps (extraction → analysis → formatting)

**Key note on Claude 4.x**: These models follow instructions very precisely. If you want
"above and beyond" behavior (extra fields, richer output), ask for it explicitly.
