# Powerhouse Resume Specialist

> **[CLI + Web]** — Works in Claude Code and Claude.ai

Generates and formats pixel-perfect, **ATS-optimized resumes** in `.docx` format.

> [!CAUTION]
> AI-generated Word documents often have broken margins, jumping dates, and unreadable tables. This skill enforces a **strict layout blueprint** so your resume looks professional to both humans and ATS scanners.

---

## What It Fixes

| Before ❌ | After ✅ |
|-----------|---------|
| Dates misaligned (spaces instead of tabs) | Perfect right-aligned tab stops |
| Left margin: 1.2" (too wide) | 0.5" - 0.6" US Letter standard |
| Font: "Arial Narrow" (ATS misreads) | Calibri only (100% ATS safe) |
| Bright blue + gray (unprofessional) | Navy (#001f3f) / Steel Blue (#4682B4) |
| Tables for layout (ATS rejects) | Pure semantic DOCX (no tables) |

---

## Professional Standard

| Specification | Value | Why |
|--------------|-------|-----|
| Margins | 0.5" - 0.6" all sides | US Letter standard |
| Font (body) | Calibri 11pt | ATS systems parse reliably |
| Font (headers) | Calibri 14pt bold | Clear hierarchy |
| Colors | Navy + Steel Blue | Prints in grayscale, professional |
| Date alignment | Right-aligned tab stops | Never jumps or overflows |
| Structure | Summary → Experience → Education → Skills | Standard US order |
| Layout | Zero tables, zero images | ATS-friendly |

---

## How to Use

**Trigger phrases:**
- *"Format my resume into a professional DOCX file"*
- *"Optimize my CV for an ATS scanner using the Powerhouse blueprint"*
- *"Help me rewrite my summary and generate a formatted Word doc"*

**What to provide (minimum):**
```
- Name and contact info
- 2-3 recent jobs (title, company, dates, 3-5 bullets each)
- Education (degree, school, year)
- Skills (technical + soft)
```

**For best results, also include:**
- Target role / industry
- Key achievements with metrics
- Summary / objective preference

---

## Installation

**Claude.ai web:**
1. Download [Powerhouse-Resume-Specialist.skill](./Powerhouse-Resume-Specialist.skill)
2. Go to [Claude.ai](https://claude.ai) → **Settings** → **Skills**
3. Click **Install Skill** and upload the file

**Claude Code:** Skills in `.claude/skills/` activate automatically when working in this repo.

---

## Contents

- `SKILL.md` — Complete technical blueprint (colors, margins, spacing, templates)
- `Powerhouse-Resume-Specialist.skill` — Installable distributable

---

## Related

| Skill | Purpose |
|-------|---------|
| [Prompt Optimizer](../Powerhouse-Prompt-Optimizer/) | Optimize job application cover letters |
| [Project Setup Kit](../Powerhouse-Claud-Project-Setup-Kit/) | Set up job search tracker |

---

*Part of the [Claude-Powerhouse](../../README.md) suite.*
