---
id: PL-TGFY
title: PL-Z34C is a frozen gate entry that qualified as needs-decision, has since moved to blocked, and is no longer debt by any class - so the gate holds an entry nothing can clear
priority: P3
effort: S
status: needs-decision
classes: planning
feature: gate-remaining-cost
touches: ROADMAP.md, docs/items
added: 2026-09-20
payoff: stops the gate holding an entry nobody can clear, which is 12 of the 13 prerequisites standing between the project and the milestone
---

**Problem.** PL-Z34C is a frozen gate entry that qualified as needs-decision, has since moved to blocked, and is no longer debt by any class - so the gate holds an entry nothing can clear

**What was verified, 2026-09-20.** At the 2026-09-06 freeze `PL-Z34C` read
`status: needs-decision` with `classes: infra, session-cost` (commit
`d1d0b86`, the newest touching the file before the freeze). `needs-decision` is
what made it debt and put it on the gate; its classes never were debt classes.
Its status has since moved to `blocked`, so `bin/docket gate` no longer counts
it as debt at all — it appears zero times in that command's output today.

**Why it matters.** The list is frozen by design and a frozen entry does not
leave because its classification moved, which is right. But this entry also
cannot be *worked*: its "done when" is a standing condition — when the
grandfathered `verify:` set reaches zero — and that set empties as each of 12
unrelated open items is started, not by anyone pushing on `PL-Z34C`. So the gate
holds an entry no session can clear, and it is the single largest contributor to
the off-gate prerequisite count `PL-FCM3` measures: 12 of the 13.

**Decision needed.** Whether a frozen gate entry that is no longer debt, and
whose completion is a standing condition rather than a piece of work, stays on
the list. This turns on what the gate is for, so it is the project owner's.
`ROADMAP.md`'s staleness sweep (beat 3, standing item `PL-6ZQY`) is the existing
mechanism if the answer is that it comes off; the entry is not *wrong*, so
"drop what no longer reproduces" does not obviously reach it.

**Done when.** `ROADMAP.md` records a decision on whether `PL-Z34C` stays on
v0.5.0's frozen list — either the entry is swept off with its reason under the
staleness beat, or the section states why an entry that is no longer debt and
cannot be worked is kept. Either way `bin/docket wave`'s count of what the gate
is waiting on reflects the answer.
