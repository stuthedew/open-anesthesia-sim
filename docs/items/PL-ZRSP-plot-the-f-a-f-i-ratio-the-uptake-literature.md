---
id: PL-ZRSP
title: Plot the F_A/F_I ratio the uptake literature plots
priority: P1
effort: S
status: blocked
classes: science, ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/controller.py, docs/MODEL.md
added: 2026-08-25
blocked-by: PL-WB0X
---
**Problem.** The wash-in curve every textbook and every uptake lecture shows is
F_A/F_I against time - the ratio that makes agents comparable and that the
solubility argument is usually taught from. The application plots six absolute
concentrations and never that ratio, so a learner cannot line up what they are
watching with the figure they were taught from.

**Why it matters.** It is the cheapest single thing that connects this simulator to
the literature: both quantities are already modeled, and the arithmetic is a
division. The reference simulator this project's parameters come from displays
compartment tension ratios for the same reason.

**Safety notes.** The ratio means what the textbook curve means only while inspired
concentration is held constant. Move the dial mid-run and F_A/F_I is still a
well-defined ratio of two modeled states but is no longer the wash-in curve, and a
learner who does not notice will read a rise as uptake when it is a dial change.
The control-input timeline (PL-DR1Z) is what makes that visible, so land this after
it. Note also that F_I here is the modeled circuit concentration, which itself
approaches the dial over the circuit time constant - that is correct and is part of
the lesson, but the label must say the ratio is against inspired, not against the
vaporizer setting.

**Done when.** F_A/F_I is available as a plotted quantity, its axis and label make
clear it is a dimensionless ratio against inspired rather than against the dial,
`docs/MODEL.md` states the constant-F_I caveat, and the trace is readable against
the published wash-in curves for the three agents.

**Blocked on `PL-WB0X` (2026-09-02, project owner).** Not a stated
prerequisite in this brief - it is file contention that `bin/docket concurrent
PL-WB0X` reports and nothing else would have surfaced. `PL-WB0X` moves the
formatters and the chart-series assembly out of `simulation_view.py` into
`app/formatting.py`, and this item edits both in their current location. Doing
it first means doing that part of it twice, and the second time inside a file
that has since moved.

The block is sequencing only: nothing here is wrong today, and the band stands
on this item's own classes rather than on the blocker's.
