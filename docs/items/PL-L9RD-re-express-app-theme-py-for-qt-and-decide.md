---
id: PL-L9RD
title: Re-express app/theme.py for Qt, and decide whether the interface pass rides this port
priority: P2
effort: M
status: done
classes: feature, ux
feature: qt-port
touches: src/anesthesia_sim/app/theme.py, ROADMAP.md, tools/contrast_check.py
added: 2026-09-10
closed: 2026-09-16
verify: python3 tools/doc_check.py check && grep -qF 'that absorption was reversed on 2026-09-16' ROADMAP.md
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

## Measured 2026-09-16: the port did not redecide the visuals, so what is left here is item 33 alone

**The absorption argument's premise did not come true.** `ROADMAP.md`'s
timeline row for this port says item 33 is absorbed because "porting redecides
palette, type scale, spacing and layout regardless", so a restyle before it
would be the same work twice. Measured against the port that actually landed
(`ae8fc7bc`, `#588`, `PL-25KS` and eleven others), it did not redecide them.

That commit's whole effect on `app/theme.py` is **10 insertions and 29
deletions**, and the only constant whose value it touched is one it removed:

```text
-ELAPSED_VALUE_WIDTH = 150
```

a Flet layout width with no Qt equivalent. Not one palette entry, type size,
padding or radius changed, and `git log` over `theme.py` since 2026-09-10
shows no change to any of `BACKGROUND`, `PANEL`, `PRIMARY`, `ACCENT`, `INK`,
`MUTED`, `WARNING`, `APP_TITLE_SIZE`, `METRIC_VALUE_SIZE`, `PAGE_PADDING`,
`PANEL_PADDING` or `PANEL_RADIUS`. The port re-expressed the **widgets** and
carried the **visual language** across intact.

**So the two halves of this item have come apart, and only one of them is
still what it says.**

- *"Re-express `app/theme.py` for Qt"* is substantially done. The file is the
  token source all five Qt modules import (`qt_widgets.py`, `qt_chart.py`,
  `run_view.py`, `simulation_view.py`, `chart_frame.py`), and `make check` is
  green on it. What remains structurally is **where the Qt styling layer
  lives**: 27 `setStyleSheet` sites compose CSS strings from these constants,
  with partial helpers (`_panel_stylesheet`, `_slider_stylesheet`,
  `selector_stylesheet`, `_surface_stylesheet`, `_text_stylesheet`) in the view
  modules rather than here. `PL-Y4YX` is that question and is `blocked-by` this
  item.
- *"The visual pass decided once"* is untouched, and it is the whole of
  planned-milestone item 33 - the project owner's own "decent size overhaul
  (theme, style, overall polish)", framed as not urgent and wanted after the
  simulator works, originally placed between v0.5.0 and v0.6.0.

**Why this is worth writing down rather than simply doing.** The absorption was
a scope decision the project owner took on a stated argument, and the argument
is now measurably not what happened. Un-absorbing item 33 would be a scope
change to a scoped milestone, which is theirs; so is running the design round,
since a palette chosen by a session is the owner's decision taken for them. The
structural half is ordinary judgment and is not.

**What it is blocking, which is the reason this cannot just sit.** Three of the
five open `Required scope` ids of `v0.4.26 - the interface moves to Qt` wait on
this one: this item, `PL-NGF7` (the disabled-colour coverage gap) and `PL-W8DQ`
(the four slider tracks at 2.93:1) are `blocked-by` it, and `PL-Y4YX` is a
fourth outside the scope list. Of the other two, `PL-7SVX` goes last by its own
instruction and `PL-8PSW` is the two-branch overlay. So the port's critical
path runs entirely through a design round that has not been scheduled.

## Closed 2026-09-16: item 33 is un-absorbed, and the re-expression was already done

**The project owner accepted the recommendation** that planned-milestone item
33 comes back out of this port. The section above carries the measurement that
reversed it - the port changed no palette entry, type size, padding or radius -
so this item's two halves were settled separately.

**Half one, the visual pass, is not this item's any more.** `ROADMAP.md` is
edited in seven places: the `v0.4.26` timeline row and the milestone section
both record the absorption *and its reversal* with the measurement rather than
quietly dropping it; the `v0.5.x — the interface pass` row is restored to "The
timeline" between v0.5.0 and v0.6.0, where item 33's own placement note has
pointed all along and which the absorption had removed, leaving that note
dangling; `Required scope` item 3 is narrowed to the theme alone; and the two
paragraphs that argued *from* the absorption - the splitter reservation and
`PL-8VL1`'s layout-architecture note - are reworded to argue from the
reservation instead, which survives it. Item 33 itself gains a dated note
saying it was absorbed and returned, and why.

**The reservation is the piece that stays here deliberately.** The port builds
the layout containers once with their splitter handles inert, and item 33 turns
them live. That passes the test the palette half failed: a container genuinely
*is* built once by a port, so reserving costs nothing and rebuilding would cost
twice.

**Half two, the re-expression, was already true and is now verified rather than
assumed.** `app/theme.py` is the token source all five Qt modules import, the
six compartment colours are intact (`CIRCUIT_COLOR`, `ALVEOLAR_COLOR`,
`MIXED_VENOUS_COLOR`, `VESSEL_RICH_COLOR`, `MUSCLE_COLOR`, `FAT_COLOR`) with
their dash patterns carried on the trace specs in `app/chart_frame.py`, and
`tools/contrast_check.py` and `tools/agent_identity_check.py` both pass against
it.

**One correction inside this item's own scope.** The file's "stays free of any
toolkit" comment defended itself with a reason that is checkably false - that
the two tools "read this file with `ast` in a bare checkout precisely because
it imports nothing they would need installed". Both call `ast.parse` on the
file's *text*, which executes nothing and resolves no import, so a PySide6
import would leave both working exactly as they do. The rule is kept and the
reason replaced with one that holds: this is the one place a value a clinician
could be misled by is written down, and it is worth being importable and
testable without a display or an event loop. A rule defended by a false reason
is one the next session deletes.

**`verify:` was replaced, and the old one is why `PL-Y4YX` exists.** It read
`grep -q 'PySide6' src/anesthesia_sim/app/theme.py`, which this file's own
comment forbids and which is satisfiable by a comment containing the string.
The new command pairs `doc_check` with a grep for the sentence recording the
reversal; it exits 1 on `origin/main` and 0 here, checked both ways before
being written down.

**Three things left this item rather than being dropped**, which is the part to
read if you are looking for what happened to the riders:

- `PL-Y4YX` - where the Qt styling layer lives. 27 `setStyleSheet` sites
  compose CSS from these constants with partial helpers in the view modules.
  Deliberately still open: the owner approved un-absorbing item 33, not a
  refactor.
- `PL-TMSN` - `tools/glyph_check.py`'s six `CONFIRMED` entries cite Flutter
  evidence, and U+00A0's rests on a Flutter layout fact Qt may not share.
- `PL-Z4K6` - whether seven readout columns is wanted on a 1 366 px laptop,
  which misses the seven-column width by nine pixels.
