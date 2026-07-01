# resume-tailor Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portable, keyless resume-tailoring skill where the host model reasons and small Python scripts handle the exact operations (DOCX render, deterministic score, traceability, ATS field preview).

**Architecture:** A `SKILL.md` workflow + four standalone Python CLI scripts + bundled references (ATS rubric, research, corpus schema, template). The host (Claude Code / Codex) does all reasoning; scripts are invoked only for exact operations. User data lives in their working directory, never in the skill.

**Tech Stack:** Python 3.11+, `python-docx` (core), `spacy` + `pyresparser` (field-preview extra), `difflib` (stdlib), pytest.

## Global Constraints

- Python 3.11+ (`X | None` unions, `list[...]` generics allowed).
- Scripts live in `scripts/`, are standalone CLIs with importable functions + a `main(argv=None) -> int`, and are tested via `pythonpath = ["scripts"]`.
- Core third-party dependency: `python-docx`. Field preview adds `spacy` + `pyresparser` (optional extra); its test skips cleanly when absent.
- No API keys, no network calls inside any script. Company research is the host's job, not a script's.
- Scoring weights are exactly **0.50 must-have / 0.30 keyword / 0.20 semantic**; default target **85**.
- Truthfulness: `check_traceability.py` is a **hard blocker** (non-empty `untraceable` must be resolved); `ats_preview.py` is **non-blocking** (informational) and must degrade gracefully to an install hint when spaCy/pyresparser is absent.
- Personal corpus + outputs are gitignored (`resume-brain/`, `applications/`) — already in `.gitignore`.
- Commit after each task with the exact message shown in its final step.
- Ports come from the existing repo at `C:\Users\jacks\resume-tailor` (proven, TDD-tested there).

## Parallelization note

Task 1 (scaffold) must complete first. **Tasks 2–5 are independent** — each creates only its own `scripts/<name>.py` + `tests/test_<name>.py` and touches no shared file — so they may be built in parallel (worktree isolation recommended). Tasks 6–7 depend on the scripts existing and run after.

## File Structure

```
resume-tailor-skill/
├─ pyproject.toml                ← pytest config (pythonpath=scripts, testpaths=tests)
├─ SKILL.md                      ← activation frontmatter + workflow (Task 6)
├─ README.md                     ← install + manual smoke test (Task 7)
├─ references/
│  ├─ ats-optimization.md        ← ported rubric (Task 1)
│  ├─ research-report.md         ← ported research provenance (Task 1)
│  └─ corpus-schema.md           ← corpus format spec (Task 1)
├─ templates/resume_template.md  ← ported template (Task 1)
├─ scripts/
│  ├─ render_docx.py             ← Task 2
│  ├─ score.py                   ← Task 3
│  ├─ check_traceability.py      ← Task 4
│  └─ ats_preview.py             ← Task 5
└─ tests/
   ├─ test_render_docx.py
   ├─ test_score.py
   ├─ test_check_traceability.py
   └─ test_ats_preview.py
```

---

## Task 1: Scaffold + port references

**Files:**
- Create: `pyproject.toml`, `references/corpus-schema.md`
- Copy from old repo: `references/ats-optimization.md`, `references/research-report.md`, `templates/resume_template.md`
- Create dirs: `scripts/`, `tests/`

**Interfaces:**
- Consumes: nothing.
- Produces: pytest config (`pythonpath=["scripts"]`), the bundled references the SKILL.md and scripts will use.

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "resume-tailor-skill"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["python-docx>=1.1"]

[project.optional-dependencies]
preview = ["spacy>=3.7", "pyresparser>=1.0.6"]
dev = ["pytest>=8.0"]

[tool.pytest.ini_options]
pythonpath = ["scripts"]
testpaths = ["tests"]
```

- [ ] **Step 2: Copy the proven references + template from the existing repo**

```bash
mkdir -p references templates scripts tests
cp "/c/Users/jacks/resume-tailor/brain/knowledge/ats-optimization.md" references/ats-optimization.md
cp "/c/Users/jacks/resume-tailor/brain/knowledge/research-report.md" references/research-report.md
cp "/c/Users/jacks/resume-tailor/templates/resume_template.md" templates/resume_template.md
```

- [ ] **Step 3: Write `references/corpus-schema.md`** (the corpus format the host reads for tailoring and writes for seeding)

````markdown
# Corpus Schema (`resume-brain/`)

The corpus is plain Markdown with YAML frontmatter, in the user's working directory.
The skill reads it to tailor and writes it to seed. **Only ever record facts from the
user's real resume — never invent employers, dates, metrics, or skills.**

## `profile.md`
```markdown
---
name: Jane Doe
contact: {phone: "555-0100", email: "jane@example.com", address: "City, ST"}
links: {linkedin: "https://linkedin.com/in/jane"}
summaries:
  - "First summary variant."
  - "Second variant emphasizing a different angle."
