---
id: PL-CC23
title: Scale the chart's vertical axis to the run, not to the vaporizer dial
priority: P2
effort: S
status: done
classes: ux, feature
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/formatting.py, tests/unit/test_simulation_view.py, tests/unit/test_formatting.py, docs/MODEL.md, README.md, ROADMAP.md
added: 2026-08-25
closed: 2026-09-04
pr: 319
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_the_axis_top_is_the_same_mac_multiple_for_every_agent' tests/unit/test_simulation_view.py
---

**Problem.** The chart's `max_y` is the agent's
`max_delivered_concentration_percent` - 8% for sevoflurane, 5% for isoflurane, 18%
for desflurane. A sevoflurane case run at 1 MAC therefore occupies the bottom
quarter of the plot, and a desflurane case the bottom third, with the axis top set
by a dial position nobody is using.

**Why it matters.** Two costs. The dynamics that the chart exists to show are
compressed into a corner of it, so differences between compartments read as
indistinguishable. And because the ceiling is agent-specific, the same case plotted
under two agents is drawn at two different scales - so a learner comparing
desflurane's wash-in to sevoflurane's is comparing shapes that have been silently
rescaled by a factor of two.

**Where.** `app/simulation_view.py` (`max_y` at the chart construction and in
`_refresh_view`).

**Approach.** Fit the axis to the run rather than to the device. In MAC mode
(PL-DHV7) the axis becomes agent-independent, which is what makes a cross-agent
comparison honest, and a fixed 0-2 MAC default with growth beyond it is likely
right. Whatever is chosen, the rule must be stable during a run: an axis that
rescales itself mid-case makes a rising curve look like it is flattening.

**Done when.** The plotted run fills the chart at a scale that does not depend on
which vaporizer the agent uses, the rule is stable within a run, and the axis is
labelled with the unit it is currently in.

**Appended 2026-09-04 (PL-F52R) - measured on a rendered frame, and a third
cost this item did not have.** PL-F52R put two clinical references on this
chart, and they are the first marks whose *height* is the whole point of them.
Rendered in Chromium at 1 MAC sevoflurane: the MAC-awake band spans 0.58-0.78 %
on an 8 % axis, which is **2.5 % of the plot height**. It draws as a slightly
thick line rather than as a band, so the +/-1 SD spread - the encoding that says
this is a population value and not a threshold - is technically present and
practically invisible.

That is a different cost from the two above. Those are about resolution: the
dynamics are cramped and two agents are drawn at two scales. This one is about
what a mark *asserts*. `docs/MODEL.md` s "MAC-awake as a chart reference"
requires the band to be distinguishable in kind from a line, and the geometry
is currently flattening a distinction the mark type was chosen to carry.
`CLAUDE.md`'s "make uncertainty and model limitations visible" is the standard
it sits under. The band's own label states the range in text, which is what
keeps this an interpretability defect rather than a safety one.

**One constraint to carry into the Approach.** A fixed 0-2 MAC default clips the
1 MAC line at the ceiling and leaves no room above it, and overpressure at
2-4 x MAC is a technique this simulator should be able to show. Whatever
multiple is chosen has to leave the 1 MAC line comfortably inside the plot
rather than on its edge.

**Appended 2026-09-04 (session working this item) - the three costs measured,
and they do not point the same way.** Computed from the agent files rather
than estimated. Today's axis top, expressed in MAC:

| Agent | Dial max | Axis top | 1 MAC at | MAC-awake band (+/-1 SD) |
| --- | --- | --- | --- | --- |
| Desflurane | 18 % | 3.00 MAC | 33.3 % height | 4.20 % of plot |
| Isoflurane | 5 % | 4.17 MAC | 24.0 % height | 2.40 % of plot |
| Sevoflurane | 8 % | 4.00 MAC | 25.0 % height | 2.50 % of plot |

