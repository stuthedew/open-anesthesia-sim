---
id: PL-G5SX
title: Headless tests that drive every layout operation and assert after each that the unconditional display set is still on screen, that the accounting tier is still reachable, and that a required value never left with the surface that drew it
priority: P1
effort: M
status: done
classes: safety, anticipated
feature: interface-areas
touches: tests/integration
blocked-by: PL-DWHG
added: 2026-09-16
closed: 2026-10-19
pr: 1661
payoff: every layout operation a learner can perform, saving and reloading included, is checked never to take a required clinical value off the screen
verify: grep -q 'def test_every_layout_operation_leaves_the_unconditional_set_on_screen' tests/integration/test_layout_safety.py
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

**Checked 2026-10-19:** `PL-904Y` and `PL-2KXB` have closed, so every operation but one can now be driven. Save and reload cannot, because nothing loads the reader's saved Workspaces or saves them yet. That is `PL-DWHG`, which this item now waits on.

**Built 2026-10-19 (#1661).** `tests/integration/test_layout_safety.py` opens a
dashboard as `main()` does, with its Workspaces loaded from a directory under
`tmp_path`, over a paused run with 30 minutes of history. It then resizes,
splits, swaps, joins and closes Areas, switches to each shipped Workspace,
saves, and opens a second dashboard on the saved file. After each step it
checks that every value of `unconditional_set(INHALED_AGENT)` but the halt
reason is among `visible_strings` with its widget shown, that every value on
screen before the step still is, that no value's widget sits inside the Area
container, and that every Area's chooser offers "Agent accounting". The
expected set comes from the declaration, not from the dashboard. The resize
step repeats `PL-9LNF`'s check that a widened chart is redrawn for its new
width on the next tick. To show the test can fail, `AreaLayout.perform` was
changed by hand to hide the delivered concentration after each operation.
The test then failed with "after a split, these are not on screen:
[<UnconditionalValue.DELIVERED_CONCENTRATION: 'delivered_concentration'>]".
The widening drag is shorter than the narrowing one because of `PL-4L8B`.
It still passes after `PL-L59K` gave each chart its own time window, merged
from `main` on 2026-10-19.
