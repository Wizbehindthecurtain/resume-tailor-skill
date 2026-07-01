---
title: ATS Optimization Rubric
source: docs/research/2026-06-30-agency-ats-research.md
scope: durable parsing/matching mechanics only (soft adoption stats excluded)
---

# ATS Optimization Rubric

## Formatting rules (parse-survival) — applied by the Writer/Renderer
Agency ATSs (Bullhorn et al.) and many corporate ATSs license the same parsing
engines (Sovren/Textkernel, HireAbility, Affinda), so these rules transfer broadly:
- Single column. No tables, text boxes, multi-column layouts, headers/footers for content.
- Standard section headings: "Summary", "Skills", "Work Experience", "Education".
- Real text only — never put information inside images/graphics.
- Dates as `MM/YYYY`. Job title on its own line; company and title not merged into one styled blob.
- Common fonts; no decorative glyphs as bullets.

## Matching rules (ranking) — set the Scorer's weights
Agency matchers ("AI-driven relevancy scores", "bimetric scoring") reward literal
coverage first, semantics second:
- **Literal must-have-skill coverage** is the dominant signal → Scorer weight 0.50.
- **Keyword coverage** of JD terms → Scorer weight 0.30.
- **Semantic similarity** to the JD (LLM-judged) is secondary → Scorer weight 0.20.
- Pair acronym + spell-out once: "Search Engine Optimization (SEO)".
- The ATS is the recruiter's search DB — surface for Boolean/keyword search, not just an auto-gate.

## Honesty rules
- Mirror the JD's exact phrasing ONLY for skills the corpus already evidences.
- Never claim a skill with no corpus evidence — report it as an unfillable gap instead.

## Provenance & caveats
Derived from an adversarially-verified research run (see research-report.md). The
research's adoption/impact percentages are vendor-survey self-reports and are
deliberately NOT encoded here — only the durable parsing/matching mechanics are.
