---
id: PL-GWTR
title: A schematic container that stands across a pinned run heading's lower edge shows only its lower part, so its fill can look like that of a container at or over the scale's top
priority: P1
effort: M
status: done
classes: defect, safety
feature: presentation-safety
touches: ROADMAP.md, docs/ARCHITECTURE.md, docs/INTERFACE.md, docs/VERIFICATION.md, docs/items/PL-C14T-with-two-runs-in-the-maintenance-workspace-at.md, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/pinned_heading.py, src/anesthesia_sim/app/qt_schematic.py, src/anesthesia_sim/app/view_registry.py, src/anesthesia_sim/app/views.py, src/anesthesia_sim/layout/sizing.py, tests/integration/simulation_view/test_simulation_view_page.py, tests/integration/test_compartment_schematic_view.py, tests/integration/test_layout_adapter.py, tests/integration/test_pinned_heading.py, tests/unit/test_layout_sizing.py, tests/unit/test_view_registry.py, tools/contrast_check.py
added: 2026-11-27
closed: 2026-11-28
pr: 2346
payoff: a user never sees a schematic container or label line cut off, so no fill reads as full or above the scale and no cut digit reads as another
tests: tests/integration/test_compartment_schematic_view.py::test_no_container_label_line_or_share_bar_is_painted_cut_at_any_scroll_position, tests/integration/test_compartment_schematic_view.py::test_a_canvas_paints_each_part_only_while_its_clear_part_holds_it_whole, tests/integration/test_compartment_schematic_view.py::test_a_box_too_short_for_a_row_of_containers_shows_a_notice_in_place_of_the_schematic, tests/integration/test_layout_adapter.py::test_an_area_shorter_than_its_view_s_legible_height_shows_the_notice_and_is_not_held_taller, tests/integration/test_layout_adapter.py::test_an_area_no_border_can_make_legible_says_to_make_the_window_taller, tests/integration/test_layout_adapter.py::test_an_area_follows_its_view_s_legible_height_when_the_view_drops_it, tests/unit/test_view_registry.py::test_the_too_small_notice_says_to_make_the_window_taller_where_no_border_can_help, tests/integration/test_pinned_heading.py::test_a_row_s_clear_part_is_its_part_in_view_below_the_heading, tests/unit/test_layout_sizing.py::test_largest_height_gives_an_area_its_column_less_its_siblings_least_heights, tests/unit/test_layout_sizing.py::test_largest_height_refuses_an_area_the_tree_does_not_hold
---

**Problem.** A schematic container that stands across a pinned run heading's lower edge shows only its lower part, so its fill can look like that of a container at or over the scale's top

**Why it matters.** A container shows its compartment's tension as the
height of its fill, on the concentration chart's scale. A user who sees only a
container's lower part can take it for one filled to its top or above the
scale, and so read a tension the compartment does not hold. A label line cut
in the same way can show one digit as another. Both are wrong clinical values
read from a correct number, which the safety-critical standard in `CLAUDE.md`
covers.

**What a user sees** (the review of `PL-3NGZ` after it merged, 2026-11-27,
offscreen platform). `_paint_container` in `app/qt_schematic.py` outlines
each container and, for a container above the scale, draws a line in the
warning colour along its top. A container whose upper part is under a pinned
run heading shows neither. Its fill can reach the heading's lower edge, with
its side outlines and gridline marks running up to it. In the Maintenance
Workspace at 1366 by 768 with two runs, every container shows this way,
because the schematic's box is never taller than about 24 px (`PL-C14T`).

**Present before `PL-3NGZ`.** The schematic has scrolled inside its Area
since `PL-CBYS`, and the box's top edge cut a container the same way. The
pinned heading moved the cut down to the heading's lower edge.

**A cut label line can be misread too** (the review of `PL-H55Q`'s pull
request, 2026-11-27). A label line that stands across the heading's lower edge
shows only the lower part of its characters. In the schematic's font on the
offscreen test platform, the lowest 4 px above the baseline of "3" and "8"
differ in 3 pixels, so a cut tension can be taken for another.

