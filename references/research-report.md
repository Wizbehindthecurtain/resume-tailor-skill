---
title: Staffing/Recruiting Agency ATS & AI-Screening Landscape (2025–2026)
date: 2026-06-30
source: deep-research workflow (run wf_b4ee35ef-643)
status: provenance for brain/knowledge/ats-optimization.md
confidence_note: source quality tilts toward vendor/aggregator material — see Caveats
---

# Agency ATS & AI-Screening Research — Provenance Report

This is the raw research backing the `resume-tailor` ATS optimization rubric.
It was produced by an adversarially-verified deep-research run: 6 search angles →
27 sources fetched → 117 claims extracted → top 25 verified by 3-vote panel →
17 confirmed, 8 killed. **Only confirmed findings are recorded as actionable; the
killed claims are listed so we never re-introduce them.**

> ⚠️ The rubric the writer/scorer consume must encode the **durable parsing/matching
> mechanics**, NOT the soft adoption stats. Most adoption/impact numbers trace to a
> single vendor survey (Bullhorn GRID) and are explicitly flagged below.

---

## Confirmed findings (use these)

### Market structure
- **Bullhorn is the dominant agency ATS/CRM system of record** — ~34–50% of the
  third-party staffing-agency segment, 10,000+ agencies, "industry standard,"
  criticized as expensive with a dated/buggy UI. (confidence: high)
  - *Important scope note:* dominance is **agency-specific**. In the broad/enterprise
    ATS market the leaders are Oracle, iCIMS, SAP, Workday, Greenhouse, etc. — these
    are corporate/in-house ATSs, not agency systems of record.
- **Agency field beyond Bullhorn:** Recruit CRM, Crelate, Vincere, Tracker RMS,
  JobAdder, Recruiterflow, Manatal, Zoho Recruit, plus AI-first challenger Atlas.
  Per-seat pricing ~$15/user/mo (Manatal) → ~$315/user/mo (Bullhorn enterprise).
  (confidence: high)

### Pricing (context only — not relevant to resume optimization)
- Bullhorn published ladder: Starter $99, Core $165, Pro (contact-sales). Real-world
  bands stretch to ~$315/user/mo with modules. (high/medium)

### AI screening / matching layer — **this is what matters for optimization**
- **AI screening/matching is increasingly delivered INSIDE the ATS**, not only as
  bolt-on tools. Bullhorn ships it via the **Amplify** "digital worker" suite —
  notably **Match** (surfaces & ranks candidates with **AI-driven relevancy scores**)
  and Outreach; generative JD-writing lives in the separate embedded Copilot/"Bullhorn
  AI" layer. (confidence: high)
- **Non-Bullhorn CRMs build in scoring too:** Gem (AI sourcing across 800M+ profiles
  with instant matching), SmartRecruiters "Winston" (screening/match scores),
  Manatal (AI parsing + weighted Recommendation Engine), Recruit CRM (AI parsing +
  "bimetric scoring"). (confidence: high)
- **Vendor-survey adoption signal:** ~78% of high-growth firms use AI embedded in
  their ATS; only ~10% have full-workflow agentic AI → AI-in-ATS is mainstream,
  full automation still early. (confidence: medium — Bullhorn GRID, vendor self-report)

### Stack architecture
- Full agency stack = ATS/CRM core + integrated phone/messaging (Ringover,
  RingCentral, WhatsApp) + video (Zoom/Teams/Meet) + AI sourcing (Juicebox/PeopleGPT),
  all feeding the ATS as system of record. (confidence: medium)

---

## What this means for resume optimization (the durable mechanics)

These are the **inferences we encode into the rubric** — derived from the confirmed
findings above plus how the underlying parsing/matching engines work:

1. **Optimize for the parsing engine, not the brand.** Agency ATSs and many corporate
   ATSs license the same parsing engines (Sovren/Textkernel, HireAbility, Affinda).
   Parse-friendly formatting therefore transfers across most systems:
   single-column, standard section headings, real text (no tables/text-boxes/images),
   `MM/YYYY` dates, common fonts.
2. **Matching is keyword-literal first, semantic second.** "AI-driven relevancy scores"
   and "bimetric scoring" reward literal must-have-skill/keyword coverage from the
   JD, with embedding-based semantic similarity as a secondary layer. → The scorer
   weights literal keyword coverage and must-have hit-rate heavily; semantic match
   secondary.
3. **Acronym + spell-out pairing** ("Search Engine Optimization (SEO)") covers both
   tokenized keyword search and recruiter Boolean queries.
4. **The system of record is the ATS** — a human recruiter often *searches* the
   candidate DB. So surfacing in keyword/Boolean search results matters as much as
   passing an auto-gate.

---

## Killed claims — DO NOT re-introduce (failed 3-vote verification)

- ❌ AI screening "measured" KPI improvements of >25% / cut screening time in half —
  only ever *self-reported perceptions*, not measured.
- ❌ "Workday leads / Bullhorn emerging" framing — roster supported, ranking not.
- ❌ Bullhorn May-2025 launch drove 51% submissions / 22% fill / 85% satisfaction.
- ❌ Clean temp-vs-perm tool split (Bullhorn/Avionte/Vincere = temp; Loxo/etc = perm).
- ❌ AI interviewing "almost universally" handled via ATS integration.
- ❌ Automindz 822-transcript ranking (Loxo 241 / Bullhorn 236 "tied").
- ❌ Several GRID stats restated as independent fact rather than vendor survey.

---

## Caveats (carry into the rubric)

- Headline AI adoption/impact stats (78% / 10% / 55% / 46%) all trace to **one
  vendor survey** (Bullhorn GRID, ~2,300 pros, Nov–Dec 2025) — correlational,
  commercially interested.
- Pricing/positioning rests partly on vendor blogs & aggregators; Bullhorn enterprise
  pricing is not officially published.
- Market-share % (34–50%) varies by how "staffing-agency segment" is defined.

## Open questions (candidates for a future research slice)
- Independent (non-vendor) validation of AI screening impact figures.
- Corporate-ATS (Workday/Greenhouse/Lever) ranking quirks for direct applications.
- Market-share distribution among non-Bullhorn agency platforms.
