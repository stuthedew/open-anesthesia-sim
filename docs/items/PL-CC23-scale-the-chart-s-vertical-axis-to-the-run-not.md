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