**The tension line does not help where this happens.** A first
recommendation, on 2026-11-27, classed this `defect` because a user could read
the value from the container's tension line. The same review found that the
tension line is not on screen in this state. At 1366 by 768 with two runs,
10 to 24 px of rows show under the heading (`PL-C14T`). A container's tension
line starts 22 px below its lower edge (`_BUS_GAP` and `_LABEL_GAP` in
`app/qt_schematic.py`), so no tension line is whole there. The readouts above
the Areas stay in view at any window height and through any scrolling
(`docs/INTERFACE.md` § "Where the unconditional values sit on screen",
`PL-NNML`), and
they print each compartment's tension in % of 1 atm. In this state the first
run's readouts were on screen and the branch's were not (measured offscreen,
2026-11-27).

**No fix is available inside the scrolling page.** Raising the schematic's
least height to hold its heading, a row of containers and their tension lines
(233 px, which gives a 189 px box) grows the page. After a branch the page
then scrolls the concentration chart's plot into view and leaves the chart
View's top 102 px above the window, with the chart's title and key out of view
(measured offscreen, 2026-11-27). That would make `PL-DKQ5`'s hazard live in a
shipped Workspace. The interface pass (`PL-9WDN`) replaces the scrolling page.

**Recommendation, put to the coordinator on 2026-11-27.** Class it `safety`,
because a cut container or a cut tension can be read as a wrong value. Work it
with `PL-C14T` in the interface pass, deferred from v0.7.0. The one fix
available before then would hide the chart's key instead. The first run's
tensions stay readable above the Areas, and the state arises in one Workspace,
at one screen size, with a branch open. Holding v0.7.0 for it is the
alternative. Either way, two ways to show a cut remain, and each needs a cited
convention before it is chosen: a break line across each cut container at the
heading's lower edge, or scrolling the box a whole row of containers at a time.

**Put back, and decided on 2026-11-28** (project owner, 2026-11-28,
ratified, over shipping v0.7.0 as it was and leaving the fix to the interface
pass). Late on 2026-11-27 the thread recommended to the owner a notice in
place of cut containers before the v0.7.0 cut. The safety-critical standard in
`CLAUDE.md` prefers an obvious error state to a plausible-looking value where
correctness cannot be established, and a cut container is such a value. A
notice needs no more height, so it does not push the chart's key out of view.
The owner answered "Agree with best practice approach and technical writing".

**Done when.** A container whose top is out of view cannot be read as one
filled to its top or above the scale, and a label line cut by the heading
cannot be read as another value.

**Fix.** The canvas is told which of its rows are in view and clear of the
run's heading (`clear_of_heading` in `app/pinned_heading.py`). Each time it
paints, it works out from that which parts are whole there
(`SchematicCanvas.shown_parts` in `app/qt_schematic.py`), and paints only
those. The six containers, the lines that join them and the marks inside
them are one part, because a fill is read against its neighbours and against
the scale's marks. Each label line and each share bar is a part of its own. A
container above the scale draws a line 2 px over its outline, so the
containers count as whole only when that line is in view too. Where the
containers are hidden, the canvas paints "The containers do not fit whole in
view, so they are hidden. Scroll to see them." in the warning colour, at the
top of the part in view and above the labels, where that space holds the whole
line. `RunSchematic.pin_heading` repaints the canvas after each move of the
heading, because a scroll moves pixels already painted.

**Where no scroll position can show a row, the Area shows its notice.** The
View declares a legible height: the heading and the canvas down to the
containers' lower edge, 154 px under the container's font
(`CompartmentSchematicView.legible_height`). `AreaLayout` shows the
too-small notice wherever the Area's box is shorter than that, and does not
hold the Area taller, because a taller Area grows the page and brings back
`PL-DKQ5`'s hidden chart key. The notice used to say "Drag a border to
enlarge it" in every case. While the page scrolls, no border can give the Area
more height, so that advice was false. `largest_height` in `layout/sizing.py`
now works out the greatest height a border could give the Area, and the notice
says "Make the window taller" where that is less than the need.

**The wording and its sources.** The source is NUREG-0700 Rev. 3 (O'Hara JM,
Brookhaven National Laboratory for the U.S. Nuclear Regulatory Commission,
2020), read in full in this thread from the copy at osti.gov. No guideline in
it covers a drawing cut off by the edge of a box that scrolls: the whole text
was searched for "truncat", "partially", "clipped" and "cut off", and section
2.5.6 (scrolling and paging) was read. The line follows
the two nearest, both written for messages. Guideline 2.7.3-1 (p. 2-86) says
that "when the computer detects an entry error, an error message should state
the error and possible subsequent operations", and its additional information
asks for "as much diagnostic information and remedial direction as can be
inferred reliably from the error condition". So the line says what is hidden,
why, and what to do, and the notice names the remedy that works where the
layout shows that dragging a border cannot. Guideline 10.3.4-8 (p. 10-14), for
received messages, says that "the user should be informed when a message has
been truncated, such as when a message exceeds the available space".

