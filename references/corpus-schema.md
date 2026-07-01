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
