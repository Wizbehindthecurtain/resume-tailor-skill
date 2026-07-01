---
title: How resume-tailor Works — The ATS Knowledge Base
date: 2026-07-01
audience: anyone who wants to understand what the skill "knows" and why its output ranks
status: reference
---

# How resume-tailor Works — The ATS Knowledge Base

This document explains the domain knowledge the skill is built on: how modern
Applicant Tracking Systems (ATS) actually parse and rank resumes, where that
knowledge came from, and how the skill turns it into a resume that surfaces.

> **One-line summary:** An ATS is two systems — a *parser* that turns your file into
> structured fields, and a *matcher* that ranks you against the job. Most resumes die
> at the parser. The skill optimizes for both, grounded in how the dominant parsing
> engines actually behave — not generic "resume tips."

---

## 1. Where this knowledge came from

The ATS knowledge is not folklore or blog advice. It was produced by an
**adversarially-verified deep-research run** and distilled into the skill's bundled
rubric (`references/ats-optimization.md`), with full provenance in
`references/research-report.md`.

The research pipeline:

- **6 search angles** over the ATS/recruiting-software landscape (core systems,
  market share, pricing, the AI screening layer, stack architecture, practitioner
  adoption).
- **27 sources fetched → 117 candidate claims extracted.**
- **Top 25 claims verified by a 3-vote adversarial panel** (a claim needed 2 of 3
  "refute" votes to be killed).
- **17 claims confirmed, 8 killed.** Only the confirmed, durable mechanics were
  encoded into the skill; the killed claims are recorded so they are never
  re-introduced.

