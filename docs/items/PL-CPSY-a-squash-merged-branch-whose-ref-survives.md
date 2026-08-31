---
id: PL-CPSY
title: A squash-merged branch whose ref survives reports its items in flight forever
status: untriaged
feature: parallel-sessions
added: 2026-08-31
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
