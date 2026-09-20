---
id: PL-TGFY
title: PL-Z34C is a frozen gate entry that qualified as needs-decision, has since moved to blocked, and is no longer debt by any class - so the gate holds an entry nothing can clear
priority: P3
effort: S
status: done
classes: planning
feature: gate-remaining-cost
milestone: v0.4.32
touches: ROADMAP.md, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 745
payoff: stops the gate holding an entry nobody can clear, which is 12 of the 13 prerequisites standing between the project and the milestone
verify: grep -qF 'makes a thirteenth, on a different ground' ROADMAP.md
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

**Decision (project owner, 2026-09-20, ratified, over keeping the entry on the
frozen list).** `PL-Z34C` comes off v0.5.0's frozen list and takes the
`### Sequenced past v0.5.0, so not clearable before it begins` disposition,
which that subsection already exists to record and which keeps the entry written
as the freeze put it rather than deleting it.

Two grounds, and the first is the one that decides it. Its completion is a
standing condition rather than a piece of work: `verify_required_from` retires
when the grandfathered set reaches zero, and that set drains as each of twelve
unrelated open items is started, never by anyone pushing on `PL-Z34C`. An entry
no session can clear by working it cannot be a precondition on beginning a
milestone. Second, it no longer qualifies as debt at all — it reached the gate at
`needs-decision`, has since moved to `blocked`, and `infra`/`session-cost` were
never debt classes.

**What it changed.** The gate goes 176 entries to 175 and 4 open to 3; the
workflow-lane group goes 50 entries to 49 and the sequenced-past subsection 12 to
13; the timeline row's stated total follows. `PL-FCM3`'s measurement of 13
off-gate prerequisites collapses to one — the gate now waits on `PL-FG9D` alone.
