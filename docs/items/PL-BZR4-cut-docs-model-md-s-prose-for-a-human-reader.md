---
id: PL-BZR4
title: Cut docs/MODEL.md's prose for a human reader, without losing an equation, unit, assumption, limitation or provenance note
priority: P2
effort: M
status: ready
classes: docs
feature: prose-quality
touches: docs/MODEL.md
added: 2026-09-05
not-delegable: `docs/MODEL.md` is a `protected_paths` entry, so no delegated diff may touch it whatever a check proves. Readability is judged by a person besides - no command separates trimmed prose from padded prose, and a length ceiling would be met by deleting the provenance note this item exists to keep
---

**Problem.** `docs/MODEL.md` runs to ~3,100 lines and is, in the project
owner's reading (2026-09-05), far more verbose than it needs to be. One of five per-target
items split out of `PL-3VKZ` (rewrite the human-facing markdown prose), which
was `L` and therefore unstartable from the queue.

**Why it matters.** This is the document a reader opens to decide whether to
trust a displayed number - which model is running, what a value means, what the
implementation assumes. Verbosity there costs comprehension rather than space:
a limitation buried in the third clause of a long paragraph is a limitation the
reader does not find. The standard is **human readability**, deliberately not
`PL-JK0M`'s routing standard for the agent-facing instruction files.

**The qualifier that makes this different from the other four.** `CLAUDE.md`
holds `docs/MODEL.md` to the specialist standard, not merely to readability.
Trim prose; never trim an equation, a unit, an assumption, a limitation, or a
provenance note. Where a passage is long because the science is, it stays long.
The failure this item must not produce is a shorter document that says less
about what the model cannot do.

**Where.** `docs/MODEL.md`. Counts are measured 2026-09-05 and rounded because they move every release; re-measure before starting rather than trusting them - they are here for ordering, not as a claim.

**Done when.** The document has been read end to end and cut: no paragraph
restating the one above it, no clause that adds nothing, no section that could
be a sentence. Every equation, unit, assumption, limitation and provenance note
still says what it said. `make check` passes, so no citation, provenance-table
row, package-map entry or math block was broken by the edit.
