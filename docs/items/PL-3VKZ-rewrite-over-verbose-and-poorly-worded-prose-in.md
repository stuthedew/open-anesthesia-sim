---
id: PL-3VKZ
title: Rewrite over-verbose and poorly worded prose in the human-facing markdown documents
priority: P2
effort: L
status: ready
classes: docs
feature: prose-quality
touches: docs/MODEL.md, docs/ARCHITECTURE.md, docs/maintainer.md, ROADMAP.md
added: 2026-09-05
not-delegable: prose quality is judged by a reader, and no command separates trimmed prose from padded prose. The two that could run are worse than none - a line-count ceiling is met by deleting a paragraph to reach a number, which is why `check_resident_instructions` refuses one, and `doc_check.py check` passes today. `docs/MODEL.md` is a protected path besides
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

**Where.** Candidates by size: `docs/MODEL.md` (3089 lines), `ROADMAP.md`
(2183), `docs/WORKING_NOTES.md` (705), `docs/ARCHITECTURE.md` (513),
`docs/maintainer.md` (49).

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

**`docs/WORKING_NOTES.md` is out of scope, decided at triage (2026-09-05).**
Its reader is the next session rather than a person deciding what the simulator
is, and `docket.toml`'s `workflow_paths` already counts it as apparatus rather
than product - so `CLAUDE.md`'s "working reliably and staying streamlined"
governs it, not the specialist prose standard this item applies. Length there
is a symptom of a thread still being open, and it is paid off by closing the
thread rather than by rewriting the note.

**Done when.** `docs/MODEL.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md` and
`docs/maintainer.md` have each been read end to end and cut for a human
reader: no paragraph restating the one above it, no clause that adds nothing,
no section that could be a sentence. Every equation, unit, assumption,
limitation and provenance note in `docs/MODEL.md` still says what it said, and
`make check` passes, so no citation, package-map entry or math block was broken
by the edit.
