---
title: resume-tailor skill — Design Spec
date: 2026-07-01
status: draft (pending user review)
author: Jackson McInerney
supersedes: the API-architecture resume-tailor (Wizbehindthecurtain/resume-tailor) as the distributable form
---

# resume-tailor skill — Design Spec

## 1. Purpose & Goal

Repackage resume-tailor as a **portable skill** anyone can run inside their own
Claude Code or Codex — with **no API keys, no server, no external services**. The
host model performs all reasoning (analyze JD, select bullets, write prose, judge
semantic fit); three small Python scripts handle only what a language model can't do
reliably itself (produce a real `.docx`, compute a deterministic score, verify
traceability).

This is a fresh, clean package (`resume-tailor-skill`). It **ports the proven
deterministic core and ATS knowledge** from the existing API-architecture repo and
**drops** the API/agent/pipeline/CLI layers (the host model replaces them).

### Non-goals (YAGNI)
- No Anthropic API calls; no `ANTHROPIC_API_KEY`.
- No Firecrawl / scraping key — the host uses its own web tools.
- No auto-submission to job boards/ATSs.
- No deceptive techniques (hidden text, keyword stuffing) — out of scope, never build.
- No persistent server; scripts are stateless CLIs.

## 2. Success Criteria
- A brand-new user with only a resume can, inside their own Claude/Codex, get a
  tailored `resume.docx` + `score-report.md` without supplying any API key.
- First run with no corpus triggers an onboarding gate that seeds the brain from the
  user's resume and asks them to confirm before tailoring.
- The bundled ATS knowledge is present on install; the host uses it as the rubric.
- Every claim in the output traces to a corpus bullet (verified mechanically).
- The output DOCX survives parse-back: must-have keywords are recoverable (Stage 1).
- An ATS field preview shows the structured fields (name, title, dates, skills) a real
  parser would extract from the rendered DOCX, so the user sees "what the machine sees"
  (Stage 2, proxy).
- Works in both Claude Code and Codex from the same `SKILL.md` + scripts.

## 3. Architecture

A skill = `SKILL.md` (workflow + rubric as instructions the host follows) + three
stateless Python scripts + reference/template files. User data lives OUTSIDE the
skill, in the user's working directory.

### 3.1 Package layout
```
resume-tailor-skill/
├─ SKILL.md                      ← frontmatter (name, description) + the workflow graph
├─ references/
│  ├─ ats-optimization.md        ← cited ATS rubric (ported from research)
│  ├─ research-report.md         ← full research provenance (auditable)
│  └─ corpus-schema.md           ← corpus file format; drives BOTH seeding and tailoring
├─ templates/
│  └─ resume_template.md         ← default single-column template
├─ scripts/
│  ├─ render_docx.py             ← Markdown → single-column .docx  (+ --extract for parse-back)
│  ├─ score.py                   ← deterministic keyword coverage + weighted 0–100 score
│  ├─ check_traceability.py      ← flags any output bullet not grounded in the corpus
│  └─ ats_preview.py             ← Stage-2 proxy: spaCy field extraction (name/title/dates/skills)
├─ tests/                        ← pytest for the 3 scripts
├─ README.md                     ← per-host install (Claude Code & Codex) + manual smoke test
└─ (optional, later) plugin.json / marketplace  ← Claude Code plugin wrapper
```

### 3.2 User data (outside the skill, created on first run)
```
<user's job-search folder>/
├─ resume-brain/                 ← the user's corpus
│  ├─ profile.md
│  ├─ roles/<slug>.md
│  ├─ projects/<slug>.md
│  ├─ skills.md
│  ├─ education.md
│  └─ certifications.md
└─ applications/<company>-<date>/ ← resume.docx + score-report.md
```
The skill is read-only and shareable; all personal data + outputs live in the user's
own folder.

## 4. The SKILL.md Workflow

`SKILL.md` has skill frontmatter (`name: resume-tailor`; a `description` triggering on
"tailor my resume / apply to this job / ATS optimize my resume") followed by this
decision graph the host follows:

