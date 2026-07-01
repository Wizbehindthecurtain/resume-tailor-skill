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

# Sections whose bullets are structured facts grounded in their own corpus files
# (skills.md / education.md / certifications.md / references.md) or are prose intros —
# NOT accomplishment claims, so they are exempt from the corpus-bullet traceability check.
_EXEMPT_SECTIONS = {
    "skills", "education", "certifications", "certs", "references",
    "about me", "summary", "contact", "profile",
}

def resume_bullets(resume_text: str) -> list:
    """Bullets from accomplishment sections (Work Experience, Ventures, Projects, ...),
    excluding the structured-fact sections in _EXEMPT_SECTIONS. With no `## ` headings at
    all, every bullet is collected (fallback for bare-bullet input)."""
    bullets = []
    exempt = False
    for line in resume_text.splitlines():
        s = line.strip()
        if s.startswith("## "):
            exempt = s[3:].strip().lower() in _EXEMPT_SECTIONS
        elif s.startswith("- ") and not exempt:
            bullets.append(_clean(s[2:]))
    return bullets

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
