---
id: PL-PTD8
title: A merge that resolves an add/add conflict on an item file still reports nothing when the second copy arrives by a route PL-MTHC does not close - a live branch with no pull request open yet, a forge that could not be asked, or a copy made by hand - so a resolution keeping one side whole can still drop the other's edits silently
priority: P3
effort: S
status: dropped
classes: defect
feature: merge-skew
touches: subprojects/docket/src/docket, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-09-30
closed: 2026-10-12
reason: counted 2026-10-12 against origin/main at 919ad967: no add/add merge on an item file in the 6 merge commits across the remote's 3 branches, and no closed item or recorded pull-request body since PL-MTHC (2026-09-30) records a lost edit; the brief said one found would change the answer, and none was
---

**Problem.** A merge that resolves an add/add conflict on an item file still reports nothing when the second copy arrives by a route PL-MTHC does not close - a live branch with no pull request open yet, a forge that could not be asked, or a copy made by hand - so a resolution keeping one side whole can still drop the other's edits silently

**Lead, from PL-MTHC's session (2026-09-30).** PL-MTHC closed the two routes
that handed out the copy (`claim`'s refusal and `stranded`'s recovery) where
the forge answers; it left the merge itself as silent as before. The loss is
decidable at the merge commit: for an item file both parents hold and their
merge base does not, the lines the incoming side has that the branch's *first
added* copy lacked are the edits made since the copy, and any of them missing
from the merge result were dropped. That excludes lines the branch rewrote on
purpose, which a plain "the result lacks the other side's lines" test would
flag. Whether a merge-time check earns its place against how rarely a copy now
arrives is the triage question; count the add/add merges on item files in
`main`'s history before building it.

**Why it matters.** An add/add resolution keeping one side whole drops the other side's edits to an item file with nothing reporting it, and the queue is the project's only memory between sessions, so a lost edit is a lost brief or decision. `PL-MTHC` closed the routes that hand out the copy where the forge answers; this is the residue.

**Done when.** The count below is recorded here with its date, and the item is either built - a check reporting dropped lines at the merge, with a test - or dropped with the count as its reason.

**Decision needed.** Whether a merge-time check earns its place. The answer rests on a count, so it is a session's: the add/add merges on item files since `PL-MTHC` landed. `main` squash-merges, so its history holds no resolutions; the count reads live branch refs and closed items recording a lost edit. **Recommended:** build it only if the count finds one; otherwise drop it with the count as the reason. One lost edit found since `PL-MTHC` is the number that would change that.

**Generator check.** The fact is which copy of an item file carries the edits after two branches each add it, `PL-MTHC`'s ground; this is the residual route that session named as a lead, the remainder of that fix rather than a post-close instance. One-off.

**Counted 2026-10-12, in the first batched design round, against
`origin/main` at 919ad967.** Live branch refs: the remote holds 3 branches
(`main` and two `claude/*` branches; `branch-sweep.yml` deletes finished ones
daily) with 6 merge commits between them not on `main`, and none resolves an
add/add on a file under `docs/items/` - an item file both parents hold and
their merge base lacks. Closed items: none closed on or after 2026-09-30
records a lost edit; the only mentions of add/add since are `PL-S0MB`'s
feature table naming this item, and `PL-0F33` and `PL-DQ9C` mention conflicts
of other kinds. Pull-request bodies: none recorded since 2026-09-30 mentions
one (`docs/pr-bodies/1077.md`, 2026-09-26, is `PL-MTHC`'s own). The count
reads only what can be read, as the brief said it would: a resolution made on
a branch that has since merged and been swept is gone, so it bounds what is
visible and not what happened.

**Dropped** (2026-10-12, a session's call, as the brief says): the count found
no lost edit since `PL-MTHC`, which is the number the brief named as the one
that would change the answer. A merge-time check built against zero observed
instances would fire on nothing and cost its upkeep. One lost edit found later
reopens it: file it with the merge commit and the dropped lines, and the lead
paragraph above has the decidable test.
