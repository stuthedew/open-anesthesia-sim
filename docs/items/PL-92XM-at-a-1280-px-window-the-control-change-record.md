---
id: PL-92XM
title: At a 1280 px window the control-change record narrows when the version label is long: the transport row's minimum width includes the version badge, so a dev checkout's 'Version 0.6.18+g0e0aa1cd.dirty' holds the left column at 1028 px, the record's text at 180 px, and 'Alveolar ventilation 12.0 L/min ->' (184 px) no longer fits on one line
status: untriaged
added: 2026-11-14
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
A release build's shorter version string avoids it. The readout row seats
seven across in both states.
