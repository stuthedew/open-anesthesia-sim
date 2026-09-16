---
id: PL-G5SX
title: Headless tests that drive every layout operation and assert after each that the unconditional display set is still on screen, that the accounting tier is still reachable, and that a required value never left with the surface that drew it
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: M
blocked-by: PL-904Y, PL-2KXB
classes: safety, anticipated
touches: tests/integration
---

**Problem.** Headless tests that drive every layout operation and assert after each that the unconditional display set is still on screen, that the accounting tier is still reachable, and that a required value never left with the surface that drew it

**Why it matters.** Every safety guarantee this milestone makes is a claim about
what survives an operation, and none of them is checkable today because nothing
can perform one. `docs/MODEL.md` divides the display into an unconditional set
no Workspace may remove, an accounting tier that must stay reachable, and
conditional obligations that bind a surface only when shown - and the whole
division is prose until a test drives a layout through its operations and
asserts it.

**Done when.** A headless test drives split, join, swap, resize, close,
Workspace switch, save and reload, and after each asserts through `PL-904Y`'s
predicate that every unconditional value is on screen, that the accounting tier
is reachable, and that no required value left the display with the surface that
drew it. It includes the assertion `PL-9LNF` says cannot be written today:
resize one Area while paused, and the redrawn series is sampled for that Area's
new width.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 18.
