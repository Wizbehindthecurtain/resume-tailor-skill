#!/usr/bin/env python3
"""Deterministic ATS score: word-boundary keyword/must-have coverage + weighted total.

Two integrity rules beyond naive matching:
- Word-boundary matching: 'GIS' does not match 'Solargis'; 'PV' does not match 'improve'.
- Must-have backing: must-haves are matched only against EVIDENCED sections, excluding
  aspirational prose (About Me / Summary / Objective / Profile), so a keyword mentioned
  only as a goal in the summary cannot inflate the must-have hit-rate.
"""
import json
import re
import sys

WEIGHT_MUST_HAVE = 0.50
WEIGHT_KEYWORD = 0.30
WEIGHT_SEMANTIC = 0.20

# Prose intro sections that state positioning/aspiration, not evidenced experience.
_ASPIRATIONAL_SECTIONS = {"about me", "summary", "objective", "profile"}


def _matches(term: str, text_lower: str) -> bool:
    """Whole-token/phrase match (punctuation-safe), case-insensitive.
    text_lower must already be lowercased."""
    return re.search(r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?![a-z0-9])",
                     text_lower) is not None


def _coverage(terms, text_lower):
    matched = [t for t in terms if _matches(t, text_lower)]
    missing = [t for t in terms if not _matches(t, text_lower)]
    rate = len(matched) / len(terms) if terms else 1.0
    return matched, missing, rate


def _evidenced_text(resume_text: str) -> str:
    """Resume text with aspirational prose sections (About Me/Summary/...) removed."""
    out, skip = [], False
    for line in resume_text.splitlines():
        s = line.strip()
        if s.startswith("## "):
            skip = s[3:].strip().lower() in _ASPIRATIONAL_SECTIONS
            continue
        if not skip:
            out.append(line)
    return "\n".join(out)


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
    full_lower = resume_text.lower()
    evidenced_lower = _evidenced_text(resume_text).lower()
    kw_matched, kw_missing, kw_cov = _coverage(keywords, full_lower)
    mh_matched, mh_missing, mh_rate = _coverage(must_haves, evidenced_lower)
    matched = sorted(set(kw_matched + mh_matched))
    missing = sorted(set(kw_missing + mh_missing) - set(matched))
    return {
        "score": compute_score(mh_rate, kw_cov, semantic_match),
        "keyword_coverage": kw_cov,
        "must_have_hit_rate": mh_rate,
        "semantic_match": semantic_match,
        "matched": matched,
        "missing": missing,
    }


def main(argv=None) -> int:
    json.dump(score(json.load(sys.stdin)), sys.stdout, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
