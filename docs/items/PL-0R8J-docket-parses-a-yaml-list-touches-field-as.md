---
id: PL-0R8J
title: docket parses a YAML-list touches: field as empty, so an item using the list form is offered to no lane and is unanalysed for concurrency
status: dropped
added: 2026-09-13
closed: 2026-09-13
reason: duplicate of PL-FX0K, captured in the same pass and describing the same parser defect
---

**Problem.** docket parses a YAML-list touches: field as empty, so an item using the list form is offered to no lane and is unanalysed for concurrency
**Why it matters.** Nothing on its own: the finding is real and `PL-FX0K` (the
same YAML-list `touches:` parse defect) carries it, captured in the same commit
on the same day. Two open items for one defect split the reasoning across two
files and invite two branches. `PL-FX0K` is the one kept because its title
carries the word that matters - the parse is *silent*, which is the whole
reason the defect is worth fixing.

**Done when.** Dropped at triage, 2026-09-13. `PL-FX0K` carries the work and
the reasoning.
