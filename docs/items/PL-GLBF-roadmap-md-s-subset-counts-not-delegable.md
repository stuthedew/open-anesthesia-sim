---
id: PL-GLBF
title: ROADMAP.md's subset counts - not-delegable, entries reaching into src/ - are still hand-maintained and unchecked
status: untriaged
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
