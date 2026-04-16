# Anti-Patterns in Claude Project Setup

## Overview

These are the most common ways Claude project setups fail in practice. Check this list before finalizing any project output in either CREATE or IMPROVE mode.

---

## The 7 Anti-Patterns

### 1. The Instruction Novel

**What it looks like**: Instructions over 1,200 words that try to cover every scenario.

**Why it fails**: Claude stops paying close attention to rules buried in long instruction sets. Important rules get diluted by trivial ones.

**Fix**: Keep instructions under 800 words. If a rule only applies to specific tasks, it belongs in the chat or a knowledge file, not in instructions.

---

### 2. Hardcoded Routing Maps

**What it looks like**: Listing every knowledge file in instructions with "when to use this file" trigger keywords and task-type mappings.

**Why it fails**: Claude Projects use RAG automatically — the retriever already handles this. Routing maps waste instruction tokens, fight against the retriever, and go stale every time files change.

**Fix**: Trust the RAG retriever. Make knowledge file titles and Overview sections descriptive enough that the retriever finds them reliably. Only add routing hints in instructions if testing proves a specific file is consistently missed.

---

### 3. Rule Inflation

**What it looks like**: Starting with 5 rules, then adding a new rule every time something goes slightly wrong, until there are 40 rules that contradict each other.

**Why it fails**: Compensating rules create conflicts. Claude cannot resolve contradictions gracefully, so it picks one and ignores the other.

**Fix**: When a rule is not working, rewrite it rather than adding a compensating rule. If a behavior keeps failing, the root cause is usually a vague or poorly framed rule, not a missing one.

---

### 4. Knowledge File Sprawl

**What it looks like**: Creating 12–15 tiny, narrow files when 4–5 well-organized ones would work better.

**Why it fails**: More files means more retrieval decisions and more chances for the wrong file to be pulled (or no file at all). The retriever works best with coherent, well-scoped files.

**Fix**: Group related content. A file covering "CELPIP Writing rubric and scoring" is better than three separate files for task types, scoring bands, and common errors.

---

### 5. Restating Claude's Defaults

**What it looks like**: Rules like "be helpful", "provide accurate information", "admit when you don't know", "be respectful."

**Why it fails**: Claude already does these things. Instruction space should change behavior from defaults, not restate them. Every word of defaults is a wasted token.

**Fix**: Run the "ignoring test" — if Claude would follow a rule without being told, cut it.

---

### 6. Over-Specifying Format

**What it looks like**: Detailed output templates for every possible response type, including exact section names, word counts, and formatting for routine answers.

**Why it fails**: Format over-specification makes instructions brittle. Edge cases that do not fit the template produce awkward output. Claude's default formatting judgment is generally good.

**Fix**: Specify format only where it genuinely matters — for example, a specific report structure that will be shared with stakeholders, or a command output format a downstream tool depends on. For everything else, let Claude decide.

---

### 7. Skipping the Test Step

**What it looks like**: Delivering files to the user and calling the project done without verifying it works with real prompts.

**Why it fails**: Instruction sets that look correct on paper frequently fail in practice. Retrieval misses, rule conflicts, and tone mismatches only surface during actual use.

**Fix**: Always provide 3–5 test prompts with the deliverable. A project that has not been tested is a guess. If the user reports unexpected behavior, treat that as the first iteration, not a failure.

---

## Quick Checklist

Before finalizing any output, verify:

- [ ] Instructions under 800 words?
- [ ] No routing maps hardcoded in instructions?
- [ ] No rules that compensate for other rules (rule inflation)?
- [ ] Knowledge files grouped coherently, not sprawled into tiny files?
- [ ] No rules restating Claude's default behaviors?
- [ ] Format specified only where it genuinely matters?
- [ ] Test prompts included in the deliverable?
