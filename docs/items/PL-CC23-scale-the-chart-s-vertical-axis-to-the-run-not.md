---
id: PL-CC23
title: Scale the chart's vertical axis to the run, not to the vaporizer dial
priority: P2
effort: S
status: ready
classes: ux, feature
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py
added: 2026-08-25
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