---
```

## `roles/<slug>.md` (one per job)
```markdown
---
type: role
company: Acme Corp
title: Senior Engineer
start: "2022-03"        # YYYY-MM (quoted)
end: "2024-08"          # or `null` for current
skills: [python, leadership]
---
## Bullets
- Cut thermal risk 40% by redesigning the pack [metric: 40%] [skills: safety]
- Led a 5-engineer team shipping X [skills: leadership, python]
## Context
Plain notes used for judgment; never copied verbatim into a resume.
```

## `projects/<slug>.md`
```markdown
---
type: project
name: Side Project Name
skills: [python, automation]
---
## Bullets
- Built X that did Y [metric: 2x] [skills: python]
## Context
Notes.
```

## `skills.md`
```markdown
---
skills:
  - name: python
    proficiency: expert
    evidence: [roles/acme.md]
---
```

## `education.md`
```markdown
---
education:
  - institution: State University
    credential: "B.S."      # optional
    field: "Engineering"    # optional
    dates: "2015–2019"      # optional
---
```

## `certifications.md`
```markdown
---
certifications:
  - name: Some Certification
    issuer: ""              # optional
    status: active          # "active" | "pending"
---
```

### Rules
- Tag every bullet with `[metric: …]` and `[skills: …]` so selection can retrieve well.
- Dates as `YYYY-MM`; the resume renders them `MM/YYYY`, roles reverse-chronological.
- A skill may only be claimed on a resume if it has evidence here or in a role/project bullet.
````

- [ ] **Step 4: Verify the references landed**

Run: `ls references/ templates/ && head -5 references/ats-optimization.md`
Expected: `ats-optimization.md`, `research-report.md`, `corpus-schema.md`, `resume_template.md` present; rubric header prints.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml references/ templates/
git commit -m "feat: scaffold skill + port ATS rubric, research, schema, template"
```

---

## Task 2: `render_docx.py` (Markdown → DOCX + parse-back)

**Files:**
- Create: `scripts/render_docx.py`
- Test: `tests/test_render_docx.py`

**Interfaces:**
- Consumes: `python-docx`.
- Produces: `render_resume(markdown_text: str, out_path) -> None`, `extract_text(docx_path) -> str`, `main(argv=None) -> int` in `render_docx`. Ported from the old repo's `render/docx.py`, wrapped in a CLI.

- [ ] **Step 1: Write the failing test** `tests/test_render_docx.py`

```python
import render_docx

def test_render_and_parse_back_keeps_keywords(tmp_path):
    md = ("# Jane Doe\n## Skills\n- Python (PYTHON)\n- Kubernetes\n"
          "## Work Experience\n### Engineer — Acme — 03/2022\n- Cut risk 40%\n")
    out = tmp_path / "r.docx"
    render_docx.render_resume(md, out)
    assert out.exists()
    text = render_docx.extract_text(out)
    for kw in ("Python", "Kubernetes", "Acme", "40%"):
        assert kw in text

def test_main_extract(tmp_path, capsys):
    out = tmp_path / "r.docx"
    render_docx.render_resume("# Jane\n- Python\n", out)
    rc = render_docx.main(["--extract", str(out)])
    assert rc == 0 and "Python" in capsys.readouterr().out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pip install -e ".[dev]" && pytest tests/test_render_docx.py -v`
Expected: FAIL with `ModuleNotFoundError: render_docx`.

- [ ] **Step 3: Write `scripts/render_docx.py`**

