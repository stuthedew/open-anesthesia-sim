---
id: PL-TMSN
title: tools/glyph_check.py's six CONFIRMED entries cite evidence from the Flutter client, and one rests on a Flet layout fact, so the check passes on a Qt tree none of its evidence describes
priority: P3
effort: S
status: ready
classes: docs, infra
feature: presentation-safety
touches: tools/glyph_check.py
added: 2026-09-16
verify: uv run python tools/glyph_check.py && grep -q 'Qt build' tools/glyph_check.py
---

**Problem.** tools/glyph_check.py's six CONFIRMED entries cite evidence from the Flutter client, and one rests on a Flet layout fact, so the check passes on a Qt tree none of its evidence describes

**Split out of `PL-L9RD` on 2026-09-16**, where it was a rider added
2026-09-14 as a pre-port survey note. It is its own item because it is not
about the theme: it is about a check whose evidence no longer describes the
tree it guards.

**Why it matters.** `tools/glyph_check.py` permits exactly six non-ASCII
characters in displayed strings (U+00A0, U+00B1, U+00B7, U+00D7, U+2013,
U+2014), each carrying a `CONFIRMED` evidence string saying where it was seen
to render - "rendered in the wash-in tolerance readout (PL-8XPQ, 2026-09-04)"
and the like. Every one of those observations was made against the **Flutter
client**, which this project no longer ships. The module says it has no rot
guard, deliberately, so the check passes throughout and will go on passing: it
is a green gate whose evidence is about a toolkit that is gone. That is the
false-green shape `PL-20PT` and `PL-JRS3` were both fixed for.

**One entry is worse than stale and is the reason this is not merely tidying.**
U+00A0's evidence rests on a *Flutter layout fact* - that a blank string
collapses to zero height, so a non-breaking space is what holds a row's
height. Qt lays out an empty `QLabel` differently, so the premise may simply
not hold, and if it does not, the character is being permitted for a reason
that no longer exists.

**Done when.** The Qt dashboard has been rendered and all six characters
displayed and looked at - `PL-YCWZ`'s headless rendering path is the cheapest
route - each evidence string names the Qt build and the date it was seen, and
U+00A0's premise is re-checked against Qt specifically and either restated or
the entry removed. The phrase `Qt build` in the module is what the `verify:`
command reads.
