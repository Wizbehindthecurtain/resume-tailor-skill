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