**Two corrections to the Problem statement above.** The cross-agent rescale is
**1.39x**, not "a factor of two": the axis tops differ by 3.6x in *percent*
(18 % against 5 %), but a reader compares shapes, and in MAC the span is
3.00 against 4.17. The defect is real and its size is smaller than stated.
Second, the item's own `max_y` list is the whole story only for the axis top -
`horizontal_grid_lines` is *also* fixed in percent, at `interval=2`, which is
agent-dependent in the same way and worse: sevoflurane rules at whole MAC
(2 % = 0.5 MAC, so lines every 0.5 MAC), isoflurane at 1.67 MAC intervals and
desflurane at 0.33 MAC, nine of them. Whatever the axis becomes, the gridline
interval has to be denominated in the same unit; it rides this item.

**Why the three costs conflict.** A fixed axis of K MAC for every agent:

| K | 1 MAC at | Band, % of plot | Clips (dial exceeds K) | Dead space |
| --- | --- | --- | --- | --- |
| 2.0 | 50.0 % | 5.00-6.30 % | all three | none |
| 2.5 | 40.0 % | 4.00-5.04 % | all three | none |
| 3.0 | 33.3 % | 3.33-4.20 % | iso, sevo | none |
| 4.0 | 25.0 % | 2.50-3.15 % | iso | desflurane 25 % |
| 4.5 | 22.2 % | 2.22-2.80 % | none | des 33 %, sevo 11 %, iso 7 % |

Cost 2 (honest cross-agent comparison) is closed by *any* shared K. Costs 1
(dynamics cramped) and 3 (the band draws as a line) need K **low**. The
constraint this item appends - 1 MAC comfortably inside, overpressure at
2-4x MAC showable - needs K **high**. They cannot all be satisfied.

The sharpest form of it: at K = 4.0 sevoflurane's band is **2.50 % of the
plot, exactly what it is today**, because sevoflurane's axis is already 4 MAC.
So the change this item describes does nothing at all for the defect PL-F52R
appended to it, unless the ceiling comes down to roughly 2.5 MAC - and there
the circuit trace leaves the plot during the overpressure this item's own
constraint says must stay on it.

**On "a fixed 0-2 MAC default with growth beyond it".** The two halves of that
sentence contradict each other, and the item says so itself one line later:
growth beyond the default *is* a mid-run rescale, which "the rule must be
stable during a run" forbids. `docs/MODEL.md`'s "Why the axis is fixed rather
than fitted" already settled the same question for the wash-in chart - an axis
that grew "would redraw the wash-in curve at a smaller height partway through
a lesson - a shape change a reader would attribute to the model rather than to
the axis". That reasoning transfers unchanged. Fixed holds; growth does not.

**Resolved 2026-09-04.** Fixed at 0 to 3 x MAC for every agent, ruled every
half MAC, with `horizontal_grid_lines` denominated in MAC alongside the
ceiling. Three is exactly desflurane's dial maximum in MAC, so the shared
ceiling is anchored to a device limit and the most-limited agent gets no dead
band; 1 MAC sits at a third of the plot height and the 2-3x MAC overpressure
range stays on the plot.

**"Growth beyond it" was not built** (project owner, 2026-09-04). It
contradicts this item's own requirement that the rule be stable within a run,
and `docs/MODEL.md`'s "Why the axis is fixed rather than fitted" had already
settled the same question for the wash-in plot. The axis is fixed across the
session rather than only within a run, so two consecutive runs are comparable
too.

**The band cost went to `PL-90Y6`** (the MAC-awake band draws as a line at any
axis range the overpressure constraint allows), because the measurement showed
no axis choice fixes it: the ceiling that would make a +/-0.05 MAC band
unambiguous is around 2 MAC, and there the 1 MAC line sits at mid-plot with no
room for overpressure.

**One failure mode this change introduced, and its guard.** A dial-maximum
ceiling could not be exceeded; a fixed one can, and sevoflurane at 8 % is
4.00 MAC and is a common inhalational-induction setting. A clipped trace
draws as a horizontal line, which is what a plateau looks like, so the chart
names the compartments above the ceiling and says the readouts are unclipped.
The comparison is against the displayed resolution rather than against zero,
because isoflurane's ceiling is 3 x 1.2 = 3.5999999999999996 and a naive
comparison reports floating-point noise on a run that merely reaches 3 MAC.

Also filed: `PL-DXQC` (the v0.4.0 Goal section states two problems in the
present tense that are now fixed), found sweeping the docs.
