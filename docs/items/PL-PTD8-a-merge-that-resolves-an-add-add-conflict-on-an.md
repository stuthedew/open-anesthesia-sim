---
id: PL-PTD8
title: A merge that resolves an add/add conflict on an item file still reports nothing when the second copy arrives by a route PL-MTHC does not close - a live branch with no pull request open yet, a forge that could not be asked, or a copy made by hand - so a resolution keeping one side whole can still drop the other's edits silently
status: untriaged
feature: queue-hygiene
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
