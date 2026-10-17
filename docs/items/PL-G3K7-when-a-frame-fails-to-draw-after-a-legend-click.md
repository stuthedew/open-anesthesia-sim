---
id: PL-G3K7
title: When a frame fails to draw after a legend click, the legend shows the selection the failed frame was assembled from while the chart keeps the last frame drawn, so the boxes name curves the plot is not drawing
priority: P2
effort: S
status: done
classes: defect, ux
feature: interface-areas
milestone: v0.5.25
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
closed: 2026-10-17
pr: 1492
payoff: The legend always names the curves the plot is drawing, even when the frame a click asked for fails to draw.
verify: grep -q 'def test_a_legend_click_whose_frame_fails_keeps_the_legend_on_the_frame_drawn' tests/integration/test_simulation_view.py
---

**Problem.** Found by `PL-VN6M`'s close-out review (`#1448`) and present on
`main` before it. A legend click is answered by
`SimulationView._handle_compartment_request`, which sets the new selection,
hands it to the legend and then calls `present(False)`. `present` turns an
exception into a visible halt rather than letting it out, so where the frame
for the new selection fails to assemble or draw, the legend shows the new
selection while the chart still shows the last frame drawn, from the old
one. The boxes then name curves the plot is not drawing - the disagreement
`PL-VN6M` exists to make impossible - though only in a failure state that is
itself announced. Before `PL-VN6M` the boxes moved on the click itself, with
the same result.

[superseded 2026-10-17: `PL-X7D5`'s design round made the legend a frame
widget instead, and the Done when below is rewritten to that.]
**Recommendation:** `present` reports whether it drew, and
`_handle_compartment_request` puts the previous selection back (and hands it
down again) when it did not, so the legend always names the frame on
screen. Test it by forcing `assemble_chart_frame` to raise on the request's
frame. It is presentation correctness under `CLAUDE.md`'s safety-critical
standard, which is why it was filed rather than fixed in `#1448`.

**Reproduced 2026-10-17** (triage): a started run presented once, then
`simulation_view.assemble_chart_frame` monkeypatched to raise and the fat
box unchecked through the legend. Afterwards the legend's `shown` drops fat,
`presented_frames` is unchanged (2 before, 2 after), the concentration chart
still draws the fat trace, and the run reads "Stopped - simulation error".
Script: `scratchpad/ui-a/test_repro_ui_a.py::test_g3k7`. Near-neighbour, not
a duplicate: `PL-0LG6` (`presentation-safety`) is the same legend-ahead-of-
the-plot disagreement reached through `add_run` leaving no frame owed.

**Why it matters.** The legend is how a reader learns which curve is which;
a box naming a curve the plot is not drawing, or omitting one it is, is a
mislabelled trace. **Not reachable by a learner today, which is what sets
the band:** a frame fails to assemble or draw only on a latent fault - a
snapshot refusing a value (`PL-7DJK`, which no supported setting reaches) or
runs on different agents - so `defect`/`ux` at `P2` rather than the
`safety`/`P1` the paragraph above invokes; the halt banner is also on
screen in the one state that reaches it.

**Done when.** The legend is a frame widget, the form `PL-X7D5`'s design
round chose over the Recommendation above (project owner, 2026-10-17,
ratified, "Agree with recs"): `SimulationView._refresh_view` tells the legend
the selection the frame was assembled from, once both plots have drawn, and
`_handle_compartment_request` only sets the selection and asks for a frame.
Where that frame fails, nothing writes the boxes, so the legend keeps naming
the frame on screen. A test,
`test_a_legend_click_whose_frame_fails_keeps_the_legend_on_the_frame_drawn`
in `tests/integration/test_simulation_view.py`, forces
`assemble_chart_frame` to raise on the click's frame and asserts the
legend's `shown` equals the selection the last drawn frame was assembled
from.

**Fixed 2026-10-17 under `PL-X7D5`'s second pull request**, in the rewritten
form above. `compartment_selection_changed` is emitted from `_refresh_view`
with the selection the frame was assembled from, after both plots draw, and
`_handle_compartment_request` no longer emits it. Where the clicked frame
fails, the legend's existing rule puts the clicked box back to the selection
last shown, which is the frame still on the plot. The regression test
`test_a_legend_click_whose_frame_fails_keeps_the_legend_on_the_frame_drawn`
asserts that the legend's `shown` equals the drawn frame's `visible`.
