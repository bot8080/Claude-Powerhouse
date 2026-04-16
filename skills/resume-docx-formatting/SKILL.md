---
name: resume-docx-formatting
description: Generate professional, ATS-optimized resumes in DOCX format with consistent typography, color scheme, and layout. Use this skill whenever creating or formatting a resume as a .docx file, regardless of whose resume it is or what job it's for. Handles page dimensions, margins, fonts, colors, tab stops, bullets, headers, section layouts, and validation.
compatibility: Requires docx npm package v2.10.0+
---

# Resume DOCX Formatting Skill

A complete, reusable system for generating professional resumes in DOCX format. Extracted from proven Abhinav project implementation. Zero person-specific content — pure methodology and code templates.

---

## Overview

This skill provides:
- **DOCX constants** (page size, margins, fonts, colors)
- **Section templates** (name, contact, summary, skills, experience, education, certifications)
- **Code patterns** (TextRun, Paragraph, tab stops, borders, numbering)
- **Assembly workflow** (document order, validation, output)
- **Quality checklist** (before delivery)

All values are generalized. Adapt the content (names, companies, dates) for each person.

---

## DOCX Constants (Canonical — Synchronized with Abhinav Project)

These are the foundational settings for every resume. All measurements use the docx-js standard unit (twentieths of a point, commonly called DXA or twips in OOXML). 1 inch = 1440 units.

```javascript
// Page dimensions — US LETTER (MANDATORY — never use A4)
// CRITICAL: Always set these explicitly in the Document constructor.
// If omitted, docx-js may default to A4 (11906 x 16838), breaking tab alignment.
const PAGE_WIDTH = 12240;        // 8.5 inches
const PAGE_HEIGHT = 15840;       // 11 inches

// Margins — EXACT from Abhinav project
const MARGIN_TOP = 720;          // 0.5 inches
const MARGIN_BOTTOM = 720;       // 0.5 inches
const MARGIN_LEFT = 864;         // 0.6 inches
const MARGIN_RIGHT = 864;        // 0.6 inches

// Content width for tab stops (right-align position)
// Calculated: PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT = 12240 - 864 - 864 = 10512
const CONTENT_WIDTH = 10512;     // Position for right-aligned tab stops

// Typography (all in half-points)
const FONT = "Calibri";
const NAME_SIZE = 40;             // 20pt
const SECTION_HEADING_SIZE = 24;  // 12pt
const BODY_SIZE = 20;             // 10pt
const SMALL_SIZE = 18;            // 9pt

// Color palette (professional navy/steel blue)
// All hex values are strings WITHOUT the # prefix (docx-js requirement)
const COLOR_NAME = "1B3A6B";           // Navy — candidate name
const COLOR_SECTION_HEADING = "2E6DAD"; // Steel blue — section headings + border line
const COLOR_JOB_TITLE = "2C4A7C";      // Dark slate blue — job titles, degree names
const COLOR_COMPANY = "4A6FA5";        // Medium gray-blue — company/institution names
const COLOR_DATE = "555F6E";           // Cool gray — all dates (experience + education)
const COLOR_BODY = "1A1A1A";           // Near-black — body text + bold keywords
```

**Key Principle:** Both plain and bold text use `COLOR_BODY`. Bolding provides emphasis; color is reserved for structural elements (name, headings, titles, companies, dates).

---

## CRITICAL: Page Setup in Document Constructor

**Always set page size and margins explicitly.** If omitted, docx-js defaults to A4 paper with 1-inch margins, which makes `CONTENT_WIDTH` (10512) overflow the actual content area and pushes dates off the page.

```javascript
const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: {
          width: PAGE_WIDTH,    // 12240 — US Letter
          height: PAGE_HEIGHT,  // 15840 — US Letter
        },
        margin: {
          top: MARGIN_TOP,      // 720
          bottom: MARGIN_BOTTOM,// 720
          left: MARGIN_LEFT,    // 864
          right: MARGIN_RIGHT,  // 864
        },
      },
    },
    children: [/* paragraphs */],
  }],
  numbering: {
    config: [{
      reference: "resume-bullets",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "\u2022",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 180 } } },
      }],
    }],
  },
});
```

**Without this block, dates WILL overflow.** This is the single most common resume formatting failure.

---

## Spacing Constants

```javascript
// Section heading spacing
const SPACING_SECTION_BEFORE = 200;    // Before section heading
const SPACING_SECTION_AFTER = 80;      // After section heading border

// Summary/paragraph spacing
const SPACING_SUMMARY_AFTER = 80;      // After summary paragraph

// Job entry spacing
const SPACING_JOB_TITLE_BEFORE = 120;  // Before job title
const SPACING_JOB_COMPANY_AFTER = 40;  // After company line
const SPACING_BULLET_AFTER = 20;       // After each bullet

// Education spacing
const SPACING_EDUCATION_DEGREE_BEFORE = 120;  // Before degree line
```

---

## Section Templates

### 1. Candidate Name (Centered, Bold, Navy, Large)

