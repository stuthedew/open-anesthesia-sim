---
id: PL-ZRSP
title: Plot the F_A/F_I ratio the uptake literature plots
priority: P1
effort: S
status: done
classes: science, ux
feature: teachable-case
milestone: v0.3.8
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/wash_in.py, src/anesthesia_sim/app/formatting.py, docs/MODEL.md
added: 2026-08-25
closed: 2026-09-04
pr: 306
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_the_trace_stops_where_alveolar_exceeds_inspired' tests/unit/test_wash_in.py
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

**Blocked on `PL-DR1Z` (2026-09-03).** Sequencing only, and it is this item's own
**Safety notes.** promoted from prose into the front matter: F_A/F_I is the
textbook wash-in curve only while inspired concentration is held constant, and
the control-input timeline is what makes a mid-run dial change visible. Until
that lands, a learner reading a rise as uptake when it is a dial change has
nothing on screen to correct them, which is the specific misreading this item
exists to avoid creating.

Nothing here is wrong today, and the band stands on this item's own classes
rather than on the blocker's. `PL-9K7K` records why the state changed: `docket
next` ranked this first among the v0.4.0 items on `P1`/`S` alone, which the
ranking cannot reconcile with a sentence in a brief - so every session asking
what to do next was pointed at the one item its own brief defers.

**Block cleared 2026-09-03.** `PL-WB0X` merged as `#263`, so the formatters
and the chart-series assembly are already in `app/formatting.py` and
`app/chart_series.py`. The paragraph above is kept as the record of why this
waited; it no longer holds. Recovered from `origin/claude/what-next-rsmqeu`,
which was abandoned without a pull request.

**Unblocked 2026-09-04.** `PL-DR1Z` (record the control-input timeline and mark
it on the chart) landed in v0.3.7, so the caveat this item's trace carries -
that the curve means what the textbook curve means only while inspired
concentration is held constant - is now something a reader can *check* rather
than only be told: a mid-run change to the delivered dial is marked on the same
chart, at the simulated time it took effect. That was the dependency, and it is
why this item's band followed it.

**`PL-WB0X` had cleared earlier**, as `#263`, so the formatters and the
chart-series assembly were already in `app/formatting.py` and
`app/chart_series.py` when this was worked. Neither blocked paragraph above
holds any longer; both are kept as the record of why this waited.

**`controller.py` drops off `touches:`, and two modules join it.** The ratio is
a displayed quantity rather than recorded state, so nothing is added to
`SimulationHistorySample` - which `PL-W3DD` is about to reshape, and which
would then be carrying a derived value with a defined domain. It is computed at
the display instead, in a Flet-free `app/wash_in.py` that `docs/MODEL.md`'s new
section terminates in, the way `app/formatting.py` terminates § "Displayed
precision".

**Worked 2026-09-04.** The trace is a second plot under the compartment chart,
on the same time window, on a dimensionless axis fixed 0 to 1. Four decisions
the brief did not settle:

- **The denominator has a floor.** $`F_I`$ is exactly zero before any agent
  reaches the circuit, so the quotient is $`0/0`$ at the start of every run and
  for the whole of a run whose vaporizer is never opened. The floor is the
  smallest inspired concentration the interface itself reports as non-zero,
  derived from `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` rather than chosen
  beside it.
- **The plotted range stops at 1, and that is a physiological boundary rather
  than an axis convenience.** $`F_A \le F_I`$ is exactly the uptake regime.
  Above it the tissues are returning agent faster than it is delivered, which
  is elimination and not wash-in. Measured on sevoflurane, closing the
  vaporizer at 10 L/min after a 30-minute wash-in takes the ratio to 3.47 at
  the reference adult's 4.0 L/min of alveolar ventilation and to 20.11 at
  0.5 L/min - it settles near $`1 + \dot V_{\mathrm{FGF}} / \dot V_A`$, which
  the supported input ranges do not bound. So no fitted axis would have helped
  either.
