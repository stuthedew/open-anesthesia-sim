---
id: PL-3CTW
title: A commit that leads with a captured id and also reaches outside the queue claims that id, so a finding filed alongside another item's work reads 'do not start these again' for the life of the branch
status: untriaged
added: 2026-09-19
---

**Problem.** A commit that leads with a captured id and also reaches outside the queue claims that id, so a finding filed alongside another item's work reads 'do not start these again' for the life of the branch

**Observed 2026-09-19, and it cost the opening of a session.** The session
started on `PL-RY2R` and `PL-61MD` read in its own start-up digest: `In flight
on a branch: PL-2BZY, PL-61MD, PL-6P9Y, PL-HWW1, PL-RY2R - do not start these
again`. Both were startable. They had been *filed* on
`origin/claude/tender-keller-omy3ec` by commit `6d2298a`, whose subject is
`PL-RY2R, PL-61MD: file the two remaining collapses, and name the group` and
whose diff also carries `PL-2BZY`'s 159-line `vcs.py` implementation.

**Mechanism.** `leading_ids` reads every id at the front of the subject and
`_annotates_only` withholds the claim only where the *whole* diff sits inside
the queue. A commit that files a finding while implementing something else
satisfies neither test: it leads with the captured ids, and its diff reaches
`src/`. So both captured ids are credited as work in flight.

This is `PL-X3WZ`'s harm through the opposite door. That item stopped a
queue-only commit being read as work; this is a work commit being read as a
claim on the ids it merely captured. `CLAUDE.md` makes both halves mandatory -
capture before the session ends, and lead every subject with its ids - so the
collision is produced by following the rules rather than by breaking them, and
it fires on exactly the commits whose purpose is to hand work to a later
session.

**What it costs.** The mark's whole job is to stop two sessions on one item.
Here it withholds an item nobody holds, for as long as the branch lives, and
`bin/docket next` excludes it under the strongest wording the tool has. A
capture is the one commit shape that should never claim anything.

**A candidate mechanism, not yet a decision.** `_deciding_on_base` and
`_queue_only_work` both answer a question of this kind by asking the *base*
rather than the commit, and the base separates these two cases cleanly: an id
the base does not hold at all is one this commit is filing, because a capture
creates the file. So a leading id whose item the base has no copy of could be
read as captured rather than claimed, independent of what else the diff
touched. That needs counting against the store before it is adopted - how many
historical claims it would withdraw, and whether any of them were real work on
an item whose file had not yet merged - which is the measurement this item owes
and the reason it is not a fix-now.

**Not fixed in the session that found it**, per `CLAUDE.md`'s fix-now door: it
needs a new regression test, so the first test fails outright.
