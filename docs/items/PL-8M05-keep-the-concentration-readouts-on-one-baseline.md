---
id: PL-8M05
title: Keep the concentration readouts on one baseline at narrow window widths
status: untriaged
added: 2026-09-02
---

**Problem.** At a window narrower than about 1280 CSS pixels, four of the
seven metric labels wrap to a second line — "Simulated time", "Circuit /
inspired", "Alveolar / end-tidal-equivalent" and "Vessel-rich group" — while
"Mixed venous", "Muscle" and "Fat" stay on one. The readings below them
therefore sit on two different baselines. Measured by rendering the running
app at 1024, 1280 and 1440 CSS pixels while working PL-NV9W; at 1280 and above
the row is clean, at 1024 it is ragged. Three of the four wrapped before
PL-NV9W widened the alveolar panel, so this predates that change rather than
being caused by it.

**Why it matters.** `docs/MODEL.md` § "Displayed precision" states that the
six concentration readouts "sit in one row and are read comparatively", the
reason for showing them together being that a reader can see "the circuit lead
the alveoli lead the tissues", and that the numeric gap between two of them is
"the least certain thing on the display". A row whose readings do not share a
baseline is harder to read across in exactly the way that argument depends on,
and the panels that drop are not a fixed set: which ones wrap depends on the
window width, so the row's shape changes under the reader.

**Where.** `src/anesthesia_sim/app/simulation_view.py`,
`_build_concentration_metrics` and `_build_metric_panel`;
`docs/MODEL.md` § "Displayed precision" for the comparative-row requirement.

**Approach (one option, not a decision).** Reserving a uniform two-line label
block would align every reading at every width, at the cost of a taller row
where one line would do. A more interesting alternative is to split the label
into a compartment name and a subordinate clinical qualifier — "Alveolar" over
"end-tidal-equivalent", "Circuit" over "inspired" — which would fix the
alignment and arguably read better, since the name of what the model computes
would then be visually primary and the clinical gloss secondary. That is a
design change to the whole row rather than a layout fix, so it needs the
project owner's decision before it is built.

**Done when.** Every concentration reading in the row shares one baseline at
every supported window width, and the choice is recorded with the rendered
evidence for it.
