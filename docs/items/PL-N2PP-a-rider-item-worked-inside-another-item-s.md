---
id: PL-N2PP
title: A rider item worked inside another item's session is invisible to every in-flight guard the project has
priority: P3
effort: M
status: done
classes: defect, infra
feature: carrier-detection
milestone: v0.5.6
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/vcs.py
added: 2026-09-20
closed: 2026-09-22
pr: 924
verify: grep -q 'Do the same the moment you pick up a second item' .claude/skills/docket/modes/start.md && grep -q 'def test_an_empty_commit_leading_with_an_id_claims_the_item_before_any_work' subprojects/docket/tests/test_vcs.py && uv run pytest -q subprojects/docket/tests/test_vcs.py -k an_empty_commit_leading_with_an_id_claims_the_item
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

**Done when.** A rider item's id is visible to at least one guard - `bin/docket
show`, `bin/docket flight`, or the session listing - from the moment its work
starts rather than from the moment its work is pushed; or this item records
which of the candidates was measured and why none of them pays.

**Decision needed.** Which guard, if any, should learn to see a rider: the
capture commit's id read as a soft claim, the session title carrying both ids,
or neither - accepting that a rider is unguarded and saying so where a session
would read it.

**Recommended:** read the capture commit's id as a soft claim, and do not
touch the title convention. The rider's item is pushed before its work in the
ordinary case - `PL-D9K3` was filed before it was worked - so the signal
already reaches the remote with no new obligation on anybody, and `bin/docket
show` is the command that was already run and already fetched in the observed
collision. The title route was measured and fails: a rename rule of this shape
was followed nine times in twenty (2026-09-02), and a guard that fires four
times in five trains a reader to discount it, which is worse than no guard.
Whatever is built must read as "a session may be holding this" rather than as
"work in flight" - `PL-1X2C` is the other half of this event and is what a
guard firing wrongly costs.

**What would change the answer.** How often a rider is filed and worked in one
session without its id reaching the remote first. One instance is recorded; if
that is the only shape, the soft claim closes the whole gap and nothing else is
needed.

**Closed 2026-09-22 by the start rule, not by the soft claim recommended
above.** `PL-7TVT`'s design round took the explicit route instead: an empty
commit leading with the id, pushed the moment an item is picked up, is a claim
every guard already reads - `_annotates_only` treats a commit with no diff as
work - and `.claude/skills/docket/modes/start.md` now says to push one "the
moment you pick up a second item - a rider filed as housekeeping". That makes a
rider's id visible to `show` and `flight` from the moment its work starts, which
is the **Done when.**, and it needed no code;
`test_an_empty_commit_leading_with_an_id_claims_the_item_before_any_work` pins
what it rests on. The soft claim was not built because it reverses `PL-X3WZ`:
reading a capture commit as a claim is what took startable items out of `docket
next`. What stays open is compliance - a session that skips the claim is still
invisible until its first push - and the session-list read in rule 14 is the
backstop for that.
