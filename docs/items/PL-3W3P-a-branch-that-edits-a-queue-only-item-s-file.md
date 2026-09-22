---
id: PL-3W3P
title: A branch that edits a queue-only item's file for another item's reason claims that item: PL-0HPV's verify: reorder pass made docket flight report PL-LBW5, PL-RWBV, PL-YVV4 and PL-YZKK in flight on claude/kind-cerf-mizfzd, hiding them from docket next until #920 merges
status: untriaged
added: 2026-09-22
---

**Problem.** A branch that edits a queue-only item's file for another item's reason claims that item: PL-0HPV's verify: reorder pass made docket flight report PL-LBW5, PL-RWBV, PL-YVV4 and PL-YZKK in flight on claude/kind-cerf-mizfzd, hiding them from docket next until #920 merges

**Observed 2026-09-22, by the session that ran the pass.** Each of the four
declares `touches: docs/items` and nothing else, and none of this branch's
commit subjects names them; the reorder commit, led by `PL-0HPV`, rewrote their
`verify:` lines along with 92 others whose `touches` reach past the queue, and
only the four queue-only ones were marked. So the claim comes from
`vcs._queue_only_work`'s reading (`PL-7790`) - an edit to a queue-only item's
file is taken as that item's own work - rather than from a subject. It clears
itself once the branch merges; the cost is the window in between, and any
future pass over many item files will pay it again.
