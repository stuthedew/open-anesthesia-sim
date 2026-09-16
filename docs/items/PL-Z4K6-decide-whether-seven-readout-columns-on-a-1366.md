---
id: PL-Z4K6
title: Decide whether seven readout columns on a 1366 px laptop is wanted, now that dashboard_frame.readout_columns is font-measured and that screen misses the seven-column width by nine pixels
priority: P3
effort: S
status: needs-decision
classes: ux
feature: presentation-safety
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/theme.py
added: 2026-09-16
---

**Problem.** Decide whether seven readout columns on a 1366 px laptop is wanted, now that dashboard_frame.readout_columns is font-measured and that screen misses the seven-column width by nine pixels

**Split out of `PL-L9RD` on 2026-09-16**, where it arrived as a rider from
`PL-25KS`'s close. It is a decision rather than a defect: the readout row is
correct at four columns and correct at seven, and which a 1 366 px laptop
should get is a judgment about what the interface is for.

**Why it matters.** `dashboard_frame.readout_columns` is font-measured now
rather than fixed, so the column count follows the width the window actually
gets. Seven columns want about 1 068 px on the offscreen font. The
0.8-fraction startup window supplies that from a screen of about 1 375 px and
**misses by nine pixels on a 1 366 px laptop** - one of the commonest screen
widths there is - so that machine opens on four columns while a slightly wider
one opens on seven. Nine pixels is not a meaningful difference in what a
reader can take in, and it produces a visibly different dashboard.

**Decision needed.** Whether seven-across is wanted on a 1 366 px screen, and
if so which lever pays for it. Three are available and they cost different
things: the readout **font size**, which is a legibility trade against a
clinical value; the **panel padding**, which is the spacing rhythm the
interface pass (planned-milestone item 33) will redecide anyway; and
`WINDOW_SCREEN_FRACTION`, which is how much of the screen the app claims at
startup and is the only one that costs nothing typographic.

Recommendation: **raise `WINDOW_SCREEN_FRACTION` just far enough** that 1 366
px clears the seven-column width, and leave the font and padding to item 33.
That is the lever with no clinical reading attached to it.

This is deliberately **not** blocked on item 33, because four columns is
correct meanwhile: the row degrades rather than breaking, which is why this is
`P3` and a decision rather than a defect.

**Done when.** The question above is answered and either the chosen lever is
changed with the 1 366 px case named in a test, or the item records that four
columns on that screen is the intended behaviour and why.
