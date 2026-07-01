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
     `education.md`, `certifications.md`, `references.md`. **Only facts from their resume — invent nothing.**
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
Compose the resume in Markdown using `templates/resume_template.md`. Use this section order:
**About Me → Skills → Work Experience → Businesses Owned & Operated (when applicable) → Education → Certifications → References**

- **About Me (company-tailored):** the opening section is a company-tailored "About Me" (not
  a generic summary). It MUST connect the candidate's real, corpus-grounded experience to the
  specific target company's mission, values, and role — using the company research from Step 2.
  Never invent facts about the candidate; the company framing comes from research, the
  substance comes from the corpus.
- Reverse-chronological Work Experience with real `MM/YYYY` dates from the corpus.
- Mirror the JD's phrasing ONLY for skills the corpus proves.
- **Businesses Owned & Operated (conditional):** if the corpus has projects the candidate
  founded/owned and they're relevant to the employer (especially ownership-culture or
  entrepreneurial employers), include a "Businesses Owned & Operated" section from those
  project entries.
- Education + Certifications verbatim from the corpus.
- **References:** include a References section from `references.md`, OR "References available
  upon request" if the user prefers not to list contacts. (Note the tradeoff: listing
  reference phone numbers exposes contacts' info to every ATS/recruiter.)
- Single column, standard headings, no tables/images (parse-survival).

## Step 6 — SCORE + VERIFY (iterate, max 2 extra passes)
1. `echo '<json>' | python scripts/score.py` with
   `{resume_text, keywords[], must_haves[], semantic_match}` — you supply `semantic_match`
   (0–1) as your judgment; the script computes literal coverage + the weighted score.
2. `python scripts/check_traceability.py --resume <resume.md> --brain resume-brain` —
   **if `untraceable` is non-empty, you MUST fix or drop those lines before continuing.**
3. If `score` < 85 and there's room to improve (missing keywords the corpus can prove),
   revise and re-score. Cap at 2 extra passes.
4. **Gap-driven corpus-enrichment prompt:** after scoring, if there are unmet must-haves or
   missing keywords (gaps), DO NOT stop at the low score and DO NOT fabricate. Instead:
   a. Present the specific gaps to the user and ASK whether they actually have real
      experience, qualifications, or metrics for any of them (e.g. "The JD wants OSHA and
      budget management — do you have those?").
   b. For each gap the user confirms is real, ADD it to the corpus (the appropriate
      role/project bullet, skill, or certification in `resume-brain/`), so it's grounded and
      persists for future applications.
   c. Re-select / re-write / re-score. Only user-confirmed, real facts — traceability still
      governs (never add an un-grounded claim).
   This is the honest score-raising loop: a gap in the score is often a gap in the corpus,
   not a reason to fabricate.

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
