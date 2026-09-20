---
id: PL-N2PP
title: A rider item worked inside another item's session is invisible to every in-flight guard the project has
status: untriaged
feature: carrier-detection
added: 2026-09-20
---

**Problem.** A rider item worked inside another item's session is invisible to every in-flight guard the project has

**Why it matters.** Every in-flight guard this project has keys on an item id
appearing somewhere a reader can see it - the session title, the branch name,
the commit subject, the item's own status. A *rider* - a second item worked
inside a session held open for a different one - satisfies none of them until
its commit is pushed, and the commit subject is the only one it ever satisfies.
So the window the guards exist to close stays open for the whole of the rider's
work, and it closes for the reader only after the push it was meant to prevent.

**Observed 2026-09-20.** A session titled `PL-PQC7 Closing an item does not ask
what it unblocks` filed `PL-D9K3` (promote or re-point `PL-B8MK`) as
housekeeping and worked it as a rider. Meanwhile a second session was asked to
promote `PL-B8MK` directly. Each of the checks the `docket` skill prescribes
was run by the second session and each returned a clean answer:

- `bin/docket show PL-B8MK`, fetched, at session start - clean, correctly: the
  rider had not been pushed yet.
- `list_sessions` (`mine: true`) - the other session was `RUNNING` and its
  title carried `PL-PQC7`, not `PL-B8MK`. The skill says to scan titles and
  `current_branches` for the id; neither carried it, because the rider is not
  what the session is named after.
- `bin/docket flight` - nothing, for the same reason as the first.

All three were clean and all three were right. The collision was real anyway.

**What might actually close it, none of it obvious.** The rider's *item* is
pushed before its work in the usual case - `PL-D9K3` was filed before it was
worked - so an id that reaches the remote in a capture commit could be readable
as "a session is holding this" if anything looked. Alternatively the session
title could carry both ids, which costs a rename and is the kind of rule that
is followed about three times in four (measured 2026-09-02, nine of twenty
titles). Neither is a clear win and this item is a place to think about it, not
a specification.

**Sits beside `PL-1X2C`** (`bin/docket show` names the reader's own branch),
which is the other half of the same event: that one is a guard firing wrongly,
this one is no guard being able to fire at all.
