---
id: PL-TZNM
title: Once a run is going, the agent accounting validation panel is laid out at its 188 px minimum, below its 202 px size hint, so the five-line litres readout gets 56 of the 70 px it needs and its Absolute error line is cut off
status: untriaged
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_qt_rendering.py
added: 2026-10-01
---

**Problem.** Once a run is going, the agent accounting validation panel is laid out at its 188 px minimum, below its 202 px size hint, so the five-line litres readout gets 56 of the 70 px it needs and its Absolute error line is cut off

**Measured 2026-10-01** (found during `PL-CQRL`), offscreen, the dashboard
built as `main.py` builds it - `.claude/skills/run-the-app/SKILL.md`'s command -
with each visible label's height compared against `heightForWidth` for a
wrapped label and `sizeHint().height()` otherwise:

| Window | Simulated | Panel height | Litres readout |
| --- | --- | --- | --- |
| 1600x1000 | 0 s | 202 (its size hint) | 70 of 70 px |
| 1600x1000 | 120 s | 188 (its minimum) | 56 of 70 px, clipped |
| 1920x1080 | 120 s | 188 | 56 of 70 px, clipped |
| 2400x1400 | 120 s | 188 | 56 of 70 px, clipped |

The width does not move it, so the squeeze comes from the sidebar's vertical
layout once the run starts, not from wrapping. In the grab the text is centred
in its 56 px box, so `Delivered` is overdrawn by the italic caption above it and
`Absolute error` is cut at the panel's lower edge: the figure a reader would
check the panel's `Valid` verdict against, though the verdict itself comes from
`agent_accounting_passes_validation` and was not traced further here.

**Not established.** The figures are on the container's fallback font, so the
exact pixel counts will differ on the project owner's machine; whether it
clips there is unmeasured. What does not depend on the font is that the layout
gives the panel less than its own size hint asks for.
