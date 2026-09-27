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

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it.

**Measured 2026-09-27**, offscreen (`QT_QPA_PLATFORM=offscreen`, font "Sans
Serif 9 pt", tree `aeb00392`), by building the real window as `main.py` does
and reading `ReadoutRow.width_for(7)`, the window's width less the row's, and
`initial_window_geometry` at each screen width. The seven-column row wants
1 068 px (reservations 195, 135, 149, 135, 148, 135, 135 px, spacing 6) and the
window adds 46 px around it, so seven across needs a 1 114 px window. At
`WINDOW_SCREEN_FRACTION` 0.8 a 1 366 px screen opens a 1 093 px window, the row
gets 1 047 px and misses seven by **21 px** (the nine in the title was measured
before the page padding changed; the shape is the same). The fraction that
clears seven is 0.816 at 1 366 px, 0.870 at 1 280 px, 0.774 at 1 440 px, and
1 440 px and above open on seven today. On any other font the figures move,
which is the point `PL-3355` made when it stopped recording pixels.

**Q1. Is seven across wanted on a 1 366 px screen?** **Recommendation: yes.**
`docs/MODEL.md` says what four columns costs: the six compartments split over
two lines and the comparison the row invites stops being one glance. Nothing
typographic has to pay for it, so there is no legibility trade to weigh.

**Q2. Which lever.** Two the brief did not list join its three.

- *Font size* and *panel padding*: item 33's, and refused as the brief refuses
  them.
- *Raise `WINDOW_SCREEN_FRACTION`* (the brief's recommendation). Its cost is
  that the row is font-measured precisely so that no pixel figure is
  asserted, and a fraction chosen to clear 1 068 px re-asserts one by the back
  door: 0.85 clears 1 366 px at this font with 4% to spare, leaves 1 280 px on
  four, and stops clearing anything the day v0.6.0's shipped Workspace puts
  an Area beside the row, since `PL-HJPY` makes an Area's width a fraction of
  the window.
- *Size the startup window from the content*: `max(fraction × available,
  width_for(7) + chrome)`, capped at the available width. Font-proof, but the
  same Area objection, and it reaches one View's reservation up into
  `main.py`.
- **Open the window maximized** - `QMainWindow.showMaximized()` after the
  geometry is set, so the normal geometry the reader restores to stays
  `initial_window_geometry`'s. This is the reference's own default: Blender's
  `source/blender/windowmanager/intern/wm_window.cc` defines
  `GHOST_WINDOW_STATE_DEFAULT` as `GHOST_kWindowStateMaximized` (line 132) and
  sizes the default geometry to the main screen (the `wmInitStruct` comment,
  lines 137-145, and `wm_window_ghostwindows_ensure`, lines 1217-1225), read at
  source 2026-09-27 via raw.githubusercontent.com; docs.blender.org was
  refused at CONNECT, so the Manual's page is not cited. Maximized is not full
  screen: the title bar and window controls stay, and on macOS it is the zoomed
  window, so `PL-005`'s reason - full screen "hides the window controls on some
  platforms" - does not reach it. `PL-005` is dated before 2026-09-16, so its
  kind is unrecorded and it reopens on ordinary evidence, which the 21 px and
  the coming Areas are. It is the one lever with no number in it, and it
  survives v0.6.0 because every Area gets the most room the screen has.

**Recommendation: open maximized.** Its cost is that on a large monitor the
window fills it, as Blender's does; the reader un-maximizes, and "the layout is
the reader's" is the milestone this feeds. *Alternative*, if a windowed default
is wanted kept: the fraction at 0.85, with 1 280 px recorded as opening on four
columns and why.

**For the build.** `main.py` calls `showMaximized()` in place of `show()`
after `setGeometry`; `test_the_startup_window_is_sized_from_the_screen_and_centred`
keeps its geometry cases (the restore geometry) and the launcher test in
`tests/unit/test_bootstrap.py` asserts `Qt.WindowState.WindowMaximized` in
`windowState()` - the offscreen platform may not honour the state, so assert
the flag Qt records rather than the geometry it produces. `docs/MODEL.md`'s
paragraph "In practice the row opens at whichever rung the screen affords"
is rewritten, and `PL-005`'s closing note gains one line saying what changed.
Add `src/anesthesia_sim/app/main.py`, `tests/unit/test_bootstrap.py`,
`tests/integration/test_qt_widgets.py` and `docs/MODEL.md` to `touches`.