```python
#!/usr/bin/env python3
"""Render resume Markdown to a single-column ATS-friendly DOCX, and extract text back."""
import argparse
import sys
from pathlib import Path
from docx import Document

def render_resume(markdown_text: str, out_path) -> None:
    doc = Document()
    for raw in markdown_text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=1)
        elif line.startswith("- "):
            doc.add_paragraph(line[2:], style="List Bullet")
        else:
            doc.add_paragraph(line)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))

def extract_text(docx_path) -> str:
    doc = Document(str(docx_path))
    return "\n".join(p.text for p in doc.paragraphs)

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Render resume Markdown to DOCX, or extract text.")
    parser.add_argument("--in", dest="in_path", type=Path)
    parser.add_argument("--out", dest="out_path", type=Path)
    parser.add_argument("--extract", dest="extract_path", type=Path)
    args = parser.parse_args(argv)
    if args.extract_path:
        sys.stdout.write(extract_text(args.extract_path))
        return 0
    if args.in_path and args.out_path:
        render_resume(args.in_path.read_text(encoding="utf-8"), args.out_path)
        sys.stdout.write(str(args.out_path))
        return 0
    parser.error("provide --in and --out to render, or --extract to extract")

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_render_docx.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/render_docx.py tests/test_render_docx.py
git commit -m "feat: render_docx.py — Markdown to single-column DOCX + parse-back"
```

---

## Task 3: `score.py` (deterministic keyword coverage + weighted score)

**Files:**
- Create: `scripts/score.py`
- Test: `tests/test_score.py`

**Interfaces:**
- Consumes: stdlib only.
- Produces: `compute_score(must_have_hit_rate, keyword_coverage, semantic_match) -> int`, `score(payload: dict) -> dict`, `main(argv=None) -> int` in `score`. Weights 0.50/0.30/0.20.

- [ ] **Step 1: Write the failing test** `tests/test_score.py`

```python
import score

def test_compute_score_weights():
    assert score.compute_score(1.0, 1.0, 1.0) == 100
    assert score.compute_score(1.0, 0.5, 0.0) == 65

def test_score_literal_matching():
    payload = {"resume_text": "Built CI in Python and Kubernetes",
               "keywords": ["python", "kubernetes", "terraform"],
               "must_haves": ["python"], "semantic_match": 1.0}
    out = score.score(payload)
    assert out["must_have_hit_rate"] == 1.0
    assert abs(out["keyword_coverage"] - 2 / 3) < 1e-9
    assert "terraform" in out["missing"]
    assert out["score"] == 90  # 0.50*1 + 0.30*0.667 + 0.20*1 = 0.90
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_score.py -v`
Expected: FAIL with `ModuleNotFoundError: score`.

- [ ] **Step 3: Write `scripts/score.py`**

```python
#!/usr/bin/env python3
"""Deterministic ATS score: literal keyword/must-have coverage + weighted total."""
import json
import sys

WEIGHT_MUST_HAVE = 0.50
WEIGHT_KEYWORD = 0.30
WEIGHT_SEMANTIC = 0.20

def _coverage(terms, resume_text):
    text = resume_text.lower()
    matched = [t for t in terms if t.lower() in text]
    missing = [t for t in terms if t.lower() not in text]
    rate = len(matched) / len(terms) if terms else 1.0
    return matched, missing, rate

def compute_score(must_have_hit_rate: float, keyword_coverage: float,
                  semantic_match: float) -> int:
    return round(100 * (WEIGHT_MUST_HAVE * must_have_hit_rate
                        + WEIGHT_KEYWORD * keyword_coverage
                        + WEIGHT_SEMANTIC * semantic_match))

def score(payload: dict) -> dict:
    resume_text = payload.get("resume_text", "")
    keywords = payload.get("keywords", [])
    must_haves = payload.get("must_haves", [])
    semantic_match = float(payload.get("semantic_match", 0.0))
    kw_matched, kw_missing, kw_cov = _coverage(keywords, resume_text)
    mh_matched, mh_missing, mh_rate = _coverage(must_haves, resume_text)
    return {
        "score": compute_score(mh_rate, kw_cov, semantic_match),
        "keyword_coverage": kw_cov,
        "must_have_hit_rate": mh_rate,
        "semantic_match": semantic_match,
        "matched": sorted(set(kw_matched + mh_matched)),
        "missing": sorted(set(kw_missing + mh_missing)),
    }

def main(argv=None) -> int:
    json.dump(score(json.load(sys.stdin)), sys.stdout, indent=2)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_score.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/score.py tests/test_score.py
git commit -m "feat: score.py — deterministic keyword coverage + weighted score"
```

