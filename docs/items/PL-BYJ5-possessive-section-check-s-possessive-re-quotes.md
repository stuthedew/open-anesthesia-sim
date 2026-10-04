---
id: PL-BYJ5
title: possessive_section_check's POSSESSIVE_RE quotes across a blank line, so a possessive naming a file followed by a quotation a paragraph break separates is read as one quotation equal to a heading, a false names-a-section report; latent
status: untriaged
touches: tools/possessive_section_check.py, tests/unit
added: 2026-10-04
---

**Problem.** possessive_section_check's POSSESSIVE_RE quotes across a blank line, so a possessive naming a file followed by a quotation a paragraph break separates is read as one quotation equal to a heading, a false names-a-section report; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

The quotation `[^"]{2,200}?` under DOTALL crosses a blank line, so the lines below are read as the quotation "What this project is", which equals a heading:

```markdown
`CLAUDE.md`'s "What this

project is"
```

The opposite direction from `PL-R417`'s, and its only consequence is a false report; `PL-XW87`'s soft break, block quote and list indent forms still read right. Latent.
