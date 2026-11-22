---
id: PL-92XM
title: At a 1280 px window the control-change record narrows when the version label is long: the transport row's minimum width includes the version badge, so a dev checkout's 'Version 0.6.18+g0e0aa1cd.dirty' holds the left column at 1028 px, the record's text at 180 px, and 'Alveolar ventilation 12.0 L/min ->' (184 px) no longer fits on one line
priority: P3
effort: S
status: ready
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/simulation_view.py, tests/integration/simulation_view
added: 2026-11-14
payoff: the control-change record keeps whole lines at a 1280 px window whatever version or agent the badge names
---

**Problem.** At a 1280 px window the control-change record narrows when the version label is long: the transport row's minimum width includes the version badge, so a dev checkout's 'Version 0.6.18+g0e0aa1cd.dirty' holds the left column at 1028 px, the record's text at 180 px, and 'Alveolar ventilation 12.0 L/min ->' (184 px) no longer fits on one line

**Same mechanism as `PL-6XPZ`, found while closing `PL-LKX7`.** The run rows
cannot narrow below the transport row's minimum width, so the record column
absorbs any shortfall. The new fact is that the version badge is part of that
minimum, so the floor moves with the version string. Measured 2026-11-14 with
the integration tests' `_shown_view` at 1280 px: with a clean checkout the
left column takes its 0.82 share, 1014 px, and the record's text is 194 px;
with uncommitted changes the badge reads "Version 0.6.18+g0e0aa1cd.dirty",
the transport row needs 1028 px, the record shrinks to 208 px and its text to
180 px. The widest part of a record line that cannot break is "Alveolar
ventilation 12.0 L/min ->" at 184 px, so in that state its arrow is clipped.
A release build's shorter version string avoids it, but a build without
package metadata shows "Version unavailable (this build is not traceable)",
which is longer than either, and the agent's name in the same badge changes
its width too (both found by the blind review of `PL-LKX7`). The readout row
seats seven across in both measured states.

**Checked 2026-11-22.** `RunView.build_transport_row` in `app/run_view.py` still adds the version-and-model badge (`_agent_header_badge`) at the row's right end, and nothing shortens its text. So the row's minimum width still grows with the version string and the agent's name. The badge was in the transport row at the freeze too (`git show 0947408:src/anesthesia_sim/app/run_view.py`).

**Why it matters.** The control-change record is one of the values that stay on screen in every layout. At a 1280 px window its lines lose their ends whenever the badge grows wider, so a learner can lose the arrow and what follows it. A development build shows this, and so does a build without package metadata, whose version text is longer still.

**Done when.** At a 1280 px window the record's longest unbreakable line fits whatever the badge says. A test shows it with the longest text the badge can carry, "Version unavailable (this build is not traceable)".

**Generator check.** The fact misread is the transport row's minimum width, which sets how wide the record column can be. `PL-6XPZ` (the record clips below 1366 px) is the same mechanism and is still open, so this is a second instance of an open item rather than a re-entry. The two are best fixed together.