---

## Task 4: `check_traceability.py` (truthfulness backstop)

**Files:**
- Create: `scripts/check_traceability.py`
- Test: `tests/test_check_traceability.py`

**Interfaces:**
- Consumes: stdlib (`difflib`, `re`).
- Produces: `corpus_bullets(brain_dir) -> list[str]`, `resume_bullets(resume_text) -> list[str]`, `untraceable(resume_text, brain_dir, threshold=0.5) -> list[str]`, `main(argv=None) -> int` in `check_traceability`.

- [ ] **Step 1: Write the failing test** `tests/test_check_traceability.py`

```python
import check_traceability

def _brain(tmp_path):
    roles = tmp_path / "brain" / "roles"; roles.mkdir(parents=True)
    (tmp_path / "brain" / "projects").mkdir()
    (roles / "acme.md").write_text(
        "## Bullets\n- Cut thermal risk 40% by redesigning the pack [metric: 40%]\n",
        encoding="utf-8")
    return tmp_path / "brain"

def test_grounded_bullet_traces(tmp_path):
    brain = _brain(tmp_path)
    resume = "- Reduced thermal risk 40% by redesigning the pack\n"
    assert check_traceability.untraceable(resume, brain) == []

def test_fabricated_bullet_flagged(tmp_path):
    brain = _brain(tmp_path)
    resume = "- Won the Nobel Prize in Physics for cold fusion\n"
    flagged = check_traceability.untraceable(resume, brain)
    assert len(flagged) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_check_traceability.py -v`
Expected: FAIL with `ModuleNotFoundError: check_traceability`.

- [ ] **Step 3: Write `scripts/check_traceability.py`**

```python
#!/usr/bin/env python3
"""Verify each resume bullet traces to a corpus bullet (fuzzy). Flags un-grounded lines."""
import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

_TAG = re.compile(r"\[(?:metric|skills):[^\]]*\]")

def _clean(text: str) -> str:
    return re.sub(r"\s{2,}", " ", _TAG.sub("", text)).strip().lower()

def corpus_bullets(brain_dir) -> list:
    base = Path(brain_dir)
    bullets = []
    for sub in ("roles", "projects"):
        for f in sorted((base / sub).glob("*.md")):
            in_bullets = False
            for line in f.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if s.startswith("## "):
                    in_bullets = s[3:].strip().lower() == "bullets"
                elif in_bullets and s.startswith("- "):
                    bullets.append(_clean(s[2:]))
    return bullets

def resume_bullets(resume_text: str) -> list:
    return [_clean(l.strip()[2:]) for l in resume_text.splitlines()
            if l.strip().startswith("- ")]

def untraceable(resume_text: str, brain_dir, threshold: float = 0.5) -> list:
    corpus = corpus_bullets(brain_dir)
    flagged = []
    for rb in resume_bullets(resume_text):
        best = max((SequenceMatcher(None, rb, cb).ratio() for cb in corpus), default=0.0)
        if best < threshold:
            flagged.append(rb)
    return flagged

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Flag resume bullets not grounded in the corpus.")
    parser.add_argument("--resume", type=Path, required=True)
    parser.add_argument("--brain", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args(argv)
    flagged = untraceable(args.resume.read_text(encoding="utf-8"), args.brain, args.threshold)
    json.dump({"untraceable": flagged}, sys.stdout, indent=2)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_check_traceability.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add scripts/check_traceability.py tests/test_check_traceability.py
git commit -m "feat: check_traceability.py — flag un-grounded resume bullets"
```

---

## Task 5: `ats_preview.py` (Stage-2 field-extraction proxy)

**Files:**
- Create: `scripts/ats_preview.py`
- Test: `tests/test_ats_preview.py`

**Interfaces:**
- Consumes: `pyresparser` (optional; imported lazily inside the function).
- Produces: `extract_fields(docx_path) -> dict`, `main(argv=None) -> int` in `ats_preview`. Returns `{"available": False, "hint": ...}` when deps absent, else `{"available": True, "fields": {...}}`. Non-blocking.

- [ ] **Step 1: Write the failing test** `tests/test_ats_preview.py`

