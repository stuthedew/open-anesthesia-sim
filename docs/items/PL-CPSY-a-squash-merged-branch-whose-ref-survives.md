---
id: PL-CPSY
title: A squash-merged branch whose ref survives reports its items in flight forever
priority: P2
effort: S
status: ready
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md
added: 2026-08-31
verify: uv run pytest subprojects/docket/tests/test_vcs.py -k squash
---

**Problem.** `branches_in_flight` excludes a branch by containment: a ref
whose tip `--merged=origin/main` names is finished. A squash merge writes one
new commit onto `main` and contains none of the branch's own, so the branch is
never merged by that test and its ref stays a candidate for as long as the
checkout holds it. Every id that leads one of its commit subjects then reports
as in flight, permanently.

`PL-S4M2` (switch main to squash-merge, so each item lands as one commit)
landed on 2026-08-30, so this is the merge strategy the project uses now, not
a hypothetical one. `stranded` already documents the same trap from the other
side: "a squash-merged branch is never contained in the default branch, so a
containment test calls it unmerged forever".

**Why it matters.** `in_flight_ids` feeds `docket next`, which excludes what
is in flight - so a stale ref makes `next` skip items that are finished and
startable, with no way for the reader to tell. `PL-KWC1` (read in-flight work
from the commits, not the branch name) widened the exposure without creating
it: before, a stale ref hid the one id in its name; now it hides every id
leading a commit on it.

Two things hold it down today, and neither is a guarantee. GitHub deletes the
head branch on merge where the repository is configured to, and an agent
session's container is a fresh clone that never holds a deleted ref. A
long-lived local checkout that does not prune is the case that breaks.

**Where.** `subprojects/docket/src/docket/vcs.py` - `branches_in_flight`. The
containment test is the mechanism at fault, not the commit read.

**Done when.** An item whose branch was squash-merged and whose ref this
checkout still holds is not reported in flight, and a regression test covers
the case. Whether that is a tree comparison like `stranded`'s, a pull-request
number read off the branch, or something narrower is the design work.

**Triaged 2026-08-31.** P2, `defect`/`infra`, `parallel-sessions` alongside
`PL-KWC1` (read in-flight ids from the commits, not the branch name) and
`PL-S1P1` (the refs that went unread never reach `docket next`). All three are
`vcs.py`, and `PL-S1P1` touches the same function's return value, so the two
collide on `touches` by design rather than by accident - work them in one
session or serialize them.

P2 rather than P3 despite nothing having been observed: the failure direction
is the dangerous one. `PL-SRCP`'s counterpart defect makes finished work
*visible*, and this one makes startable work *invisible*, with no line of
output saying so. `README.md` is in `touches` because `stranded`'s docstring
already documents this exact trap from the other side, and the fix should
leave one statement of it rather than two.

Not admitted to v0.2.8's frozen list. It is close: `PL-KWC1` is an entry, and
this widens the same blindness. But `PL-KWC1` is `done` and its own claim -
that a harness-named branch's ids are read - holds; a stale ref is a second
mechanism, present before `PL-KWC1` and unchanged by it, so this is a new
finding rather than the completion of one. `ROADMAP.md`'s "What the freeze
closes" sends it to the queue.
