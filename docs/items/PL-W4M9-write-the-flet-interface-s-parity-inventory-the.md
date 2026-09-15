---
id: PL-W4M9
title: Write the Flet interface's parity inventory the Qt port's definition of done measures against: the 200 tests in tests/unit/test_simulation_view.py are the only record of it and the port rewrites them, though the v0.4.25 tag keeps them reachable
priority: P3
effort: M
status: ready
classes: docs, planning
feature: qt-port
touches: docs/ARCHITECTURE.md
added: 2026-09-14
verify: grep -q 'parity inventory' docs/ARCHITECTURE.md
---

**Problem.** Write the Flet interface's parity inventory the Qt port's definition of done measures against: the 200 tests in tests/unit/test_simulation_view.py are the only record of it and the port rewrites them, though the v0.4.25 tag keeps them reachable

**Overtaken in part, 2026-09-15.** The port landed in #588, so the inventory can
no longer be written *before* the rewrite it was meant to guard - the 200 tests
in `tests/unit/test_simulation_view.py` have already been replaced. The `v0.4.25`
tag still holds them, so the record is recoverable rather than lost, and that is
what keeps this worth doing rather than dropping.

**Why it matters.** The port's definition of done is parity with an interface
that now exists only in a tag, which means "is the port finished?" is currently
answered from memory. That is the question a milestone closes on, and the two
ways of getting it wrong are both expensive: calling the port done while a
behaviour is missing ships a regression nobody is looking for, and calling it
unfinished forever is how a milestone stops closing. An inventory written from
the tagged tests turns it back into something a reader can check.

It is also the last moment the inventory is cheap. Every session after this one
reads the Qt interface as the interface, so recovering what the Flet one did
gets harder as the tag recedes rather than easier.

**Done when.** `docs/ARCHITECTURE.md` carries the parity inventory - each
behaviour the Flet interface had, recovered from `v0.4.25`'s
`tests/unit/test_simulation_view.py`, marked as ported, deliberately dropped
with a reason, or outstanding - and the port's remaining items can be read off
the outstanding rows.
