---
id: PL-L9RD
title: Re-express app/theme.py for Qt and make the interface pass's visual decisions once, absorbing ROADMAP item 33
status: untriaged
feature: qt-port
added: 2026-09-10
---

**Problem.** Re-express app/theme.py for Qt and make the interface pass's visual decisions once, absorbing ROADMAP item 33

**`v0.5.1`'s Required scope, item 3**, and it absorbs planned-milestone item
33 - the interface pass the `v0.5.x` row used to carry. A restyle of a
dashboard about to be rewritten is the same work twice, so palette, type scale,
spacing rhythm, density and layout are decided once, here.

**What must survive the re-expression**: the six compartment colours and their
dash patterns. `theme.py` records that the four simulated colour-vision models
put pairs of them as close as 1.08, far under the 3:1 that would make colour
sufficient, so the dash pattern is the separating channel rather than
decoration. The spike copies both and says so in `chart_sources.TRACES`.

**`PL-JRS3` is the companion and is already filed**: `tools/contrast_check.py`
and `tools/agent_identity_check.py` both parse `theme.py`, and after a port they
would not fail - they would *pass*, on a tree they no longer describe. That is
the same false-green shape `PL-20PT` was fixed for.