```
1. ONBOARDING GATE (every invocation)
   Does ./resume-brain/ exist with a valid profile.md?
   ├─ NO  → SEED FLOW (Section 6)
   └─ YES → continue
2. GATHER TARGET
   • Company URL → host web-fetches the site (products, stack, values). No Firecrawl.
   • Job description (pasted or URL)
3. ANALYZE  — host extracts must-haves, keywords (acronym+spellout), seniority,
              team priorities, guided by references/ats-optimization.md
4. SELECT   — host reads resume-brain/, picks best-matching bullets, tracking each
              pick's source file (provenance)
5. WRITE    — host composes resume Markdown on templates/resume_template.md,
              reverse-chronological, mirroring JD phrasing only for corpus-proven skills
6. SCORE + ITERATE
   • python scripts/score.py            → coverage %, must-have hit-rate, weighted score
   • python scripts/check_traceability.py → untraceable[] (BLOCKS if non-empty)
   • If score < target (default 85) and room remains: revise + re-score (cap 2 passes)
7. RENDER + VERIFY + REPORT
   • python scripts/render_docx.py → applications/<company>-<date>/resume.docx
   • Stage 1 parse-back: render → --extract → confirm must-have keywords survived
   • Stage 2 field preview: python scripts/ats_preview.py resume.docx →
     structured fields a parser would extract (name/title/dates/skills). Optionally
     also run on the user's original resume for a before/after comparison.
   • Write score-report.md (coverage, matches, honest gaps, ATS field preview)
```
Steps 3–5 are host reasoning; scripts are called only at 6–7.

## 5. The Three Scripts

Standalone CLIs, args/stdin → file or stdout JSON. Only dependency: `python-docx`.
Each stays pytest-covered.

### 5.1 `render_docx.py`
- `--in resume.md --out resume.docx` → single-column, standard headings, `MM/YYYY`
  dates, real text (no tables/images/text-boxes) per the rubric's parse-survival rules.
- `--extract resume.docx` → prints raw text (powers the parse-back check).
- Ported from the existing `render/docx.py` (already tested).

### 5.2 `score.py`
- Input JSON (stdin): `{resume_text, keywords[], must_haves[], semantic_match: 0..1}`.
- Computes literal keyword coverage % and must-have hit-rate by case-insensitive,
  acronym-aware string matching (no host subjectivity on the literal part). Host
  supplies only `semantic_match`.
- Output JSON: `{score, keyword_coverage, must_have_hit_rate, semantic_match,
  matched[], missing[]}`, weights **0.50 must-have / 0.30 keyword / 0.20 semantic**.
- Ported from `compute_score`, extended with the matching.

### 5.3 `check_traceability.py`
- Input: generated resume + `resume-brain/` path.
- For each substantive claim/bullet, checks it maps to a corpus bullet (fuzzy match on
  source text). Emits `{untraceable[]}`.
- The workflow treats non-empty `untraceable[]` as a **hard blocker** — the host must
  fix or drop the line. This preserves "never invent" when the host reasons freely.

### 5.4 `ats_preview.py` — Stage-2 field-extraction proxy
- **Tech:** spaCy (`en_core_web_sm` or larger) via a resume-parser layer (e.g.
  `pyresparser`), reading the rendered DOCX.
- `python scripts/ats_preview.py resume.docx` → JSON of the structured fields a real ATS
  parser would extract: name, contact, employers, titles, dates, and skills.
- **Purpose:** show the user "what the machine sees." Optionally run on the user's
  original resume too, for a before/after comparison of recognized skills/fields.
- **Honest labeling:** this is a *proxy* for the proprietary commercial engines
  (Sovren/Textkernel, HireAbility, Affinda) — which are closed-source and cannot be run
  locally. It approximates Stage-2 field extraction; it is not the real engine.
- **Non-blocking:** the preview informs the user; it does not gate completion (unlike
  traceability). A field the proxy fails to extract is a *signal* worth surfacing.

### 5.5 Why two verification stages
A real ATS parses in two stages, and the skill mirrors both:
- **Stage 1 — text extraction** (`render_docx.py --extract`): file → raw text. This is
  the layer where formatting kills resumes (columns, tables, images). Our check here is
  **real, not a proxy** — `python-docx` performs genuine text extraction, the same first
  step every parser must do.
