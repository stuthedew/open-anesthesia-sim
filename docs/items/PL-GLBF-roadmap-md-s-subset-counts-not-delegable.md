---
id: PL-GLBF
title: ROADMAP.md's subset counts - not-delegable, entries reaching into src/ - are still hand-maintained and unchecked
priority: P3
effort: S
classes: defect, docs
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
status: needs-decision
added: 2026-09-01
---

**Problem.** PL-H8MQ made every count of a frozen list's *size* checkable, and
removed the prose restatements a checker cannot safely read. What it did not
touch are the counts of a *subset* of a list, which state a property of the
entries rather than the list's length. Live examples, all hand-maintained:

- "**Seven entries are marked `not-delegable`,**" in the v0.2.8 section
- "The two entries that change repository configuration rather than the tree"
- "Three entries reach into `src/`" in the definition of done

**Why it matters.** Each goes stale the next time an entry with that property
is admitted or closed, and none of them fails anything. The same failure PL-H8MQ
describes, one level down: on 2026-09-01 the v0.3.0 section still said its
contents were "the fourteen listed under Debt gate" when the list had held
twenty since six entries were added — a reader would have thought the release
shipped fourteen items. That one was found by hand while working PL-H8MQ, not
by a check.

**Where.** `ROADMAP.md`; `tools/doc_check.py`'s `check_gate_counts`, which
already has the entries parsed and reports at the right granularity.

**Approach.** The `not-delegable` count is the one worth doing first, because
it is decidable without judgment: `docket` reads `not-delegable:` off each
item, so the count is a query over the entries the gate already names. The
other two describe what an entry's *work* touches, which no field records —
those are either left to the reader (and then the number should come out of
the prose, per PL-H8MQ's rule) or need a field that does not exist yet. Decide
which before writing anything: a check that guesses the judgment half is worse
than no check.

**Done when.** A subset count in `ROADMAP.md` either fails `make check` when it
disagrees with the items, or has been removed from the prose because nothing
can decide it.

**Triaged 2026-09-01 to `needs-decision`, not to `ready`.** The fields are
filled in - `P3`, `defect`/`docs`, `dev-tooling`, beside `PL-H8MQ`, whose work
this continues - but the item cannot be started, because its own **Approach.**
names a decision that has to come first and this triage pass deliberately did
not make it.

**Decision needed.** Whether the two counts that describe an entry's *work* -
"the two entries that change repository configuration" and "three entries reach
into `src/`" - come out of `ROADMAP.md`'s prose, or whether an item gains a
field recording what its work touches so a checker can decide them. The
`not-delegable` count needs no decision and is checkable either way.

Stated at length: the `not-delegable`
count is a query over fields `docket` already reads and can simply be checked.
The other two - "the two entries that change repository configuration" and
"three entries reach into `src/`" - describe what an entry's *work* touches,
which no field records. So either those two numbers come out of the prose (per
`PL-H8MQ`'s rule that a count nothing can decide should not be written down),
or an item gains a field that records what its work touches at that
granularity, which is a larger change and one that would need filling in
across the gate.

No `verify:` yet, and that is correct rather than missing: the command depends
on which answer is taken, and `docket check` owes one only at `ready`.
