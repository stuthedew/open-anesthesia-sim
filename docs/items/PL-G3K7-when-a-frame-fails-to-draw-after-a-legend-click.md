---
id: PL-G3K7
title: When a frame fails to draw after a legend click, the legend shows the selection the failed frame was assembled from while the chart keeps the last frame drawn, so the boxes name curves the plot is not drawing
status: untriaged
feature: interface-areas
added: 2026-10-12
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

**Recommendation:** `present` reports whether it drew, and
`_handle_compartment_request` puts the previous selection back (and hands it
down again) when it did not, so the legend always names the frame on
screen. Test it by forcing `assemble_chart_frame` to raise on the request's
frame. It is presentation correctness under `CLAUDE.md`'s safety-critical
standard, which is why it was filed rather than fixed in `#1448`.
