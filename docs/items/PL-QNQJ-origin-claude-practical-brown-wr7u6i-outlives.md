---
id: PL-QNQJ
title: origin/claude/practical-brown-wr7u6i outlives PL-66Z5 by design, carries a ROADMAP.md paragraph main has never held, and keeps PL-ZM48 marked in flight
priority: P2
effort: S
status: done
classes: docs
feature: remote-ref-deletion
milestone: v0.4.33
touches: ROADMAP.md, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 754
payoff: the debt gate keeps the reason PL-ZM48 was declined instead of filing it under a ground it does not meet, and the last superseded ref goes without taking prose main never had
verify: grep -qF 'after the freeze and declined with it' ROADMAP.md
---

**Problem.** `origin/claude/practical-brown-wr7u6i` outlives `PL-66Z5` by
design, carries a `ROADMAP.md` paragraph main has never held, and keeps
`PL-ZM48` marked in flight.

**Measured 2026-09-20**, while running the refresh rule 14 of
`.claude/rules/instruction-writing.md` requires before a closing block.

**This item was first filed on a misreading, and the correction is the
finding.** It originally said `PL-66Z5` ("delete the ten superseded `claude/*`
branch refs") had one ref left to go. It does not: its `verify:` names ten refs
explicitly, all ten are deleted, and its own brief excludes
`claude/practical-brown-wr7u6i` in as many words - "this item's own branch".
`PL-66Z5` was simply finished and never closed, which is what reddened `main`
from #744 onward, and it is closed in the same change as this correction.

**What is actually left is a ref no item covers.** `PL-66Z5` could not delete
the branch it was filed on, and nothing else names it:

- It stood when this item was filed: `git ls-remote --heads origin
  'refs/heads/claude/*'` returned four, of which three were live sessions and
  this was the fourth. Re-read while the recovery below was being written, it
  returned one - the project owner had deleted this ref and
  `claude/gallant-cori-a381pf` in between.
- **It carries roadmap prose `main` has never held** - the post-freeze gate
  disposition opening "**`PL-ZM48`, added 2026-09-20, after the freeze and
  declined with it.**", 17 lines explaining why that entry was declined to
  Gate 2. `git show origin/main:ROADMAP.md | grep -c 'after the freeze and
  declined with it'` returns 0; the same grep on the branch returns 1.
- **It keeps `PL-ZM48` marked `IN FLIGHT`**, and `bin/docket next` excludes
  in-flight work, so that item is unreachable except by being named directly.

**Whether the paragraph is a loss needs judgment, not a command.** `main` does
carry `PL-ZM48` in its `### Declined to Gate 2` list, at 209 entries against
the branch's 206 and worded differently - so `main` is the later state and took
a different route to recording the same decision. Whether the paragraph is
superseded prose or a dropped explanation is a read of the two texts.
`bin/docket stranded` cannot see it at all: that check reads item files, and
this is roadmap prose, which is a gap worth noting on its own (`PL-BYMX`).

**Why it matters.** A spent ref that no item covers is invisible work: it
suppresses a real item from the queue, and the one check that would report a
branch carrying something `main` lacks does not look at roadmap prose. The
analogous case cost `PL-XLQ5` a recovery.

**Done when.** The branch's `ROADMAP.md` paragraph is recorded as superseded or
carried onto `main`, and the ref is gone. Deleting a ref on the remote stays the
project owner's (`PL-K2C8`).

**Answered 2026-09-20: carried, not superseded, and the two texts are what
decide it.** The subsection is headed `### Declined to Gate 2 on the
refilling-queue ground`, and its opening prose says of its entries that they
"pass the presence test as squarely as those do, and they are deferred anyway".
`PL-ZM48` does not pass it: the `docs/worker.md` text it corrects was written
under `PL-4Q9B` on 2026-09-19 (`fbd99f0`, #685, shipped in v0.4.28), thirteen
days after the 2026-09-06 freeze, so there was nothing at the freeze for a gate
to hold. `main`'s list entry alone would therefore have filed the decline under
a ground the entry does not meet. That is the same ground `PL-09G9` and
`PL-YFXG` are recorded on, each in a paragraph of its own, and the section says
in as many words why: "saying so is cheaper than stretching the refilling-queue
argument over it". So the paragraph is carried, with two short paragraphs added
naming the ground and the provenance.

**The split is exact: 17 lines carried, one superseded.** The ref's commit
added 18 lines to `ROADMAP.md`. Seventeen are the paragraph and are here
verbatim; the eighteenth is the `### Declined to Gate 2` list entry itself,
which `main` already carries in a later wording that backticks its citations
the way the rest of the file does. So "superseded prose" was the right reading
of one line and the wrong reading of the other seventeen, which is why this
needed the two texts read rather than a count of entries.

**The ref went while this was being written, which is the finding rather than a
complication.** At the start of the session the remote held it; by the time the
paragraph was in the working tree it was gone, deleted by the project owner on
`PL-66Z5`'s conclusion that the superseded refs carry nothing `main` lacks -
which was true of the ten `PL-66Z5` compared file-by-file and not of the
eleventh, the one it excluded for being its own branch. The prose survived only
because this session had already copied it out; on the remote it no longer
exists, and what was left was one container's stale `refs/remotes/` entry.
`PL-BYMX` is that gap: both halves of `bin/docket stranded` are keyed on item
ids, so a branch carrying a non-item file the base lacks is reported by
nothing, and the deletion decision is taken on that answer.