```python
import importlib.util
import sys
import pytest
import ats_preview

def test_returns_hint_when_pyresparser_absent(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "pyresparser", None)  # force ImportError
    result = ats_preview.extract_fields(tmp_path / "x.docx")
    assert result["available"] is False and "hint" in result

@pytest.mark.skipif(importlib.util.find_spec("pyresparser") is None,
                    reason="pyresparser not installed")
def test_extracts_fields_when_available(tmp_path):
    import render_docx
    docx = tmp_path / "r.docx"
    render_docx.render_resume("# Jane Doe\njane@example.com\n## Skills\n- Python\n", docx)
    result = ats_preview.extract_fields(docx)
    assert result["available"] is True and "fields" in result
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ats_preview.py -v`
Expected: FAIL with `ModuleNotFoundError: ats_preview` (the skipif test is collected but the import of the module under test fails first).

- [ ] **Step 3: Write `scripts/ats_preview.py`**

```python
#!/usr/bin/env python3
"""Stage-2 ATS field-extraction PROXY (spaCy/pyresparser). Non-blocking; degrades if absent.

This approximates the field extraction that proprietary engines (Sovren/Textkernel,
HireAbility, Affinda) perform. Those engines are closed-source and cannot run locally;
this is a labeled proxy, informational only.
"""
import argparse
import json
import sys
from pathlib import Path

_HINT = ("Install the field-preview extra to enable the ATS field preview: "
         "pip install spacy pyresparser && python -m spacy download en_core_web_sm")

def extract_fields(docx_path) -> dict:
    try:
        from pyresparser import ResumeParser
    except Exception:
        return {"available": False, "hint": _HINT}
    data = ResumeParser(str(docx_path)).get_extracted_data() or {}
    return {"available": True, "fields": {
        "name": data.get("name"),
        "email": data.get("email"),
        "mobile_number": data.get("mobile_number"),
        "skills": data.get("skills", []),
        "designation": data.get("designation", []),
        "company_names": data.get("company_names", []),
    }}

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ATS field-extraction proxy (Stage 2).")
    parser.add_argument("docx", type=Path)
    args = parser.parse_args(argv)
    json.dump(extract_fields(args.docx), sys.stdout, indent=2)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_ats_preview.py -v`
Expected: PASS or PASS+SKIP (the `available` test passes; the `when_available` test passes if pyresparser is installed, else skips).

- [ ] **Step 5: Commit**

```bash
git add scripts/ats_preview.py tests/test_ats_preview.py
git commit -m "feat: ats_preview.py — Stage-2 field-extraction proxy (graceful degrade)"
```

---

## Task 6: `SKILL.md` (the workflow)

**Files:**
- Create: `SKILL.md`

**Interfaces:**
- Consumes: all four scripts + the references. This is instructions for the host, not code.
- Produces: the activatable skill.

- [ ] **Step 1: Write `SKILL.md`**

````markdown
---
name: resume-tailor
description: Use when the user wants to tailor, ATS-optimize, or generate a resume for a specific job or company — e.g. "tailor my resume for this job", "ATS optimize my resume", "apply to this posting". Seeds a personal experience corpus on first run, then produces a truthfully tailored DOCX + a score report.
---

# resume-tailor

Tailor the user's resume to a specific job, drawing ONLY from their personal experience
corpus (`resume-brain/`). You (the host model) do the reasoning; call the bundled scripts
for the exact operations. Never invent experience.

Scripts (run from the skill dir): `scripts/render_docx.py`, `scripts/score.py`,
`scripts/check_traceability.py`, `scripts/ats_preview.py`.
References: `references/ats-optimization.md` (ATS rubric — READ IT FIRST),
`references/corpus-schema.md`, `templates/resume_template.md`.

## Step 1 — ONBOARDING GATE (every run)
Check the user's working directory for `resume-brain/profile.md`.
- **If missing → SEED FLOW:**
  1. Ask the user for their resume (PDF path, a file, or pasted text). Read it.
  2. Convert it into corpus files per `references/corpus-schema.md`:
     `profile.md`, `roles/<slug>.md`, `projects/<slug>.md`, `skills.md`,
     `education.md`, `certifications.md`. **Only facts from their resume — invent nothing.**
     Tag every bullet with `[metric: …]` and `[skills: …]`.
  3. Write the files into `./resume-brain/`.
  4. Show a summary (roles found, bullet counts, skills) and flag genuine gaps the
     resume didn't answer (e.g. missing degree/year). Ask them to confirm or correct.
  5. Only proceed once they confirm.
