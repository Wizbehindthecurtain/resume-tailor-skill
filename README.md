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
   pip install spacy
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
> **Windows:** run this block in **Git Bash or WSL** — it uses POSIX shell (`/tmp`, `mkdir -p`, `printf`), which raw PowerShell/cmd don't support.
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
