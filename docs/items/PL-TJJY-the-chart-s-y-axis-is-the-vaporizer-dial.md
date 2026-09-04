---
id: PL-TJJY
title: The chart's y-axis is the vaporizer dial maximum, so the clinical range and the MAC-awake band are compressed into the bottom eighth of the plot
priority: P2
effort: M
status: dropped
classes: ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md
added: 2026-09-04
closed: 2026-09-04
reason: Duplicate of PL-CC23, which states the same defect and the same cause and was already ready. Captured before checking the feature's own list, which is the miss PL-TH7P exists to close. The measurement this item added - the MAC-awake band spanning 2.5 percent of the plot height at 1 MAC sevoflurane - has been folded into PL-CC23 rather than lost with the file.
---

**Problem.** `SimulationView` sets `max_y` to
`snapshot.max_delivered_concentration_percent`, the agent's real vaporizer dial
maximum: 8 % sevoflurane, 5 % isoflurane, 18 % desflurane. Nothing clinical
happens up there. A 1 MAC sevoflurane case tops out at 2 %, so the whole run
occupies the bottom quarter of a 360 px chart, and the desflurane case occupies
the bottom third of an 18 % axis.

**Why it matters, and why now.** PL-F52R's MAC-awake band is the first mark
whose *height* is the whole point of it. Measured in the browser on 2026-09-04
at 1 MAC sevoflurane: the band spans 0.58-0.78 % on an 8 % axis, which is
2.5 % of the plot height. It renders as a slightly thick line rather than as a
band, so the +/-1 SD spread - the thing that says this is a population value and
not a threshold - is technically visible and practically not. The mark type is
carrying a distinction the geometry then flattens.

The same compression costs the six traces their vertical resolution, so this is
not only a MAC-awake problem; it is just that MAC-awake is where it first
becomes a correctness-of-reading question rather than a legibility one.

**What is not obvious, and is the reason this is a decision rather than a
fix.** Three candidate rules, each with a real cost:

- **Track the run.** An axis that rescales as the trace climbs makes two
  moments of the same run incomparable and animates the grid during playback.
- **A fixed multiple of the agent's MAC** (say 0-3 x MAC). Comparable across
  agents by construction, which is what the MAC axis exists for, but it clips a
  deliberate overpressure at 4-8 x MAC - which is a technique the simulator
  should be able to teach.
- **Keep the dial maximum and let the reader zoom.** No zoom control exists;
  adding one adds a mode, and `docs/MODEL.md` argues against modes on this
  chart.

A fourth is worth pricing: keep the dial maximum as the default and add a
second, clinically-scaled view rather than replacing the axis.

**Where.** `src/anesthesia_sim/app/simulation_view.py`, `_refresh_view` sets
`self._concentration_chart.max_y`; the initial value is set in `__init__`.
`docs/MODEL.md` s "MAC-awake as a chart reference" and s "MAC multiples as a
display unit" are what a change here has to stay true to.

**Done when.** A 1 MAC case fills a useful fraction of the plot's height, the
MAC-awake band reads as a band rather than as a thick line, and whatever rule
sets the ceiling is stated in `docs/MODEL.md` beside the two references it
governs - so a reader knows whether the top of the chart means anything.

**Found.** PL-F52R, 2026-09-04, on a rendered frame rather than from the code.

**Decision needed.** Which rule sets the chart's y-axis maximum. The four
candidates and their costs are under **What is not obvious** above.

*Recommendation:* the fourth - keep the dial maximum as the default and add a
clinically-scaled alternative - is the only one that gives up nothing. But it
is also the largest, and if the answer has to be one axis, it is a fixed
multiple of the agent's MAC: it is the rule that makes two agents comparable,
which is the same argument the MAC axis itself rests on, and overpressure above
the ceiling is a case the simulator can teach by other means. A run-tracking
axis should be ruled out either way - it makes two moments of one run
incomparable, which is the opposite of what this chart is for.