- **If present → continue.**

## Step 2 — GATHER TARGET
- Company: ask for the URL; use your own web tools to read the site (products, stack,
  values, recent news). Do NOT use any external scraping service.
- Job description: accept pasted text or a URL you fetch.

## Step 3 — ANALYZE (read `references/ats-optimization.md` first)
Extract: must-have skills, nice-to-haves, exact keywords (pair acronym + spell-out once,
e.g. "Search Engine Optimization (SEO)"), seniority, and inferred team priorities.

## Step 4 — SELECT
Read `resume-brain/`. Pick the bullets that best prove the must-haves/keywords. Track
each pick's source file. Prefer bullets carrying the exact JD terms (literal-first).

## Step 5 — WRITE
Compose the resume in Markdown on `templates/resume_template.md`:
- Reverse-chronological Work Experience with real `MM/YYYY` dates from the corpus.
- Mirror the JD's phrasing ONLY for skills the corpus proves.
- Single column, standard headings, no tables/images (parse-survival).
- Education + Certifications verbatim from the corpus.

## Step 6 — SCORE + VERIFY (iterate, max 2 extra passes)
1. `echo '<json>' | python scripts/score.py` with
   `{resume_text, keywords[], must_haves[], semantic_match}` — you supply `semantic_match`
   (0–1) as your judgment; the script computes literal coverage + the weighted score.
2. `python scripts/check_traceability.py --resume <resume.md> --brain resume-brain` —
   **if `untraceable` is non-empty, you MUST fix or drop those lines before continuing.**
3. If `score` < 85 and there's room to improve (missing keywords the corpus can prove),
   revise and re-score. Cap at 2 extra passes.

## Step 7 — RENDER + PREVIEW + REPORT
1. `python scripts/render_docx.py --in <resume.md> --out applications/<company>-<date>/resume.docx`
2. Stage-1 parse-back: `python scripts/render_docx.py --extract <resume.docx>` — confirm
   every must-have keyword survived.
3. Stage-2 field preview: `python scripts/ats_preview.py <resume.docx>` — show the user the
   fields a parser would extract. If it returns `available: false`, relay the install hint
   (optional feature; do not block on it).