- **Stage 2 — field extraction** (`ats_preview.py`): text → structured fields. This is
  the proprietary ML layer; we approximate it with an open spaCy parser as a preview.

Split principle: **code owns what must be exact** (DOCX bytes, keyword arithmetic,
traceability); **the host owns judgment** (bullet fit, phrasing, semantic match); the
**field preview is an informational proxy**, clearly labeled as such.

## 6. Corpus & Seeding Flow

Corpus format is unchanged from the proven build, ported as `references/corpus-schema.md`
(same doc the host reads for tailoring and writes for seeding):
- `profile.md` (name, contact, links, summary variants)
- `roles/<slug>.md` (`type/company/title/start/end/skills` frontmatter + `## Bullets`
  tagged `[metric:]` `[skills:]` + `## Context`)
- `projects/<slug>.md`, `skills.md`, `education.md`, `certifications.md`

Seeding flow (the onboarding gate, in detail):
1. Host asks for the resume (PDF path, file, or pasted text; hosts read PDFs directly).
2. Host parses it into corpus structure per `corpus-schema.md`, with hard rules:
   **only what's in the resume** (never invent), and **tag every bullet** with
   `[metric:]`/`[skills:]`.
3. Host writes files into `./resume-brain/`.
4. Host shows a summary (roles, bullet counts, skills) and asks the user to **confirm or
   correct**, flagging genuine gaps the resume didn't answer (e.g. missing degree/year).
5. On confirmation, proceeds to tailoring.

Enrichment is invited, not required — the brain is a living store the user can grow for
better tailoring, but they can tailor immediately with just the seed.

## 7. Truthfulness, Testing & Distribution

### Truthfulness (three layers, since reasoning moved to the host)
1. **Instruction** — SKILL.md + corpus-schema.md state "only what's in the corpus, never
   invent" at both seed and write steps.
2. **Verification** — `check_traceability.py` mechanically flags un-grounded output; a
   non-empty result blocks completion.
3. **Honest gaps** — JD wants what the corpus can't prove → reported in `score-report.md`
   as a gap, never fabricated.

### Testing
- Scripts pytest-covered: render + parse-back keyword survival; score weight math +
  keyword matching; traceability detection of a planted un-grounded claim; and
  `ats_preview.py` extracting expected fields from a known DOCX (skipped cleanly if
  spaCy/model absent, so the core suite runs without the heavy dependency).
- Skill workflow: a documented **manual smoke test** in README.md — tiny sample corpus +
  JD, run end-to-end in a real host, confirm DOCX + report land and traceability passes.
  (Workflow instructions can't be unit-tested; this is the acceptance check.)

### Distribution ("anyone can run on Claude or Codex")
- Portable skill is the primary artifact — drop `resume-tailor-skill/` into a skills dir;
  both hosts load `SKILL.md` + scripts.
- README.md: per-host install + the one dependency (`pip install python-docx`).
- Optional later: thin Claude Code plugin wrapper (`plugin.json` + marketplace) for
  one-click install — additive, doesn't change the skill.

### Ported vs dropped
- **Ported** (proven, reused): ATS rubric + research report, `render/docx.py` →
  `render_docx.py`, `compute_score` → `score.py` core, corpus schema, template.
- **Dropped** (host replaces): `llm.py`, the API-calling agents, `pipeline.py`, `cli.py`,
  the corpus loader/importer as Python (host reads Markdown directly).

## 8. Build Order (slices)
1. Scaffold repo + port ATS rubric/research/template/corpus-schema into `references/`.
2. `render_docx.py` + parse-back tests (port + verify).
3. `score.py` + tests (keyword matching + weighted math).
4. `check_traceability.py` + tests (planted un-grounded claim).
5. `ats_preview.py` + tests (spaCy field extraction; tests skip if model absent).
6. `SKILL.md` — onboarding gate + tailoring workflow + rubric + Stage-1/Stage-2 verify.
7. README (per-host install incl. spaCy model step + manual smoke test); run it.
8. (Optional) plugin wrapper for Claude Code distribution.