- **The trace breaks rather than bridging.** A vaporizer closed and later
  reopened leaves a stretch outside the domain; one polyline through the drawn
  samples would draw a straight segment across values the run never produced.
  It is a fixed pool of segment series, parked when unused, on the pattern
  `PL-DR1Z` established for the control marks.
- **One reading, not two functions.** `read_wash_in` returns the plottable
  value and the domain together, so the trace and the sentence beside it are
  produced from one evaluation and cannot disagree about the same instant.

The control marks get a second pool on this plot, drawn in the same pass over
the same adjustments: this trace's whole caveat is that it is the textbook
curve only while inspired concentration is held constant, and a mark on the
chart above leaves the plot that is actually being misread unannotated.

`tests/reference/test_published_wash_in_and_elimination.py` now asserts that the number the
chart draws is the number the Yasuda comparison was made on, so the validated
quantity and the displayed quantity cannot drift apart.

**Two things found in passing.** The replayed run in
`tests/integration/test_chart_patching.py` had its alveolar trace *leading* its
circuit trace - a lung filling a circuit - which no test noticed until a wash-in
ratio was computed from the pair; its decay constant moves from 0.998 to
0.9993, and the docstring says why the ordering matters. And the wash-in axis
first shipped with gridlines at 0.25 and labels at whatever interval the chart
chose, which is two scales on one axis; it now carries explicit labels and a
`label_spacing` equal to the gridline interval. `PL-Q4VH` records that the
compartment chart above still has the milder form of the same problem.

**Verified against the running app.** Chromium over Playwright against the
`flet_web` server, with the CanvasKit assets rerouted to `flet_web`'s local
copies because this container cannot reach `gstatic.com`. A 33 s sevoflurane
wash-in drew `F_A/F_I = 0.30`, against 0.2804 at 30 s and 0.4143 at 60 s
computed directly from the core. Closing the vaporizer and raising the flow to
10 L/min then took the trace up to 1.00, where it stopped, with the line beside
the plot reading "alveolar exceeds inspired - the patient is returning agent,
which is elimination and not wash-in" and both dial changes marked on both
plots.

**Appended 2026-09-04, on review of the rendered plot** (project owner: "Stop
at or just above 1, but so it looks natural and not cut off"). The stop stays;
what changed is that it now reads as an ending rather than as a clipped edge.
Three things together, none of which moves the boundary:

- **The trace is drawn one sample past the boundary.** The last sample at or
  below equilibrium is up to one simulation step below the line it stopped at,
  so the curve halted in clear space with nothing to show why. It now includes
  the crossing sample at each end of a stretch, so it meets the equilibrium
  reference and terminates on it. Bounded by a stated
  `WASH_IN_TERMINUS_CEILING` rather than by a property of the model: a 0.1 s
  step crosses by a hair - 1.00235 at worst across every agent and every
  supported ventilation and cardiac output at maximum flow - but
  `BreathingCircuit.set_circuit_volume` conserves agent while changing the
  volume it is divided by, so the ratio is not continuous in general, and a
  crossing sample above the ceiling is not drawn at all rather than clamped
  onto it.
- **Equilibrium is drawn as a labelled reference line.** A trace that halts in
  open space reads as cut; one that halts on a labelled line reads as having
  arrived. It is a definitional anchor rather than a measured value with
  spread, so it is a line and not a band, in MUTED and the same wide dash as
  the 1 MAC line on the chart above.
- **The axis stands at 1.15 with the ruling and the labels stopping at 1.00.**
  With the axis topping out at equilibrium the ending landed on the frame,
  where a line that stopped and a line the plot cut off look identical. The
  top of the frame is left unlabelled so the readable scale is still 0 to 1.

A terminal dot marks the last point of a stretch that stopped by crossing,
and only such a stretch: the live right-hand end of a growing run is not an
ending, and a dot there would move every frame while saying nothing.
