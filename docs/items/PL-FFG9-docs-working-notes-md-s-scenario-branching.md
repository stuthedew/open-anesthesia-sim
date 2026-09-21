---
id: PL-FFG9
title: docs/WORKING_NOTES.md's scenario-branching thread states its own exit condition - 'the thread stays open until item 26 is scoped' - and item 26 shipped in v0.5.0, so the thread reads as live design work on something already built
priority: P3
effort: S
status: done
classes: docs
feature: doc-consistency-checks
touches: docs/WORKING_NOTES.md
added: 2026-09-21
closed: 2026-09-21
pr: 858
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

## Closed 2026-09-21 by `PL-DL4M`'s deletion, and deletion is why the outcome
## differs from the one asked for

`PL-DL4M` deleted the thread outright rather than re-heading it, so the
heading this item's `verify:` tests for is gone and the command passes.
`bin/docket check --verify` caught that on `#858` as *"open but its `verify:`
command already passes"*, which is the right error and the first of the two
dispositions it names: the work landed.

**The `verify:` discriminated, which is what makes this a close rather than a
rewrite.** `! grep -q '^## Open thread: scenario branching, bookmarks'` fails
against `origin/main`, where the heading is present, and passes against the
branch that removed it. Both were run before this was closed - the second
disposition the error offers, a command that proves nothing, does not apply.

**What this item asked for and did not get, decided rather than overlooked.**
The *Done when* above asks for a `Settled:` or `Decided:` retitle plus a dated
closing note in the file. `PL-DL4M` deleted instead, on `docs/WORKING_NOTES.md`'s
own header policy - a fully resolved thread "should be deleted rather than left
stale" - and on the finding that a retitle here would have re-blessed a framing
`ROADMAP.md` item 12's *Branch points* note already records as superseded. The
"where the record now lives" half is discharged in `PL-DL4M`'s close-out, which
names the successor for each part: `ROADMAP.md` items 8, 11, 12 and 26, the
v0.5.0 section, `tests/unit/test_bookmarks.py` and
`tests/reference/test_canonical_evaluation.py`.

The one condition this item set for splitting - *"`PL-DHV7` is the one queue
item the 2026-08-25 triage note left startable, and its status is the thing to
read first"* - is satisfied: `PL-DHV7` is `done`, so nothing was left open to
split out.

**This is a repeat filing, and that is the evidence rather than a nuisance.**
`PL-DL4M` named this same thread on 2026-09-14 as one of three; this was filed
independently on 2026-09-21 against the same heading. Two sessions finding the
same stale thread six days apart is `PL-DG84`'s case, which is being built
concurrently as a grooming advisory - it needs no new record here beyond the
count.
