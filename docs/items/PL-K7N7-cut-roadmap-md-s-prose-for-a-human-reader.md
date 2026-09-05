---
id: PL-K7N7
title: Cut ROADMAP.md's prose for a human reader
priority: P2
effort: M
status: ready
classes: docs
feature: prose-quality
touches: ROADMAP.md
added: 2026-09-05
not-delegable: readability is judged by a person, and no command separates trimmed prose from padded prose. The two that could run are worse than none - a line-count ceiling is met by deleting a rule to reach a number, which is why `check_resident_instructions` refuses one, and `doc_check.py check` passes today
---

**Problem.** `ROADMAP.md` runs to ~2,200 lines and is, in the project owner's
reading (2026-09-05), far more verbose than it needs to be. One of five per-target
items split out of `PL-3VKZ` (rewrite the human-facing markdown prose), which
was `L` and therefore unstartable from the queue.

**Why it matters.** `ROADMAP.md` is the authoritative version and milestone
map, and every session reads it to find out what is in scope. A rule stated in
four sentences where one would do is a rule read past. The standard is **human
readability**, deliberately not `PL-JK0M`'s routing standard for the
agent-facing instruction files.

**The qualifier.** The version table, the frozen debt-gate lists, the current
baseline mark and the milestone `Required scope` blocks are read by
`bin/docket wave`, `bin/docket gate` and `tools/doc_check.py`, not only by a
person. Cut the prose around them; do not restructure them, and do not shorten
a milestone's scope statement into something that no longer places the items it
places.

**Where.** `ROADMAP.md`. Counts are measured 2026-09-05 and rounded because they move every release; re-measure before starting rather than trusting them - they are here for ordering, not as a claim.

**Done when.** The document has been read end to end and cut: no paragraph
restating the one above it, no clause that adds nothing. Every recorded
decision still states its reason. `make check` passes, so the release train,
the current baseline and the release tags all still resolve, and `bin/docket
wave` reports the same beat it reported before the edit.