**Honesty about the sources.** Much of the *adoption/impact* data (e.g. "78% of
high-growth firms use AI embedded in their ATS") traces to a single vendor-published
survey — Bullhorn's GRID report — and is correlational and commercially interested.
The skill therefore encodes only the **durable parsing/matching mechanics**, which are
independently corroborated, and deliberately excludes the soft survey statistics from
its ranking logic.

---

## 2. The modern ATS landscape (what the research found)

### 2.1 The market is concentrated, and engines are shared
- For third-party staffing/recruiting agencies, **Bullhorn is the dominant system of
  record** — roughly **34–50% share**, 10,000+ agencies. (In the broader corporate
  market the leaders are different — Workday, iCIMS, Oracle, Greenhouse — but that is
  a separate segment.)
- Critically, **agency ATSs and many corporate ATSs license the same parsing
  engines** — Sovren/Textkernel, HireAbility, Affinda. This is the single most
  important fact for optimization: **you are not optimizing for a brand, you are
  optimizing for a parsing engine**, and a handful of engines cover most of the market.

### 2.2 AI screening now lives *inside* the ATS
- Matching/screening is increasingly delivered as a layer inside the core ATS rather
  than as separate tools — e.g. Bullhorn's Amplify suite (its **Match** "digital
  worker" surfaces and ranks candidates with **AI-driven relevancy scores**), and
  comparable built-ins in Gem, SmartRecruiters (Winston), Manatal, and Recruit CRM
  ("bimetric scoring").
- Practical implication: a resume is scored by an **automated relevancy model** before
  (or alongside) a human ever reads it, and that model rewards literal coverage first.

### 2.3 What was *refuted* (and excluded)
Claims the research panel killed — and which the skill does **not** rely on — include:
AI screening producing "measured" KPI gains (the figures were self-reported
perceptions only); "Workday leads / Bullhorn emerging" framing; specific vendor
launch-impact stats; a clean temp-vs-perm tool split; and "AI interviewing is almost
universally via ATS integration." Excluding these keeps the skill grounded.

---

## 3. How an ATS actually processes your resume

### 3.1 The parser (where most resumes die)
Your file is first converted to text and mapped to a **structured schema** — name,
contact, a list of `{employer, title, start, end}` work entries, a skills list,
education. Parsers reliably choke on:

- Multi-column layouts (text is read in the wrong order or merged).
- Tables, text boxes, and content inside headers/footers.
- Text baked into images or graphics (invisible to the parser).
- Non-standard section headings (the parser can't find "Work Experience").
- Fancy date formats and merged "Company · Title · Date" blobs.

If parsing fails, you are never scored — you're simply mis-filed or dropped. This is
why the skill's **parse-survival formatting rules** are non-negotiable.

### 3.2 The matcher / ranker
Once parsed, you are scored against the job. The research shows the weighting is
**keyword-literal first, semantic second**:

1. **Literal must-have-skill coverage** — does the resume contain the job's required
   skills, verbatim? (dominant signal)
2. **Keyword coverage** — how many of the job description's exact terms appear?
3. **Semantic similarity** — embedding-based "close enough" matching (a secondary,
   newer layer).

Recruiters also **search** the candidate database with Boolean/keyword queries
(`("project manager" OR "program manager") AND PMP`), so surfacing in search results
matters as much as passing an auto-gate — and that, too, is literal.

### 3.3 Can we test against the real engines? (Honest answer: no — so we use proxies)
The dominant engines — **Sovren/Textkernel** (Sovren was acquired by Textkernel, now
part of Bullhorn), **HireAbility**, and **Affinda** — are **proprietary, closed-source
cloud/API products**. None can be `pip install`-ed and run locally, so a keyless local
skill cannot execute *their* code. What we can do is verify each of the two stages with
open tooling:

- **Stage 1 (text extraction)** — replicable with open libraries and used as a **real**
  check: `python-docx` for DOCX (`render_docx.py --extract`), and Apache Tika / pdfplumber
  / PyMuPDF for PDF. This is the same first step every parser performs, and it's the layer
  where formatting actually kills resumes — so our parse-back here is genuine, not a proxy.
- **Stage 2 (field extraction)** — the proprietary ML. We approximate it with an open
  spaCy-based parser (`ats_preview.py`) to show "what a machine would extract" (name,
  title, dates, skills), clearly labeled as a **proxy**, not the commercial engine.

So the skill "optimizes for the engine" in the sense that matters — it follows the engines'
**documented parse-survival and ranking behavior** (the rubric) and verifies with the same
kind of extraction they perform — without pretending to run their closed code.

---

## 4. The rubric: how the knowledge becomes rules

The skill encodes the durable mechanics as a rubric (`references/ats-optimization.md`)
that the host model and the scoring script both consult.

### 4.1 Parse-survival rules (applied when writing + rendering)
- Single column. No tables, text boxes, or multi-column layouts.
- Standard headings: **Summary, Skills, Work Experience, Education, Certifications**.
- Real text only — never information inside images.
- Dates as **`MM/YYYY`**; job title on its own line; don't merge company/title/date.
- Common fonts; plain bullet characters.

### 4.2 Matching rules (set the score weights)
The scorer's weights are derived directly from the "literal-first" finding:

| Signal | Weight | Rationale |
|---|---|---|
| Must-have-skill coverage | **0.50** | The dominant ranking signal |
| Keyword coverage | **0.30** | Literal JD term overlap |
| Semantic match | **0.20** | Secondary embedding-style similarity |

- **Acronym + spell-out pairing** once: "Search Engine Optimization (SEO)" — covers
  both tokenized keyword search and recruiter Boolean queries.
- Mirror the JD's exact phrasing **only** for skills the corpus actually proves.

### 4.3 Honesty rules
- Never claim a skill with no corpus evidence — report it as an unfillable gap instead.
- The output is something you can defend in an interview, by construction.

---

## 5. How the skill applies the knowledge, end to end

| Step | What the host model does | Which knowledge it uses |
|---|---|---|
| **Analyze** | Extracts must-haves, exact keywords (with acronym pairs), seniority, team priorities from the JD | §3.2 matching signals; §4.2 acronym rule |
| **Select** | Pulls the corpus bullets that best prove those must-haves/keywords | Literal-first: prioritize bullets that carry the exact terms |
| **Write** | Composes the resume, mirroring JD phrasing for proven skills, reverse-chronological | §4.1 parse-survival; §4.2 mirroring rule |
| **Score** | `score.py` computes literal coverage + weighted score | §4.2 weights, literal matching |
| **Verify** | Parse-back (render → re-extract) confirms keywords survive the DOCX; traceability confirms no invented claims | §3.1 parser reality; §4.3 honesty |
| **Report** | Surfaces coverage, matches, and honest gaps | §4.3 honesty rules |

---

## 6. Scope & caveats (read this before trusting a number)

- **Agency vs corporate:** the research targeted agency tools, but the parse-survival
  rules transfer to corporate ATSs (Workday/Greenhouse/Lever) because they share the
  same parsing engines. Corporate *ranking* quirks are a candidate for a future
  research refresh.
- **The rubric encodes mechanics, not survey stats.** Adoption/impact percentages are
  vendor-sourced and are intentionally not part of the scoring logic.
- **No deception.** Hidden white-on-white keywords, invisible fonts, and keyword-
  stuffed metadata are explicitly out of scope — modern parsers strip formatting and
  read raw text, recruiters see the rendered version (a mismatch is an instant reject),
  and AI matchers increasingly flag stuffing. The skill wins through *legitimate*
  optimization only.
- **The knowledge is versioned and regenerable.** `references/ats-optimization.md`
  carries its provenance; a future research run can refresh it without touching the
  skill's machinery.
