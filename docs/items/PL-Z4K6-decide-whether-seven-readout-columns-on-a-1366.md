---
id: PL-Z4K6
title: Decide whether seven readout columns on a 1366 px laptop is wanted, now that dashboard_frame.readout_columns is font-measured and that screen misses the seven-column width by nine pixels
priority: P3
effort: S
status: done
classes: ux
feature: presentation-safety
milestone: v0.5.15
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/main.py, src/anesthesia_sim/app/qt_widgets.py, tests/unit/test_bootstrap.py, tests/integration/test_qt_widgets.py, docs/MODEL.md, docs/ARCHITECTURE.md, docs/interface-provenance.md, docs/items/PL-005-replace-the-full-screen-startup-window-with-a.md
added: 2026-09-16
closed: 2026-09-27
pr: 1182
verify: grep -qF 'showMaximized' src/anesthesia_sim/app/main.py && grep -qF 'WindowMaximized' tests/unit/test_bootstrap.py
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

**Answered 2026-09-27.** Seven across is wanted on a 1 366 px screen, and the
window opens maximized to pay for it - `QMainWindow.showMaximized()` after the
geometry is set, which is Blender's default window state and keeps the window
controls (project owner, 2026-09-27, ratified, over raising
`WINDOW_SCREEN_FRACTION` to 0.85, which clears 1 366 px at one font and leaves
1 280 px on four columns). The measurement, the levers weighed and the build
notes are under "Design round 2026-09-27: recommendations" below; `PL-005`'s
full-screen refusal does not reach a maximized window, and its closing note
gains a line saying so. Status `ready`; `touches` widened to
`src/anesthesia_sim/app/main.py`, `tests/unit/test_bootstrap.py`,
`tests/integration/test_qt_widgets.py` and `docs/MODEL.md`.

[superseded 2026-09-27: the design round below weighed this lever against
opening the window maximized, and the owner ratified maximized; see "Answered
2026-09-27" above] Recommendation: **raise `WINDOW_SCREEN_FRACTION` just far
enough** that 1 366 px clears the seven-column width, and leave the font and
padding to item 33. That is the lever with no clinical reading attached to it.

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

## Built 2026-09-27

`main.py` calls `showMaximized()` in place of `show()` after `setGeometry`, so
the window opens maximized over `initial_window_geometry`'s centred eight
tenths, which is what a reader gets back on un-maximizing.
`SimulationView.resizeEvent` already owes the render tick a frame at the new
width, so the first frame is redrawn once the platform applies the size.

Measured under `QT_QPA_PLATFORM=offscreen` before the test was written: after
`showMaximized()` the window state carries `WindowMaximized` at once while
`geometry()` still reads the set geometry; after `processEvents()` the platform
moves the geometry to the screen (2, 2, 796, 796 on its 800 px screen) and
`normalGeometry()` keeps the set geometry throughout. So the launcher test in
`tests/unit/test_bootstrap.py` asserts the flag Qt records and that
`normalGeometry()` equals `initial_window_geometry`'s, never the geometry the
platform happens to have produced by the time the assertion runs.
`test_the_startup_window_is_sized_from_the_screen_and_centred` keeps its
geometry cases as the restore geometry.

The documentation was updated to match. `docs/MODEL.md`'s paragraph on which
rung the row opens at is rewritten around the maximized window, with the 21 px
shortfall and the 0.85 alternative recorded as the ratified decision.
`PL-005`'s closing note gains a dated line. `docs/interface-provenance.md`
§ "Adopted" records the Blender default. `docs/ARCHITECTURE.md`'s package-map
line for `main.py`, and the `WINDOW_SCREEN_FRACTION` comment and
`initial_window_geometry` docstring in `qt_widgets.py`, now describe a normal
geometry rather than where the window opens. `touches` was widened to the files
above.

**Moved from docs/MODEL.md on 2026-11-04.** From § "Displayed precision", when `PL-J37P` took the decision history out of that section:

At the window's normal size of eight tenths of the screen (`WINDOW_SCREEN_FRACTION`), on the offscreen font that the tests render with, the row on a 1366 px screen fell 21 logical pixels short of the seven-across width. A 1093 px window carried a 1047 px row, while the row's 1068 px wanted a window of about 1114 px. So that machine opened on four columns while a slightly wider one opened on seven. The conditional arrangement was then the ordinary case rather than the resized one. Maximized, the same screen offers the row about 1320 px, and a 1280 px screen offers it about 1234 px, so both open on seven. These figures are an example of the rule on one font rather than a specification of it (project owner, 2026-09-27, ratified, over raising the fraction to 0.85, which clears 1366 px at one font and leaves a 1280 px screen on four columns; `PL-Z4K6`).

Until the Qt port the window opened full screen, and the widest breakpoint was the only one a reader met without resizing.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "A decision that the Qt port or its interface pass makes once".

> **And one from the split of `PL-L9RD`**: `PL-Z4K6` (whether seven readout columns are wanted on a 1 366 px laptop, which misses the seven-column width by nine pixels). It was captured 2026-09-16. It is `P3` and `ux`, and it is debt only because it is `needs-decision`. It is deferred rather than admitted because planned-milestone item 33 is going to redecide the interface it asks about. Two of the levers are the readout font size and the panel padding, and the interface pass sets both. The third lever, `WINDOW_SCREEN_FRACTION`, is the one that `PL-Z4K6` can answer alone. Four columns is correct in the meantime, so the row degrades rather than breaking. The question's own answer says "leave two of the three levers to item 33". So holding a gate open on that question would mean holding it open on item 33.