**Where the schematic shows now** (measured 2026-11-28 on `b893e699` with this
change, offscreen platform, in the Maintenance Workspace with a branch open).
Under the container's font, the Area shows "It needs at least 720 by 198 px;
this Area is 720 by 110. Make the window taller, or choose a smaller View from
the menu above." at 1366 by 768. It shows the notice at 1440 by 900 (172 px),
1536 by 864 (136 px) and 1600 by 900 (172 px). It shows the schematic, scrolled
inside its Area, at 1680 by 1050 and 1920 by 1080, and whole at 2560 by 1440.
Under DejaVu Sans, which CI draws text in, the need is 750 by 194 px and the
sizes fall the same way. With one run the schematic is shown at every one of
these sizes (`test_each_shipped_workspace_shows_its_lesson_whole_with_one_run`).
Before the change, no scroll position at the four smaller sizes showed a row
of containers whole. At 1366 by 768 and 1440 by 900, dragging either border of
the schematic's Area by 300 px up or down did not make the Area taller, which
is what the notice's new advice rests on.

**Tests.** Seven tests in `tests/integration/test_compartment_schematic_view.py`
are listed in `docs/INTERFACE.md`'s note for developers on the schematic, and
three new ones in `tests/integration/test_layout_adapter.py` check the notice
for any View that declares a legible height. Five tests in
`tests/unit/test_layout_sizing.py` check `largest_height`, and one in
`tests/unit/test_view_registry.py` checks the taller-window advice. The two
`PL-CBYS` tests in `tests/integration/simulation_view/test_simulation_view_page.py`
that need the schematic shown and scrolling in its Area now run at 1920 by 1080,
because at 1366 by 768 the Area shows the notice. All pass under the container's
font and under DejaVu Sans.

Each part of the painting rule was taken out in turn on the merged tree, and
`.venv/bin/python -m pytest -q tests/integration/test_compartment_schematic_view.py -k "painted_cut or paints_each_part"`
failed each time:

1. Painting the containers whatever the clear part holds fails
   `test_no_container_label_line_or_share_bar_is_painted_cut_at_any_scroll_position`
   with `AssertionError: (0, 'Run 2, at 10m of simulated time', 'Circuit')`.
2. Painting every label line fails the same test with `assert 19 == 1`, the
   count of colours on a label line's middle row that should be blank.
3. Painting every share bar fails it with `assert 3 == 1`.
4. Leaving the off-scale line's 2 px out of the containers' extent fails both
   tests, the second at a clear part 13 px from the top.
5. Comparing only a part's top with the clear part fails both tests.

**Gate.** Added to v0.7.0's frozen list by the owner's decision above. The
`ROADMAP.md` paragraph before v0.7.0's "Required scope" records it.

**Generator check.** The fifth item on the mechanism that `PL-DKQ5`'s
Generator check names, a View cut inside a box that scrolls, after `PL-C14T`,
`PL-H55Q`, `PL-3NGZ` and `PL-DKQ5` itself. The scrolling page is that box, and
the interface pass (`PL-9WDN`) replaces it. Whether the five make a generator
is triage's call, as `PL-DKQ5` says.

**Documents checked.** `docs/INTERFACE.md` § "The compartment schematic: what
its heights, amounts and share bar assert", its note for developers, and the
sentence on which Views scroll in the section on Areas. `docs/VERIFICATION.md`'s
hazard rows for a run's value read as another's and for a container's fill,
with a new row for a cut container. `docs/ARCHITECTURE.md`'s lines for
`app/area_layout.py`, `app/qt_schematic.py`, `app/pinned_heading.py` and
`layout/sizing.py`. `ROADMAP.md`'s v0.7.0 gate. `tools/contrast_check.py`'s
requirement for the warning colour on the panel, which now names the cut
line. `docs/MODEL.md` and `README.md` do not describe the schematic's
drawing. `PL-C14T`'s brief has a dated paragraph on what its state shows now.
