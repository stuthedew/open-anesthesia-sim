---
id: PL-ZRSP
title: Plot the F_A/F_I ratio the uptake literature plots
priority: P1
effort: S
status: ready
classes: science, ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/controller.py, docs/MODEL.md
added: 2026-08-25
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

**What the denominator is, and what has to be said about it (added 2026-09-03).**
$`F_I`$ here is the modelled breathing-circuit fraction, and the identity
$`F_C \equiv F_I`$ holds only *because of* this model's circuit assumptions - one
ideal, perfectly mixed circuit, no dead space, and no separate inspiratory and
expiratory limbs. It would stop holding under a multi-limb circuit such as Lerou
and Booij's three-part breathing system. Since this trace is the field's canonical
teaching graph, and v0.4.0's Definition of Done already requires that it "carry, at
the point of display, what it does and does not assert", that assumption is part of
what it must carry - not a footnote deferred to the naming pass.

So this item records the assumption in `docs/MODEL.md` § "Model boundary" or
§ "Assumptions" and surfaces it at the point of display, whether or not `PL-3TLK`
(rename the middle gas-phase state $`F_C`$ to the domain's $`F_I`$) has landed.
`PL-3TLK` carries the source: Hendrickx JFA, De Wolf A. Special aspects of
pharmacokinetics of inhalation anesthesia. In: Schuttler J, Schwilden H (eds).
Modern Anesthetics. Handbook of Experimental Pharmacology 182. Springer,
2008:159-186 - the $`F_D \rightarrow F_I \rightarrow F_A`$ cascade on pp. 161-162
and the curve's didactic role on p. 167.

**What v0.4.1 does to this.** `PL-3TLK` renames the denominator's accessor from
`BreathingCircuit.circuit_concentration_fraction` to
`inspired_partial_pressure_fraction`, so any label, docstring or axis title
written here that calls it "circuit" is reworded one release later. Prefer the
domain's name now; the code will catch up.