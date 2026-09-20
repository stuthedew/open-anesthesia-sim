---
id: PL-QNQJ
title: origin/claude/practical-brown-wr7u6i outlives PL-66Z5 by design, carries a ROADMAP.md paragraph main has never held, and keeps PL-ZM48 marked in flight
status: untriaged
added: 2026-09-20
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

- It still stands. `git ls-remote --heads origin 'refs/heads/claude/*'` returns
  four, of which three are live sessions and this is the fourth.
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
this is roadmap prose, which is a gap worth noting on its own.

**Why it matters.** A spent ref that no item covers is invisible work: it
suppresses a real item from the queue, and the one check that would report a
branch carrying something `main` lacks does not look at roadmap prose. The
analogous case cost `PL-XLQ5` a recovery.

**Done when.** The branch's `ROADMAP.md` paragraph is recorded as superseded or
carried onto `main`, and the ref is gone. Deleting a ref on the remote stays the
project owner's (`PL-K2C8`).
