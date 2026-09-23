---
id: PL-8GV1
title: docket flight reads a branch that blocks an item it never claimed as a note, so docket next goes on offering an item a grooming pass is parking until the pass merges: PL-8FJK's closure promotion reads only the closed statuses
status: dropped
classes: defect
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py
added: 2026-09-22
closed: 2026-09-23
reason: Counted 2026-09-23 over origin/main's 1,261 commits. Exactly one queue-only commit moved an item from a status docket next offers to blocked under a subject leading with that item's id: PL-9SH6 in #518 on 2026-09-13. The closure shape PL-8FJK recovers has 59, and no collision is recorded. bin/docket show already prints 'Its file is already edited on' and the branch at the step start.md requires before starting. The widening is a fix to what exists, so the pause does not hold it. At one case in 33 days it does not earn a promotion clause, a test and README prose.
---

**Problem.** docket flight reads a branch that blocks an item it never claimed as a note, so docket next goes on offering an item a grooming pass is parking until the pass merges: PL-8FJK's closure promotion reads only the closed statuses

**Found 2026-09-22 by `PL-8FJK`'s session and not built there, because the
owner's request named closure.** A grooming pass that sets an item to
`blocked` in a queue-only commit leading with its id reads as a note, so
`docket next` offers the item until the pass merges; a second session starting
it collides with the pass in the item file and works an item the pass has
parked - the cost `PL-8FJK` removed for a drop. `vcs._own_edit_claims` reads
`CLOSED_STATUSES` at the branch's tip; "a status `docket next` does not offer,
where the base's copy is one it does" is the one-predicate widening. Not
observed yet: nobody has counted how often a pass blocks a startable item in a
queue-only commit, which is the number that says whether this is worth
building.

**Counted 2026-09-23, the number the brief asked for.** The count covers
`origin/main`'s 1,261 commits from 2026-08-21 to 2026-09-23. Of those, 271 are
queue-only, meaning every path they touch is under `docs/items/`. Reading the
`-status:`/`+status:` pairs in those 271:

| A queue-only commit moved an item from `ready` or `needs-decision` to | Moves | Under a subject leading with that id |
| --- | --- | --- |
| `done` or `dropped` (what `PL-8FJK` recovers) | 76 | 59 |
| `blocked` (this item) | 6 | 1 |
| `untriaged` | 0 | 0 |

The one is `PL-9SH6`, blocked on `PL-H46J` in `#518` on 2026-09-13. The other
five moves sit in three commits led by another id: `PL-5WFS` twice, then
`PL-LDHD`. The feed reads only commits whose subject leads with the item's id
(`PL-3W3P`), so the widening would have missed those as well. No collision is
recorded from any of them. `main` holds squash merges, so this counts landed
pull requests rather than the branch commits `flight` walks. That is close
enough for an order of magnitude.

**A weaker cover already reaches the step where the collision starts.**
`.claude/skills/docket/modes/start.md` sends every session that starts an item
to `bin/docket show` first. For an unclaimed queue-only edit to the item's
file, which is this shape, `show` prints `Its file is already edited on` and
the branch name (`FlightReport.editing`, `PL-N1JK`).

**Why it matters, and why it is not built.** When it happens, a second session
works an item a pass has parked, and the two collide in one item file. That
cost is real, but it came to one pass in 33 days with no collision on record,
and `show` already warns the session. Widening the predicate is a fix to what
exists, not a new rule. It changes the condition an existing guard,
`_own_edit_claims`, applies to one promotion, and it adds no command, check or
field, so the generator pause does not hold it. What holds it is the count.
The widening would add a clause, a test and README prose, and keep them up for
good, to catch about one case beside the closure shape's 59. `CLAUDE.md`'s build
gate settles it: "Where the benefit is unclear, the answer is no."

**Generator check.** Already a recorded member of `PL-8FJK`, whose
`root-cause-of:` names it. It was filed the day that head closed, and it is the
evidence behind the head's `generator: live` verdict. It is not a new
mechanism. Dropping this item leaves that record as it stands. The next
unclaimed shape a pass takes is a post-close instance of `PL-8FJK`.
