---
id: PL-3VKZ
title: Rewrite over-verbose and poorly worded prose in the human-facing markdown documents
status: dropped
added: 2026-09-05
closed: 2026-09-05
reason: split into three per-document items, with the project owner's agreement (2026-09-05), because at `L` this could not be started from a queue entry - the whole of `PL-72V3`'s triage of it was undone by that. Nothing is lost and nothing is added: PL-BZR4 takes `docs/MODEL.md` and carries the specialist-standard qualifier, PL-K7N7 takes `ROADMAP.md`, and PL-TPS7 takes `docs/ARCHITECTURE.md` and `docs/maintainer.md` together. The two exclusions this item settled hold in all three - `README.md` stays frozen by `.claude/rules/readme-hold.md`, and `docs/WORKING_NOTES.md` is out because `docket.toml`'s `workflow_paths` counts it apparatus, so the specialist prose standard does not reach it. The body below is the reasoning; it was not rewritten into any child
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
