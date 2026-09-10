---
id: PL-25KS
title: Port the dashboard to PySide6: the readout row, the four parameter controls, the agent selector, the transport, the new-case dialog and the notice banner
status: untriaged
feature: qt-port
added: 2026-09-10
---

**Problem.** Port the dashboard to PySide6: the readout row, the four parameter controls, the agent selector, the transport, the new-case dialog and the notice banner

**`v0.5.1`'s Required scope, item 2** - the bulk of it.
`app/simulation_view.py` is 3 619 lines and this is most of what replaces it.

**The hedges are requirements, not labels.** "end-tidal-equivalent" and
"inspired" are `PL-NV9W` and `PL-8M05`; "common gas outlet" is `PL-71CF`.
Each has a test holding the exact pair of strings, and each exists because the
unhedged form is a wrong clinical inference from a correct number. The spike
carries all three and `spikes/qt/chart_sources.py` records why.

**One thing the spike does better than the shipped build, worth keeping.** Qt
sliders are integer-valued, and the spike turns that into a property: the steps
are the display resolution, so the value applied to the model is exactly the
value printed beside it. The Flet slider is continuous and rounds only its drag
label, which is what `PL-3TLK`'s comment had to reason about.
