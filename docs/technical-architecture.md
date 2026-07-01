---
title: resume-tailor — Technical Architecture
date: 2026-07-01
audience: developers / anyone evaluating how the skill is built
status: reference
---

# resume-tailor — Technical Architecture

This document covers the technology involved: the execution model, the components,
what each is built from, how data flows, and why the responsibilities are split the
way they are.

> **Design in one sentence:** The host model (the user's own Claude or Codex) does all
> the *reasoning*; three small, stateless Python scripts do the three things a language
> model can't do reliably — produce a real `.docx`, compute an exact score, and verify
> traceability. No API keys, no server.

---

## 1. Execution model: host-reasoned, not API-driven

The predecessor was a Python application that called the Anthropic API once per
"agent" step (analyze, select, write, score). This version inverts that: **the host
model is the reasoning engine.**

```
        ┌─────────────────────────────────────────────────────────┐
        │  Host model (user's Claude Code / Codex session)         │
        │                                                          │
        │   reads SKILL.md → follows the workflow →                │
        │   reasons over corpus + JD + ATS rubric →                │
        │   calls scripts only for exact operations                │
        └───────────────┬───────────────────────┬─────────────────┘
                        │ shells out             │ reads/writes
                        ▼                        ▼
             ┌──────────────────┐     ┌──────────────────────────┐
             │  scripts/*.py    │     │  ./resume-brain/  (corpus)│
             │  (deterministic) │     │  ./applications/  (output)│
             └──────────────────┘     └──────────────────────────┘
```

**Consequences of this model:**
- **No `ANTHROPIC_API_KEY`, no cost to the user** — the reasoning runs on the session
  they already have.
- **Portable** — the same `SKILL.md` + scripts run in any host that loads skills
  (Claude Code and Codex both do).
- **No network services** — company research uses the host's own web tools; there is no
  Firecrawl or other scraping dependency.
- **Truthfulness moves from structural to verified** — because the host can read the
  whole corpus and reason freely, "never invent" is enforced by an explicit
  verification script rather than by physically withholding data (see §5).

---

## 2. The skill mechanism

A **skill** is a `SKILL.md` file plus bundled resources. Its frontmatter
(`name`, `description`) tells the host *when* to activate it; its body is the workflow
the host follows. Hosts load skills through their own skill-loading mechanism (the
Claude Code `Skill` tool, Codex's native skill loading), so no runtime shim is needed.

```
resume-tailor-skill/
├─ SKILL.md              ← activation frontmatter + the workflow decision-graph
├─ references/           ← knowledge the host reads (rubric, research, corpus schema)
├─ templates/            ← default resume template
├─ scripts/             ← the deterministic tools (below)
└─ tests/               ← pytest for the scripts
```

`SKILL.md` is **instructions, not code**. Steps like "analyze the JD" or "select the
best bullets" are performed by the host reasoning against the bundled rubric; the skill
only *calls out* to scripts at the exact-operation boundaries.

---

## 3. The three scripts (the deterministic core)

Standalone CLIs — args/stdin in, file or JSON out. **Only third-party dependency:
`python-docx`.** Each is independently pytest-covered.

### 3.1 `render_docx.py` — Markdown → DOCX (+ parse-back)
- **Tech:** `python-docx`. Maps `#/##/###` to headings, `-` to list bullets, other
  lines to paragraphs; enforces single-column, default styles (parse-survival).
- `--in resume.md --out resume.docx` writes the file; `--extract resume.docx` prints
  the document's raw text back out.
- **Why it must be code:** a language model cannot emit valid `.docx` binary (it's a
  zipped OOXML package). The `--extract` mode enables the **parse-back check**: render,
  re-read, assert the must-have keywords survived — the single highest-value test,
  because it proves the output survives the medium a real parser will read.

### 3.2 `score.py` — deterministic scoring
- **Tech:** pure Python string processing (case-insensitive, acronym-aware matching);
  no dependencies.
- **Input** (JSON on stdin): `{resume_text, keywords[], must_haves[], semantic_match}`.
- **Does the literal work in code** — keyword coverage % and must-have hit-rate by
  string matching — so the literal signals are not subject to host guesswork. The host
  supplies only the `semantic_match` judgment (0–1).
- **Output** (JSON): `{score, keyword_coverage, must_have_hit_rate, semantic_match,
  matched[], missing[]}`, combined with fixed weights **0.50 / 0.30 / 0.20**. The final
  integer score is computed here, never trusted from the model.

### 3.3 `check_traceability.py` — the truthfulness backstop
- **Tech:** fuzzy string matching (Python stdlib `difflib`, or `rapidfuzz` if we accept
  one more dependency) between output bullets and corpus bullets.
- **Input:** the generated resume + the `resume-brain/` path.
- **Output** (JSON): `{untraceable[]}` — output lines that don't map to any corpus
  bullet above a similarity threshold.
- The workflow treats a non-empty result as a **hard blocker**: the host must fix or
  drop the line before completion. This is what keeps "never invent" honest once the
  host reasons freely.

### 3.4 `ats_preview.py` — Stage-2 field-extraction proxy
- **Tech:** spaCy (`en_core_web_sm`) via a resume-parser layer (`pyresparser`), reading
  the rendered DOCX.
- `python scripts/ats_preview.py resume.docx` → JSON of the structured fields a real ATS
  would extract (name, contact, employers, titles, dates, skills). Optionally run on the
  original resume for a before/after comparison.
- **Why it's a proxy, not the real thing:** the named commercial engines
  (Sovren/Textkernel, HireAbility, Affinda) are **proprietary and closed-source** — none
  are pip-installable, so they cannot run in a keyless local skill. This script
  approximates their Stage-2 field extraction with an open spaCy parser and is labeled as
  a proxy. It is **non-blocking** (informational), and **degrades gracefully** — if spaCy
  or the model isn't installed, it emits a "run `python -m spacy download en_core_web_sm`
  to enable the ATS field preview" message rather than failing the run.

### 3.5 The two parsing stages (why there are two verification steps)
A real ATS parses in two stages; the skill mirrors both, with different fidelity:
| Stage | What it does | Our tool | Fidelity |
|---|---|---|---|
| **1. Text extraction** | file → raw text (where columns/tables/images break resumes) | `render_docx.py --extract` (python-docx) | **Real** — genuine extraction, the same first step every parser performs |
| **2. Field extraction** | text → {name, title, dates, skills} | `ats_preview.py` (spaCy/pyresparser) | **Proxy** — approximates the proprietary ML engines |

---

## 4. The corpus (data layer)

The corpus is plain Markdown with YAML frontmatter — human-readable, git-friendly, and
directly readable by the host (no loader needed at tailor time).

```
resume-brain/
├─ profile.md            # name, contact, links, summary variants
├─ roles/<slug>.md       # frontmatter: type/company/title/start/end/skills
│                        # ## Bullets  (each tagged [metric: …] [skills: …])
│                        # ## Context
├─ projects/<slug>.md
├─ skills.md             # skill inventory, each with proficiency + evidence links
├─ education.md
└─ certifications.md
```

- **Inline bullet tags** (`[metric: 40%]`, `[skills: permitting, sop-development]`) make
  the corpus *searchable* — the Select step retrieves by tag rather than guessing.
- **Provenance:** every bullet knows its source file, which is what
  `check_traceability.py` maps against.
- The corpus lives in the **user's working directory**, never inside the shared skill —
  personal data stays local and is gitignored by the skill's own template `.gitignore`.

---

## 5. Where reasoning ends and code begins

The architecture draws one clean line:

| Owned by **code** (must be exact / repeatable) | Owned by the **host model** (judgment) |
|---|---|
| DOCX bytes (`render_docx.py`) | Which bullets best fit the job (Select) |
| Keyword/must-have arithmetic + weighted score (`score.py`) | How to phrase and frame (Write) |
| Traceability of every claim (`check_traceability.py`) | Semantic-fit judgment (the `semantic_match` input) |
| The corpus file format (schema) | Reading the JD and company site (Analyze) |

Neither side does the other's job. This is why the tool layer is three small scripts
instead of a framework: everything that benefits from a language model is *left* to the
language model, and only the exact operations are frozen into code.

---

## 6. Data flow (one tailoring run)

```
resume-brain/ ──┐
                ├─▶ [host: Analyze JD + company] ─▶ must-haves, keywords, priorities
job description ┘
                        │
                        ▼
             [host: Select bullets] ─▶ chosen bullets (+ provenance)
                        │
                        ▼
             [host: Write resume.md]  ◀─── templates/resume_template.md
                        │                    references/ats-optimization.md
                        ▼
        score.py ─▶ score + coverage      check_traceability.py ─▶ untraceable[]
                        │                            │
                        ├── score < 85 & untraceable empty? → revise (≤2 passes)
                        ▼
        render_docx.py ─▶ applications/<company>-<date>/resume.docx
                        │   (parse-back: --extract confirms keywords survived)
                        ▼
                 score-report.md  (coverage, matches, honest gaps)
```

---

## 7. Requirements, testing, distribution

**Requirements**
- A host that loads skills (Claude Code or Codex).
- Python 3.11+.
- Core dependency: `python-docx` (`difflib` for traceability is stdlib).
- Field-preview dependency (Stage 2): `spacy` + `pyresparser` +
  `python -m spacy download en_core_web_sm`. Heavier (~hundreds of MB with the model),
  fully local and keyless. Core tailoring works without it; the preview degrades to an
  install hint if absent.
- No API keys. No network services (company research uses the host's web tools; the
  proprietary parsing engines are never called — Stage 2 uses a local open proxy).

**Testing**
- The three scripts are **pytest-covered** — the deterministic core is where automated
  tests have leverage: render + parse-back keyword survival, score math + matching, and
  traceability catching a planted un-grounded claim.
- The **workflow** (SKILL.md) is validated by a documented **manual smoke test** in the
  README: seed a tiny sample corpus, run one tailoring pass in a real host, confirm a
  DOCX + report land and traceability passes. Workflow instructions can't be unit-
  tested, so this is the acceptance check.

**Distribution**
- Primary artifact: the portable `resume-tailor-skill/` directory — drop it into a
  skills directory in either host.
- Optional later: a thin Claude Code **plugin wrapper** (`plugin.json` + marketplace
  entry) for one-click install. Additive; it does not change the skill.

---

## 8. Relationship to the predecessor

This skill is a re-architecture, not a rewrite from zero. The proven **deterministic
core and domain knowledge are ported** from the earlier API-architecture build
(`render/docx.py`, the `compute_score` math, the ATS rubric, the corpus schema and
template), all of which were already TDD-verified there. What is **dropped** is the
orchestration layer that the host model now replaces: the API client, the per-step
agents, the pipeline, and the CLI. Building the API version first is what let us prove
the rendering, scoring, and corpus format before betting the portable skill on them.
