---
id: PL-3YND
title: AreaLayout._fits lays out the whole tree with apportion twice per Area on every bisection step of a stopped border drag, about 9 ms a pointer move at 6 Areas and 56 ms at 20 (blind review of PL-501T); the start layout depends only on the drag's start and could be laid out once per drag
priority: P3
effort: S
status: ready
classes: perf
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py
deferred-from: v0.7.0 - a new problem: the repeated start layout came in with #2169 (718862f7, 2026-11-16, PL-501T), which cleared a frozen entry after the freeze
added: 2026-11-16
payoff: A border drag in a Workspace of many Areas keeps up with the pointer, because each move lays out the tree about half as often.
---

**Problem.** AreaLayout._fits lays out the whole tree with apportion twice per Area on every bisection step of a stopped border drag, about 9 ms a pointer move at 6 Areas and 56 ms at 20 (blind review of PL-501T); the start layout depends only on the drag's start and could be laid out once per drag

**Checked 2026-11-22**, at `d4e8200c`. The cost is still there. In `AreaLayout._fits` in `app/area_layout.py`, the loop over `moved.areas()` calls `drawn(start, area.id)` for every Area, and `drawn` runs `apportion` over the whole tree each time. The start layout depends only on where the drag began, yet it is laid out again on every bisection step of every pointer move. The check came in with #2169 (718862f7, 2026-11-16, `PL-501T`).

**Why it matters.** A stopped border drag runs this check on each pointer move. The blind review of `PL-501T` measured about 9 ms a move at 6 Areas and 56 ms at 20. At 20 Areas that is enough to make the drag lag visibly behind the pointer. About half of it is the start layout repeated. No value a learner reads changes.

**Done when.** The start layout of a border drag is laid out once for the drag rather than once per Area on each bisection step, and a test shows that a drag stops at the same place as before.

**Generator check.** A one-off. The work it repeats is a value that depends only on the drag's start, recomputed inside a loop. No head's `misread:` line states that fact, and no other open item repeats it.
