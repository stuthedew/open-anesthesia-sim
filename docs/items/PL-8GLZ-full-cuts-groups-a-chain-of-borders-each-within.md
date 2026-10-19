---
id: PL-8GLZ
title: _full_cuts groups a chain of borders each within BORDER_ALIGNMENT_TOLERANCE of the next, but tests whether a piece straddles the line against the chain's first member alone, so a chain wider than the tolerance could reject a valid cut; no case has been built
priority: P3
effort: S
status: ready
classes: defect
feature: layout-sliver-areas
touches: src/anesthesia_sim/layout/model.py, tests/unit/test_layout_model.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 triage pass
added: 2026-10-18
payoff: A join across nearly aligned borders is either shown to work or fixed, so a reader is never refused a layout the model could hold
verify: grep -q 'def test_a_chain_of_borders_wider_than_the_tolerance' tests/unit/test_layout_model.py
---

**Problem.** _full_cuts groups a chain of borders each within BORDER_ALIGNMENT_TOLERANCE of the next, but tests whether a piece straddles the line against the chain's first member alone, so a chain wider than the tolerance could reject a valid cut; no case has been built

**Why it matters.** `_full_cuts` in `layout/model.py` decides whether a join can
be carried out. If a chain of nearly aligned borders spans more than
`BORDER_ALIGNMENT_TOLERANCE`, a piece could be tested against the wrong line
and a valid join refused. Unlike `PL-25D9`, the borders here sit in different
splits, so no Area narrower than the tolerance is needed and `PL-391Y`'s fix
does not remove the case.

**Done when.** A test in `tests/unit/test_layout_model.py` builds a chain of
three or more borders, each within the tolerance of the next but spanning more
than it. Either the test shows a valid join refused, and `_full_cuts` is fixed
so it passes; or the test shows the join taken, and the item closes with the
test as the evidence that the case is safe.
