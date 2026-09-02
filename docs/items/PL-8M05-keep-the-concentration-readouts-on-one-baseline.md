---
id: PL-8M05
title: Keep the concentration readouts on one baseline at narrow window widths
priority: P1
effort: S
status: done
classes: safety, ux
feature: presentation-safety
milestone: v0.2.10
touches: src/anesthesia_sim/app/simulation_view.py, tests/unit/test_simulation_view.py, tools/contrast_check.py
added: 2026-09-02
closed: 2026-09-02
pr: 196
verify: uv run pytest tests/unit/test_simulation_view.py -k qualifier_line
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

**Done when.** Every concentration reading in the row shares one baseline at
every supported window width, and the choice is recorded with the rendered
evidence for it.

**Worked.** Two changes, and the first is why the second was possible.

Each panel now names a compartment on one line and glosses it on a smaller
italic line beneath — "Alveolar" over *end-tidal-equivalent*, "Circuit" over
*inspired* — instead of joining the two with a slash. That is a safety
decision before it is a typographic one: what the model computes is a
compartment, what a clinician would set beside it on a monitor is a different
and measured thing, and a slash offered them as alternative names for one
quantity. Two lines at two sizes say which claim is which. It also removes
the longest labels, so no name is long enough to wrap.

A panel with no gloss still draws the gloss line, using a non-breaking space
so the spacer is tied to the qualifier's font size rather than to a pixel
constant somebody would have to re-measure. Every label block is therefore
the same height and every reading sits on one baseline.

The row also reflows rather than compressing: seven panels across at 1200 CSS
pixels and wider, four at 992, two at 768, one below that, each panel spanning
one column of a grid whose column *count* is what changes. Rendered at 1024,
1200 and 1440: every name on one line and every reading on one baseline at all
three. 1200 is the tightest seven-across case and it holds there in a serif
fallback wider than the Roboto the app actually ships, so the shipped font has
margin rather than being on the edge.

`test_every_readout_reserves_a_qualifier_line_and_an_equal_column` holds both
invariants — every panel draws its gloss line at a smaller size than its name
and takes an equal column, and the widest step of the ladder still seats every
readout side by side, so an eighth panel cannot silently split the row.

**Note on the contrast table.** The gloss adds no pair to
`tools/contrast_check.py`: same `MUTED` on the same `PANEL`, and at 12px it is
normal text by WCAG's definition, so it is judged at the 4.5:1 the name above
it already meets. The `INK`/`PANEL` and `MUTED`/`PANEL` entries' line
citations were 90-odd lines stale and are refreshed; `PL-J7C5` proposes
replacing them with symbol names, which do not drift.