4. Write `applications/<company>-<date>/score-report.md`: score, keyword coverage,
   must-have hit-rate, matched/missing, honest gaps (must-haves the corpus can't prove),
   and the ATS field preview.

## Honesty rules (non-negotiable)
- Never claim a skill or accomplishment not in `resume-brain/`. Unmet must-haves are
  reported as gaps, never fabricated.
- No hidden text, keyword stuffing, or invisible fonts — legitimate optimization only.
````

- [ ] **Step 2: Verify frontmatter + script references are valid**

Run: `head -4 SKILL.md && grep -c "scripts/" SKILL.md`
Expected: frontmatter with `name: resume-tailor` and `description:`; at least 4 `scripts/` references.

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "feat: SKILL.md — onboarding gate + tailoring workflow"
```

---

## Task 7: README + manual smoke test

**Files:**
- Create: `README.md`
- Test: manual smoke test (documented + executed once)

**Interfaces:**
- Consumes: everything.
- Produces: install docs + the acceptance smoke test.

- [ ] **Step 1: Write `README.md`**

````markdown
# resume-tailor (skill)

A keyless resume-tailoring skill for Claude Code and Codex. Your own model does the
reasoning; small Python scripts handle DOCX rendering, deterministic scoring, traceability,
and an ATS field preview. No API keys. Your personal data stays in your working directory.

## Install

1. Drop `resume-tailor-skill/` into your host's skills directory (Claude Code or Codex).
2. Install the core dependency:
   ```bash
   pip install python-docx
   ```
3. (Optional) Enable the Stage-2 ATS field preview:
   ```bash
   pip install spacy pyresparser
   python -m spacy download en_core_web_sm
   ```

## Use
Ask your host: *"Tailor my resume for this job: <URL or pasted JD>."* On first run it
seeds your `resume-brain/` from a resume you provide, then produces
`applications/<company>-<date>/resume.docx` + `score-report.md`.

## What runs where
- **Host model:** analyze JD, research the company (its own web tools), select bullets, write.
- **Scripts:** `render_docx.py` (DOCX + parse-back), `score.py` (weighted score),
  `check_traceability.py` (blocks un-grounded claims), `ats_preview.py` (field preview).

## Manual smoke test (acceptance)
```bash
pip install -e ".[dev]"
pytest -v                       # all script tests pass (ats_preview may SKIP without spaCy)

# End-to-end script check with a tiny corpus:
mkdir -p /tmp/rt-smoke/resume-brain/roles /tmp/rt-smoke/resume-brain/projects
printf '## Bullets\n- Cut thermal risk 40%% by redesigning the pack [metric: 40%%]\n' \
  > /tmp/rt-smoke/resume-brain/roles/acme.md
printf -- '- Reduced thermal risk 40%% by redesigning the pack\n' > /tmp/rt-smoke/resume.md
python scripts/check_traceability.py --resume /tmp/rt-smoke/resume.md --brain /tmp/rt-smoke/resume-brain
# → {"untraceable": []}
echo '{"resume_text":"Python Kubernetes","keywords":["python","go"],"must_haves":["python"],"semantic_match":0.8}' \
  | python scripts/score.py
# → score with keyword_coverage 0.5, must_have_hit_rate 1.0
python scripts/render_docx.py --in /tmp/rt-smoke/resume.md --out /tmp/rt-smoke/out.docx
python scripts/render_docx.py --extract /tmp/rt-smoke/out.docx    # text round-trips
```

## Truthfulness
The skill only uses what's in your corpus. `check_traceability.py` blocks any claim it
can't ground. Unmet job requirements are reported as honest gaps, never invented.
No deceptive ATS tricks.
````

- [ ] **Step 2: Run the full test suite**

Run: `pip install -e ".[dev]" && pytest -v`
Expected: all pass (ats_preview `when_available` may SKIP if spaCy absent).

- [ ] **Step 3: Run the documented end-to-end script smoke test**

Run the shell block from README "Manual smoke test" (the `check_traceability`, `score`, `render_docx` invocations).
Expected: `{"untraceable": []}`; a score JSON with `keyword_coverage` 0.5 and `must_have_hit_rate` 1.0; a DOCX whose extracted text round-trips.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: README with per-host install + manual smoke test"
```

---

## Self-Review

**Spec coverage:**
- Keyless, host-reasoned skill → SKILL.md (Task 6), no API in any script. ✓
- Onboarding gate seeds every new user → SKILL.md Step 1 + corpus-schema (Tasks 1, 6). ✓
- ATS knowledge bundled → references/ats-optimization.md + research-report.md (Task 1). ✓
- Three "exact" scripts + Stage-2 preview → Tasks 2–5. ✓
- Two-stage verification (parse-back real; field preview proxy) → Tasks 2, 5; SKILL Step 7. ✓
- Traceability hard blocker; field preview non-blocking → Task 4 + SKILL Step 6; Task 5 graceful degrade. ✓
- Weights 0.50/0.30/0.20, target 85 → Task 3 + SKILL Step 6. ✓
- Corpus in working dir, gitignored → `.gitignore` (present) + corpus-schema. ✓
- Portable to Claude Code + Codex, per-host install → README (Task 7). ✓
- Reverse-chron, MM/YYYY, education+certs verbatim → SKILL Step 5. ✓
- No deception → SKILL honesty rules; README. ✓

**Placeholder scan:** No TBD/TODO; every code step shows complete code; references are ported by explicit `cp` from named paths.

**Type consistency:** `render_resume`/`extract_text`/`main` consistent (Tasks 2, 5 test, 7). `compute_score(must_have_hit_rate, keyword_coverage, semantic_match)` arg order consistent in def + `score()` call (Task 3). `untraceable(resume_text, brain_dir, threshold=0.5)` consistent (Task 4 + SKILL Step 6 flags). `extract_fields(docx_path) -> dict` consistent (Task 5 + SKILL Step 7). Script CLI names in SKILL/README match the created files.

**Note:** Tasks 2–5 touch disjoint files and may run in parallel after Task 1; Tasks 6–7 are sequential and last.
