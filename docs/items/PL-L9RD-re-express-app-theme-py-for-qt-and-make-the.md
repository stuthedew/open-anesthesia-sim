---
id: PL-L9RD
title: Re-express app/theme.py for Qt and make the interface pass's visual decisions once, absorbing ROADMAP item 33
priority: P2
effort: M
status: ready
classes: feature, ux
feature: qt-port
touches: src/anesthesia_sim/app/theme.py, ROADMAP.md, tools/contrast_check.py
added: 2026-09-10
verify: uv run python tools/import_boundary_check.py && grep -q 'PySide6' src/anesthesia_sim/app/theme.py
---

**Problem.** Re-express app/theme.py for Qt and make the interface pass's visual decisions once, absorbing ROADMAP item 33

**The Qt port's Required scope, item 3**, and it absorbs planned-milestone item
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

**Why it matters.** A restyle of a dashboard about to be rewritten is the same
work twice, which is why planned-milestone item 33 is absorbed here rather than
left to follow the port. Palette, type scale, spacing rhythm, density and layout
are decided once, at the moment the widgets are being written anyway.

What must survive the re-expression is the pair of channels the chart depends
on: the six compartment colours and their dash patterns. `theme.py` records that
the four simulated colour-vision models put pairs of them as close as 1.08, so
the dash pattern is load-bearing rather than decorative, and a re-expression
that keeps the colours and drops the patterns is a regression a normal-vision
reviewer cannot see.

**Done when.** `app/theme.py` is expressed for Qt with the six colours and their
dash patterns intact, the interface pass's visual decisions recorded once,
`ROADMAP.md` item 33 marked absorbed, and `tools/contrast_check.py` and
`tools/agent_identity_check.py` both passing against the new file - which is
`PL-JRS3`'s subject, since after a port they would otherwise pass on a tree they
no longer describe.

**Rider, 2026-09-14 (pre-port survey).** `tools/glyph_check.py`'s six
`CONFIRMED` entries (U+00A0, U+00B1, U+00B7, U+00D7, U+2013, U+2014) record
evidence against the Flutter client - "rendered in the wash-in tolerance
readout (PL-8XPQ, 2026-09-04)" and the like - and U+00A0's rests on a Flutter
layout fact ("a blank string collapses to zero height"). The module says it
has no rot guard, deliberately. Once the Qt dashboard renders, display all
six, look at them, and rewrite each evidence string to name the Qt build and
the date; re-check U+00A0's premise specifically, since Qt lays out a blank
label differently. The check passes throughout the port either way, which is
why this is written down rather than left to be noticed.

**Rider, 2026-09-15 (from PL-25KS's close).** The readout row's reflow rule
(`docs/MODEL.md` § the readout row, `dashboard_frame.readout_columns`) is
font-measured now: seven columns want about 1 068 px on the offscreen font,
which the 0.8-fraction startup window supplies from a screen of about 1 375 px
and a 1 366 px laptop misses by nine pixels, so that laptop opens on four
columns. The font, the panel padding and `WINDOW_SCREEN_FRACTION` are this
item's levers; whether seven-across on a 1 366 screen is wanted is its
decision, and the row is correct at four either way.
