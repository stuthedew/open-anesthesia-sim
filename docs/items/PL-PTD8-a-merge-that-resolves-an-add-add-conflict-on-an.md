---
id: PL-PTD8
title: A merge that resolves an add/add conflict on an item file still reports nothing when the second copy arrives by a route PL-MTHC does not close - a live branch with no pull request open yet, a forge that could not be asked, or a copy made by hand - so a resolution keeping one side whole can still drop the other's edits silently
priority: P3
effort: S
status: needs-decision
classes: defect
feature: queue-hygiene
touches: subprojects/docket/src/docket, subprojects/docket/tests
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-09-30
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