```javascript
new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 40 },
  children: [
    new TextRun({
      text: "[CANDIDATE NAME]",
      bold: true,
      size: NAME_SIZE,
      font: FONT,
      color: COLOR_NAME,
    }),
  ],
})
```

**Notes:**
- Always centered
- Always bold and navy
- Spacing after: 40

---

### 2. Contact Line (Centered, Small, Pipe-Separated)

```javascript
new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 200 },
  children: [
    new TextRun({ text: "[LOCATION] | [PHONE] | [EMAIL] | ", size: SMALL_SIZE, font: FONT, color: COLOR_DATE }),
    new ExternalHyperlink({
      children: [new TextRun({ text: "[GITHUB URL]", style: "Hyperlink", size: SMALL_SIZE, font: FONT })],
      link: "[GITHUB LINK]",
    }),
  ],
})
```

**Notes:**
- GitHub is a hyperlink; all other text is plain
- Spacing after: 200
- Format: `City, Province | +1 XXX-XXX-XXXX | email@example.com | github.com/username`

---

### 3. Section Heading (Uppercase, Bold, Steel Blue, Bottom Border)

```javascript
function createSectionHeading(title) {
  return new Paragraph({
    spacing: { before: 200, after: 80 },
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 6, color: COLOR_SECTION_HEADING, space: 1 },
    },
    children: [
      new TextRun({
        text: title.toUpperCase(),
        bold: true,
        size: SECTION_HEADING_SIZE,
        font: FONT,
        color: COLOR_SECTION_HEADING,
      }),
    ],
  });
}
```

**Notes:**
- Always uppercase
- Always has bottom border
- Spacing: before 200, after 80
- Border: single line, size 6, space 1

---

### 4. Summary Paragraph (Plain + Bold Keywords)

```javascript
new Paragraph({
  spacing: { after: 80 },
  children: [
    new TextRun({ text: "Accomplished ", size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: "Full Stack Engineer", bold: true, size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: " with ", size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: "5+ years", bold: true, size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: " of experience...", size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
  ],
})
```

**Pattern:**
- 3-4 sentences max
- Split into TextRuns: plain, bold keyword, plain, bold keyword, etc.
- All TextRuns use `COLOR_BODY`
- Spacing after: 80

---

### 5. Skills Section (Category Bold, High-Priority Skills Bold)

```javascript
new Paragraph({
  spacing: { after: 40 },
  children: [
    new TextRun({ text: "Frontend: ", bold: true, size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: "React.js", bold: true, size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: ", ", size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: "TypeScript", bold: true, size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: ", JavaScript, HTML5, CSS3", size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
  ],
})
```

**Pattern:**
- One paragraph per skill category
- Category name (bold): `"Frontend: "`
- High-priority skills (bold): key technologies for JD
- Other skills (plain): comma-separated
- Spacing after: 40

---

### 6. Experience Entry (Two-Line Header + Bullets)

#### Line 1: Job Title + Date (Tab-Aligned Right)

```javascript
new Paragraph({
  spacing: { before: 120, after: 0 },
  tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_WIDTH }],
  children: [
    new TextRun({ text: "[JOB TITLE]", bold: true, size: BODY_SIZE, font: FONT, color: COLOR_JOB_TITLE }),
    new TextRun({ text: "\t", size: BODY_SIZE, font: FONT }),
    new TextRun({ text: "[START DATE] - [END DATE]", italics: true, size: BODY_SIZE, font: FONT, color: COLOR_DATE }),
  ],
})
```

**CRITICAL:** Tab stop is `TabStopType.RIGHT` at `position: CONTENT_WIDTH` (10512). This aligns dates to the far right margin. This ONLY works when page margins are set to 864 left/right in the Document constructor. If margins differ, dates will overflow or underflow.

#### Line 2: Company, Location

```javascript
new Paragraph({
  spacing: { before: 0, after: 40 },
  children: [
    new TextRun({ text: "[COMPANY], [LOCATION]", italics: true, size: BODY_SIZE, font: FONT, color: COLOR_COMPANY }),
  ],
})
```

#### Bullet Points

Define numbering config ONCE at document level (see Page Setup section above).

Then each bullet:

```javascript
new Paragraph({
  numbering: { reference: "resume-bullets", level: 0 },
  spacing: { after: 20 },
  children: [
    new TextRun({ text: "Developed", bold: true, size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: " backend APIs using ", size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: "Node.js", bold: true, size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
    new TextRun({ text: " and MongoDB.", size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
  ],
})
```

**Pattern:**
- Start with action verb (bold)
- Alternate plain and bold TextRuns
- End with quantified result
- Spacing after: 20

---

### 7. Education Entry (Two-Line Layout)

#### Line 1: Degree + Date (Tab-Aligned Right)

