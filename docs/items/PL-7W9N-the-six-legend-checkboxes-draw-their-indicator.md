---
id: PL-7W9N
title: The six legend checkboxes draw their indicator from the host palette, so under a dark appearance the tick is INK on near-black at 1.3:1 and an unchecked box reads as a filled one
priority: P2
effort: S
status: ready
classes: defect, ux
feature: platform-palette
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_dark_appearance.py
added: 2026-09-20
payoff: the box that says whether a compartment is on the chart stops reading the same checked and unchecked under a dark host
verify: grep -q 'def test_a_legend_checkbox_draws_its_indicator_in_the_theme' tests/integration/test_dark_appearance.py
---

**Problem.** The six legend checkboxes draw their indicator from the host palette, so under a dark appearance the tick is INK on near-black at 1.3:1 and an unchecked box reads as a filled one

**Why it matters.** The box is what says whether a compartment is drawn on the
chart. `TraceLegend` declares the *label* - `color: INK` while the trace is
drawn, `MUTED` while it is hidden - and declares nothing for the indicator, so
the indicator's interior comes from palette `Base`. Measured on 2026-09-20 by
walking the rendered widget tree under a dark host palette: all six boxes
resolve `Base #1e1e1e` against a tick drawn in `Text`, which the label's
stylesheet has set to `INK #243B53`. That is 1.35:1, so the tick is very nearly
invisible, and an unchecked box is a solid dark square on a light panel - the
shape a filled or selected box has in most interfaces, which is the opposite of
what it means here.

**It is a legibility defect rather than a wrong reading, because a second
channel survives.** A hidden compartment also loses its line-style swatch and
its label goes `MUTED`, and `.claude/rules/ui-color.md` judgment 2 is what put
those there. So a reader has two other cues for which traces are drawn, and
this does not reach the safety-critical standard's wrong-value bar. It is still
the control's own state rendered unreadable.

**Done when.** Each of the six boxes declares the interface's palette, so the
indicator's interior is `PANEL` and its tick `INK` under either host
appearance, and a test holds it under a dark host palette.
