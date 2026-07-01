# Fix-A Report: Scope Traceability to Work Experience Bullets

## Summary

**Bug:** `resume_bullets()` in `scripts/check_traceability.py` collected every `- ` line in a resume, causing Skills, Education, and Certifications bullets to be flagged as untraceable — false positives, since those are grounded in their own corpus files.

**Fix:** Modified `resume_bullets()` to collect bullets only when under a `## …experience…` heading. `### ` subheadings (e.g. job titles) do NOT toggle the section — only `## ` headings do. If no experience heading exists anywhere, falls back to collecting all `- ` lines to preserve behavior for bare-bullet inputs.

## TDD Cycle

### RED (before fix)
Added `test_only_experience_section_bullets_are_checked` to `tests/test_check_traceability.py`.

```
FAILED tests/test_check_traceability.py::test_only_experience_section_bullets_are_checked
AssertionError: assert 'fabricated skill nobody has' not in ['fabricated skill nobody has', 'won the nobel prize in physics', 'made-up university']
1 failed, 2 passed in 0.10s
```

### Fix applied to `scripts/check_traceability.py`

Replaced the one-liner `resume_bullets()` with the scoped implementation:
- Detects whether any `## …experience…` heading exists (`has_exp` flag)
- If `has_exp` is False → `in_exp` starts True (fallback: collect all)
- Only `## ` headings toggle `in_exp`; `### ` headings are ignored
- Bullets are only appended when `in_exp` is True

### GREEN (after fix)
```
8 passed, 1 failed in 4.42s
```

The 1 failure (`test_extracts_fields_when_available`) is a **pre-existing machine issue** — `pyresparser` is installed but broken (`config.cfg` missing from the package). This test was already failing before this fix (confirmed by stashing changes and running baseline: same 1 failed, 7 passed).

Expected result per task spec was "8 passed, 1 skipped" — on this machine the `pyresparser` test is not skipped because the package IS importable; it only crashes at runtime. This is not a regression introduced by this fix.

## Files Changed

- `scripts/check_traceability.py` — `resume_bullets()` function replaced
- `tests/test_check_traceability.py` — `test_only_experience_section_bullets_are_checked` added

## Commit

`fix: scope traceability to Work Experience bullets (skills/education/certs live in their own corpus files)`
