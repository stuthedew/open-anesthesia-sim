---
id: PL-FFG9
title: docs/WORKING_NOTES.md's scenario-branching thread states its own exit condition - 'the thread stays open until item 26 is scoped' - and item 26 shipped in v0.5.0, so the thread reads as live design work on something already built
priority: P3
effort: S
status: ready
classes: docs
feature: doc-consistency-checks
touches: docs/WORKING_NOTES.md
added: 2026-09-21
payoff: a session reading the working notes for branching context stops finding a live design thread on something v0.5.0 shipped
verify: ! grep -q '^## Open thread: scenario branching, bookmarks' docs/WORKING_NOTES.md
---

**Problem.** docs/WORKING_NOTES.md's scenario-branching thread states its own exit condition - 'the thread stays open until item 26 is scoped' - and item 26 shipped in v0.5.0, so the thread reads as live design work on something already built

The thread at `docs/WORKING_NOTES.md:486` - "Open thread: scenario branching,
bookmarks, and what a snapshot is for - PL-DHV7, ROADMAP items 8, 11, 12 and
26" - ends its 2026-08-25 triage note with "The thread stays open until item 26
is scoped." Item 26 was scoped into v0.5.0 on 2026-09-06 and shipped on
2026-09-21, so the condition the thread names for its own closure was met
fifteen days before it shipped and nothing read it.

**Why it matters.** `docs/WORKING_NOTES.md` is what a session reads for the
narrative behind an open thread, and `bin/docket show` splits it at its `##`
headings to name the threads concerning the item being shown. A thread that
reads as live design work on branching and bookmarks will be opened by a
session working anything near them, and the measurements and reasoning in it
are written in the future tense about a feature that now exists - so the cost
is a session re-deriving a design question v0.5.0 already answered, in the
document the project keeps specifically to stop that.

**Done when.** The thread's heading no longer begins `## Open thread: scenario
branching, bookmarks` - it is retitled the way this file's other closed threads
are, `Settled:` or `Decided:` with the date - and the thread carries a dated
closing note saying what shipped and where the record now lives:
`ROADMAP.md`'s v0.5.0 section for the milestone, the items for the individual
decisions. The retitle is required in every outcome, which is what the
`verify:` command tests. Where part of it is genuinely still open, split that
part out under its own `## Open thread:` heading rather than holding the whole
thread open for it. `PL-DHV7` is the one queue item the 2026-08-25 triage note
left startable, and its status is the thing to read first: if it is still open,
that is the part to split out.

**The first `verify:` written for this item proved nothing, and the way it
failed is worth keeping.** It was `grep -q 'The thread stays open until item 26
is scoped' docs/WORKING_NOTES.md && exit 1 || exit 0` - but that sentence is
line-wrapped in the file between `is` and `scoped`, and `grep` is line-based,
so the phrase never matched and the command passed on the day it was written.
`bin/docket check --verify` caught it in CI on `#850`; `make check` does not run
that flag locally, which is `PL-J3WK`.
