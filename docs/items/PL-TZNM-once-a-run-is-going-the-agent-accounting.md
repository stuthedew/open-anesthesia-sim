---
id: PL-TZNM
title: Once a run is going, the agent accounting validation panel is laid out at its 188 px minimum, below its 202 px size hint, so the five-line litres readout gets 56 of the 70 px it needs and its Absolute error line is cut off
priority: P2
effort: S
status: ready
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_qt_rendering.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: the accounting panel shows every line of its readout while a run is going, so the error figure the Valid verdict rests on can be read
verify: grep -q 'def test_no_readout_value_is_clipped_once_a_run_is_going' tests/integration/test_qt_rendering.py
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

**Why it matters.** The panel's Absolute error line is the figure the Valid verdict is checked against, and once a run is going it is cut off and the Delivered line is overprinted by the caption above it - a value hidden or overdrawn, which `CLAUDE.md` counts as a presentation failure. The squeeze is the layout giving the panel less than its own size hint, which does not depend on the font.

**Done when.** Once a run is going the panel gets at least its size hint, and a rendering test over a run in progress, built as `main()` builds the page, finds no line of the litres readout clipped.
