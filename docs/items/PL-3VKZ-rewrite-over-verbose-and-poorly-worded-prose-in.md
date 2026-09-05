---
id: PL-3VKZ
title: Rewrite over-verbose and poorly worded prose in the human-facing markdown documents
status: untriaged
feature: prose-quality
touches: docs, ROADMAP.md
added: 2026-09-05
---

**Problem.** The human-facing markdown documents are, in the project owner's
reading (2026-09-05), far too verbose and poorly written — the same complaint
as `PL-XXBD` (the code-comment pass), against prose a person reads directly.

**Why it matters.** The standard is **human readability**: these are the
documents a reader meets when deciding what the simulator is and whether to
trust it, so verbosity costs comprehension, not merely space. Same standard as
`PL-XXBD`, and deliberately *not* the standard in `PL-JK0M` (route or justify
the resident instruction lines) — see that item for why the agent-facing files
are measured differently.

**Where.** Candidates by size, measured 2026-09-05 and rounded because they
move every release: `docs/MODEL.md` (~3100 lines), `ROADMAP.md` (~2200),
`docs/WORKING_NOTES.md` (~700), `docs/ARCHITECTURE.md` (~520),
`docs/maintainer.md` (~50). Re-measure before starting rather than trusting
these; they are here for ordering, not as a claim.

Two exclusions, both deliberate:

- **`README.md` is excluded.** It is frozen by `.claude/rules/readme-hold.md`
  until the project owner lifts it; `PL-RM83` (decide what README.md is for) is
  the decision that unblocks it and `PL-N092` (rewrite README as a
  human-readable introduction) is the rewrite. The freeze exists for exactly
  this failure mode — successive sessions each improving a paragraph in
  isolation while the document got worse — so a prose pass is the last thing
  README should get before its audience is settled.
- **`docs/MODEL.md` is held to the specialist standard**, not merely to
  readability. Trim prose there; never trim an equation, a unit, an assumption,
  a limitation or a provenance note. Where a passage is long because the
  science is, it stays long.

`docs/WORKING_NOTES.md` needs a scope decision of its own at triage: it is a
working log of open threads rather than a document with a reader, so "too
verbose" may not be a defect in it at all.

**Done when.**