```javascript
new Paragraph({
  spacing: { before: 120, after: 0 },
  tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_WIDTH }],
  children: [
    new TextRun({ text: "[DEGREE NAME]", bold: true, size: BODY_SIZE, font: FONT, color: COLOR_JOB_TITLE }),
    new TextRun({ text: "\t", size: BODY_SIZE, font: FONT }),
    new TextRun({ text: "[YEAR]", italics: true, size: BODY_SIZE, font: FONT, color: COLOR_DATE }),
  ],
})
```

#### Line 2: Institution, Location, GPA

```javascript
new Paragraph({
  spacing: { before: 0, after: 40 },
  children: [
    new TextRun({ text: "[INSTITUTION], [LOCATION]", italics: true, size: BODY_SIZE, font: FONT, color: COLOR_COMPANY }),
    new TextRun({ text: " | GPA: [X.X]", size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
  ],
})
```

---

### 8. Certifications (Name + Number)

```javascript
new Paragraph({
  spacing: { before: 80, after: 0 },
  children: [
    new TextRun({ text: "[CERTIFICATION NAME]", bold: true, size: BODY_SIZE, font: FONT, color: COLOR_JOB_TITLE }),
  ],
})
new Paragraph({
  spacing: { before: 0, after: 40 },
  children: [
    new TextRun({ text: "Certification #: [NUMBER]", size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
  ],
})
```

---

### 9. References (Footer)

```javascript
new Paragraph({
  spacing: { before: 80 },
  children: [
    new TextRun({ text: "Available upon request", italics: true, size: BODY_SIZE, font: FONT, color: COLOR_BODY }),
  ],
})
```

---

## Document Assembly Order

Always assemble in this exact sequence:

1. Candidate name
2. Contact line
3. SUMMARY heading + summary paragraph
4. SKILLS heading + skill category paragraphs
5. EXPERIENCE heading + job entries
6. PROJECTS heading + project entries (if applicable)
7. EDUCATION heading + education entries
8. CERTIFICATIONS heading + certification entries
9. REFERENCES heading + line

---

## Critical DOCX Rules (Never Break)

### Layout & Structure
- **ALWAYS set page size and margins in the Document constructor** (see Page Setup section)
- Use tab stops: `TabStopType.RIGHT` at `position: CONTENT_WIDTH` (10512)
- Two-line headers: title + date line 1, company line 2
- Use `LevelFormat.BULLET` with numbering config (not raw Unicode)
- No tables for layout (ATS fails to parse)
- No images, logos, or graphics
- No headers/footers for contact (ATS skips them)
- Consistent paragraph spacing via `spacing: { before: X, after: Y }`

### Typography & Color
- Single font: Calibri throughout
- Vary via size, bold, italic, color only
- Bold keywords using `bold: true` on TextRun (requires splitting into multiple TextRuns)
- Body text and bold keywords both use `COLOR_BODY`
- Colors reserved for structure: name (navy), headings (steel blue), titles (dark slate blue), companies (gray-blue), dates (cool gray)
- All hex values are strings without `#` prefix

### Borders & Styling
- Section borders ONLY on section heading paragraphs
- Border: single line, size 6, steel blue color
- Never use table rows as dividers

---

## Validation Checklist

Before delivering any resume DOCX:

- [ ] Page size is US Letter (12240 x 15840) — NOT A4
- [ ] Page margins set explicitly (864 left/right, 720 top/bottom)
- [ ] All required sections present (Name, Contact, Summary, Skills, Experience, Education)
- [ ] All text is Calibri font
- [ ] Tab stops align dates to far right (position 10512)
- [ ] Section headings are uppercase with bottom borders
- [ ] Job/education entries use two-line format
- [ ] Bullets use proper numbering config
- [ ] All colors match the six defined constants
- [ ] No images, tables, headers, or footers
- [ ] Resume fits 1-2 pages
- [ ] Validation script passes

---

## Color Hex Reference (Copy-Paste)

```
Navy (name):              1B3A6B
Steel blue (section):     2E6DAD
Dark slate blue (titles): 2C4A7C
Medium gray-blue (co.):   4A6FA5
Cool gray (dates):        555F6E
Near-black (body):        1A1A1A
```

All hex strings: **no # prefix**, as strings (`"1B3A6B"` not `#1B3A6B`).

---

## Common Mistakes (Don't Do These)

- **Omit page size/margins in Document constructor** — causes A4 default + date overflow (most common failure)
- Hardcode colors inline — use named constants
- Use spaces/padding for date alignment — use tab stops
- Mix fonts or vary size inconsistently — single font (Calibri)
- Remove quantified metrics — preserve all numbers
- Use plain Unicode bullets — use numbering config
- Bold company names — only bold job titles and keywords
- Add images or logos — ATS fails to parse
- Use tab position 10080 when margins are 864 — CONTENT_WIDTH must be 10512 (12240 - 864 - 864)
- Use A4 page dimensions (11906 x 16838) — always US Letter (12240 x 15840)

---

## Support

This skill is methodology-only — pure templates and rules. Adapt the content (names, companies, dates, achievements) for each person. The formatting and structure never change. All values are synchronized with the Abhinav project's `knowledge_tailor_coverletter.md`.
